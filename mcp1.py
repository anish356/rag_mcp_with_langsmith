from fastmcp import FastMCP
import sqlite3
from ddgs import DDGS

mcp = FastMCP("todo-sql-search-mcp")

DB_PATH = "todo.db"


# =========================
# 🧱 INIT DATABASE
# =========================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'pending',
        priority TEXT DEFAULT 'medium',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        due_date TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# =========================
# 🔎 DUCKDUCKGO SEARCH TOOL
# =========================
@mcp.tool()
def web_search(query: str, max_results: int = 5):
    """Search the internet using DuckDuckGo and return relevant results."""
    results = []

    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append({
                "title": r["title"],
                "url": r["href"],
                "snippet": r["body"]
            })

    return results


# =========================
# ➕ CREATE TODO
# =========================
@mcp.tool()
def add_todo(title: str, description: str = "", priority: str = "medium", due_date: str = None):
    """Create a new todo item with title, description, priority and due date."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO todos (title, description, priority, due_date)
        VALUES (?, ?, ?, ?)
    """, (title, description, priority, due_date))

    conn.commit()
    conn.close()

    return {"status": "todo added", "title": title}


# =========================
# 📄 GET ALL TODOS
# =========================
@mcp.tool()
def get_todos():
    """Retrieve all todo items from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM todos")
    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "id": r[0],
            "title": r[1],
            "description": r[2],
            "status": r[3],
            "priority": r[4],
            "created_at": r[5],
            "due_date": r[6]
        }
        for r in rows
    ]


# =========================
# 🔍 GET SINGLE TODO
# =========================
@mcp.tool()
def get_todo(todo_id: int):
    """Retrieve a specific todo item by its ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    r = cursor.fetchone()

    conn.close()

    if not r:
        return {"error": "todo not found"}

    return {
        "id": r[0],
        "title": r[1],
        "description": r[2],
        "status": r[3],
        "priority": r[4],
        "created_at": r[5],
        "due_date": r[6]
    }


# =========================
# ✔️ MARK COMPLETE
# =========================
@mcp.tool()
def complete_todo(todo_id: int):
    """Mark a todo item as completed using its ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE todos
        SET status = 'completed'
        WHERE id = ?
    """, (todo_id,))

    conn.commit()
    conn.close()

    return {"status": "completed", "id": todo_id}


# =========================
# ✏️ UPDATE TODO
# =========================
@mcp.tool()
def update_todo(todo_id: int, title: str = None, description: str = None, priority: str = None):
    """Update a todo item's title, description, or priority."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if title:
        cursor.execute("UPDATE todos SET title = ? WHERE id = ?", (title, todo_id))

    if description:
        cursor.execute("UPDATE todos SET description = ? WHERE id = ?", (description, todo_id))

    if priority:
        cursor.execute("UPDATE todos SET priority = ? WHERE id = ?", (priority, todo_id))

    conn.commit()
    conn.close()

    return {"status": "updated", "id": todo_id}


# =========================
# ❌ DELETE TODO
# =========================
@mcp.tool()
def delete_todo(todo_id: int):
    """Delete a todo item permanently using its ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))

    conn.commit()
    conn.close()

    return {"status": "deleted", "id": todo_id}


# =========================
# 🔎 FILTER TODOS
# =========================
@mcp.tool()
def filter_todos(status: str = None, priority: str = None):
    """Filter todo items by status or priority."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = "SELECT * FROM todos WHERE 1=1"
    params = []

    if status:
        query += " AND status = ?"
        params.append(status)

    if priority:
        query += " AND priority = ?"
        params.append(priority)

    cursor.execute(query, params)
    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "id": r[0],
            "title": r[1],
            "description": r[2],
            "status": r[3],
            "priority": r[4],
            "created_at": r[5],
            "due_date": r[6]
        }
        for r in rows
    ]


# =========================
# 💬 CHAT TOOL
# =========================
@mcp.tool()
def chat(user_query: str) -> str:
    """General assistant for chat or when no other tool applies."""
    return f"Assistant: {user_query}"




# =========================
# PROMPTS (Used by the Graph)
# =========================
@mcp.prompt()
def llm_prompt(tools, context="", user_query=""):

    sys_prompt = f"""
    You are a TOOL ROUTING AGENT.

    Your job is to ALWAYS select the BEST matching tool.

    AVAILABLE TOOLS:
    {tools}

    INTERNAL CONTEXT:
    {context}

    USER QUERY:
    {user_query}


    EXAMPLES:

    User: add a task to buy milk
    {{ "tool": "add_todo", "args": {{ "title": "buy milk" }} }}

    User: show all todos
    {{ "tool": "get_todos", "args": {{}} }}

    User: complete todo 2
    {{ "tool": "complete_todo", "args": {{ "todo_id": 2 }} }}

    User: delete todo 3
    {{ "tool": "delete_todo", "args": {{ "todo_id": 3 }} }}

    User: search latest AI news
    {{ "tool": "web_search", "args": {{ "query": "latest AI news" }} }}

    User: hello
    {{ "tool": "chat", "args": {{ "user_query": "hello" }} }}

    RULES:
    - Return ONLY valid JSON
    - No markdown
    - No explanation
    - ALWAYS choose the closest matching tool
    - DO NOT return "none" unless absolutely impossible
    - If unsure, use "chat"

    OUTPUT FORMAT:
    {{
        "tool": "tool_name",
        "args": {{ ... }}
    }}
    """
    return sys_prompt

@mcp.prompt()
def beautiful_output_prompt(user_input: str, tool_result: str,chat_history=None):
    return f"""You are a highly skilled AI assistant.

        Respond in a clean, structured, and beautiful format.If user quer related to history response accordingly

        Rules:
        - Use headings
        - Use bullet points
        - Keep response concise
        - Highlight key points in bold
        - If greeting → respond casually
        - If no data → just reply normally
        - Avoid unnecessary summary format

        .\nUser: {user_input}\nData: {tool_result}\nCHAT HISTORY:{chat_history}"""


@mcp.prompt()
def retry_prompt(error: str, tools_formatted: str):
    return f"System: The last call failed with: {error}. Fix the JSON using these tools:\n{tools_formatted}"


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8001)