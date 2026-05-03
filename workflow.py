import json
import os
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from fastmcp import Client
from groq_llm import call_groq
from langsmith import traceable
from dotenv import load_dotenv
load_dotenv()  

# =========================
# MCP CLIENT
# =========================
client = Client("http://127.0.0.1:8001/mcp")

PROMPTS, TOOLS = [], []


# =========================
# UTILITIES
# =========================
async def load_context(connected_client):
    global PROMPTS, TOOLS
    TOOLS = await connected_client.list_tools()
    PROMPTS = await connected_client.list_prompts()


def get_mcp_prompt(name: str):
    alt_name = name.replace("_", "-")
    for p in PROMPTS:
        if p.name in (name, alt_name):
            return p.name
    raise ValueError(f"Prompt '{name}' not found.")


# =========================
# STATE
# =========================
class GraphState(TypedDict):
    user_input: str
    tool_json: dict
    tool_result: str
    error: Optional[str]
    final_output: str
    retry_count: int
    chat_history: list
    client: Client


# =========================
# NODE 1: TOOL SELECTOR
# =========================
@traceable(name="tool_selector", run_type="chain")
async def tool_selector_node(state: GraphState):
    try:
        tools_str = "\n".join([f"{t.name}: {t.description}" for t in TOOLS])

        p_name = get_mcp_prompt("llm_prompt")

        prompt_data = await state["client"].get_prompt(
            p_name,
            {
                "tools": tools_str,
                "user_query": state["user_input"],
                "chat_history": json.dumps(state["chat_history"])
            }
        )

        content = prompt_data.messages[0].content.text

        decision = call_groq(prompt=content)

        try:
            tool_json = json.loads(decision)
        except:
            tool_json = {"tool": "none", "args": {}}

        return {
            **state,
            "tool_json": tool_json,
            "error": None
        }

    except Exception as e:
        return {
            **state,
            "error": str(e),
            "tool_json": {"tool": "none", "args": {}}
        }


# =========================
# NODE 2: TOOL EXECUTOR
# =========================
@traceable(name="tool_executor", run_type="tool")
async def tool_executor_node(state: GraphState):
    try:
        tool = state["tool_json"].get("tool")
        args = state["tool_json"].get("args", {})

        if not tool or tool == "none":
            return {**state, "tool_result": "No tool needed."}

        result = await state["client"].call_tool(tool, args)

        return {
            **state,
            "tool_result": json.dumps(result, default=str)
        }

    except Exception as e:
        return {
            **state,
            "tool_result": f"Tool error: {e}"
        }


# =========================
# NODE 3: RESPONSE GENERATOR
# =========================
@traceable(name="response_generator", run_type="chain")
async def response_node(state: GraphState):
    try:
        p_name = get_mcp_prompt("beautiful_output_prompt")

        prompt_data = await state["client"].get_prompt(
            p_name,
            {
                "user_input": state["user_input"],
                "tool_result": state["tool_result"],
                "chat_history": json.dumps(state["chat_history"])
            }
        )

        content = prompt_data.messages[0].content.text

        final = call_groq(prompt=content)

        return {
            **state,
            "final_output": final
        }

    except Exception as e:
        return {
            **state,
            "final_output": f"Formatting Error: {e}"
        }


# =========================
# GRAPH BUILDER
# =========================
def build_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("selector", tool_selector_node)
    workflow.add_node("executor", tool_executor_node)
    workflow.add_node("response", response_node)

    workflow.set_entry_point("selector")
    workflow.add_edge("selector", "executor")
    workflow.add_edge("executor", "response")
    workflow.add_edge("response", END)

    return workflow.compile()


# =========================
# RUNNER
# =========================
@traceable(name="langgraph_workflow")
async def run_workflow(user_query: str, chat_history=None):

    async with client:
        await load_context(client)

        app = build_workflow()

        # ✅ Generate graph only once
        if not os.path.exists("graph.png"):
            png_bytes = app.get_graph().draw_mermaid_png()
            with open("graph.png", "wb") as f:
                f.write(png_bytes)

        initial_state = {
            "user_input": user_query,
            "chat_history": chat_history or [],
            "tool_json": {},
            "tool_result": "",
            "error": None,
            "final_output": "",
            "retry_count": 0,
            "client": client
        }

        result = await app.ainvoke(initial_state)

        return result