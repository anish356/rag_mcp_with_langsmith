# 🚀 RAG Project (FastAPI + Streamlit + MCP + LangSmith)

## 📌 Overview

This project is a **Retrieval-Augmented Generation (RAG)** system that allows users to query data using an LLM-powered backend.

It combines:

* ⚡ FastAPI (backend APIs)
* 🎨 Streamlit (UI)
* 🧠 LLM (Groq)
* 🔗 MCP (Model Context Protocol workflow)
* 📊 LangSmith (LLM tracing & debugging)

---

## ✨ Features

* 🔍 Semantic query handling
* 🧠 LLM-based response generation
* 🔄 Workflow-based execution (graph-based)
* 💬 Chat history support
* ⚡ FastAPI backend for APIs
* 🎨 Interactive Streamlit UI
* 📊 End-to-end LLM tracing with LangSmith

---

## 🧱 Project Structure

```
RAG_Project_v1/
│
├── chat_api.py          # FastAPI endpoints
├── workflow.py          # Core RAG workflow logic
├── groq_llm.py          # LLM integration (Groq)
├── mcp1.py              # MCP server logic
├── UI5.py               # Streamlit UI
├── chat_history.json    # Stores chat history
├── todo.db              # Local database
├── graph.png            # Workflow graph visualization
├── requirements.txt     # Dependencies
├── .env                 # Environment variables
└── test.py              # Testing file
```

---

## ⚙️ Installation

```bash
# Clone repo
git clone <your-repo-link>
cd RAG_Project_v1

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in root:

```
GROQ_API_KEY=your_api_key_here

# LangSmith Config
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=rag-project
```

---

## ▶️ Running the Project

### 1️⃣ Start FastAPI Server

```bash
uvicorn chat_api:app --reload
```

API will run on:
👉 http://127.0.0.1:8000
👉 Docs: http://127.0.0.1:8000/docs

---

### 2️⃣ Start Streamlit UI

```bash
streamlit run UI5.py
```

UI will open at:
👉 http://localhost:8501

---

### 3️⃣ (Optional) Run MCP Server

```bash
python mcp1.py
```

---

## 🧠 Workflow

The system follows a **graph-based workflow**:

1. User query input
2. Context retrieval
3. LLM processing (Groq)
4. Response generation
5. Chat history storage

📊 Workflow visualization: `graph.png`

---

## 📊 LangSmith Integration

This project uses LangSmith for **LLM observability and debugging**.

### 🔍 What you can track:

* User queries
* Retrieved context
* Prompt sent to LLM
* Final LLM response
* Execution flow of workflow

---

### ⚙️ Basic Usage

Add tracing to your workflow:

```python
from langsmith import traceable

@traceable
def run_workflow(query):
    ...
```

---

### 📈 Benefits

* Debug wrong answers easily
* Understand retrieval issues
* Improve prompt quality
* Track performance of RAG pipeline

---

## 🧪 Testing

```bash
python test.py
```

## 👤 Author

**Anish Yadav**

---

## ⭐ Notes

* Make sure virtual environment is activated before running
* Use `python` (not `python3`) inside Windows venv
* Ensure `.env` file is properly configured
* Enable LangSmith tracing for debugging

---
