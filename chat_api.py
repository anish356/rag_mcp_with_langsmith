from fastapi import FastAPI
from fastapi.responses import PlainTextResponse  # ✅ added
from pydantic import BaseModel
from contextlib import asynccontextmanager
from workflow import run_workflow, load_context
import logging
import asyncio
import os
from fastapi.responses import FileResponse, PlainTextResponse

# This hides the 'ConnectionResetError' traceback in the console
logging.getLogger("asyncio").setLevel(logging.CRITICAL)

app = FastAPI()


# =========================
# REQUEST MODEL
# =========================
class ChatRequest(BaseModel):
    user_query: str
    chat_history: list[dict] = []


# =========================
# STARTUP (LOAD MCP CONTEXT ONCE)
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🔥 Startup
    print("🚀 Loading MCP context...")
    await load_context()
    print("✅ MCP context loaded")

    yield

    # 🔥 Shutdown (optional cleanup)
    print("👋 Shutting down...")


# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def home():
    return {
        "status": "running",
        "message": "FastAPI + LangGraph + MCP + Groq 🚀"
    }


# =========================
# 🚀 CHAT ENDPOINT (PLAIN TEXT RESPONSE)
# =========================
@app.post("/chat", response_class=PlainTextResponse)  # ✅ added here
async def chat(req: ChatRequest):

    result = await run_workflow(req.user_query,req.chat_history)

    return result.get("final_output")

from fastapi.responses import FileResponse, PlainTextResponse
import os

@app.get("/graph")
async def get_graph():
    file_path = "graph.png"

    if not os.path.exists(file_path):
        return PlainTextResponse(
            content="No graph found",
            status_code=404
        )

    return FileResponse(
        path=file_path,
        media_type="image/png"
    )
# http://127.0.0.1:8000/graph