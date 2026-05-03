import streamlit as st
import uuid
import datetime
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Chat History", page_icon="🤖", layout="wide")

# =========================
# 🔥 SAFE SESSION INIT (FIXED WHITE SCREEN ISSUE)
# =========================
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None


def create_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.chat_sessions[new_id] = {
        "title": f"New Chat {datetime.datetime.now().strftime('%H:%M')}",
        "messages": [],
    }
    st.session_state.current_session_id = new_id


# Ensure at least one chat exists
if len(st.session_state.chat_sessions) == 0:
    create_new_chat()

# Safety check for active session
if (
    st.session_state.current_session_id is None
    or st.session_state.current_session_id not in st.session_state.chat_sessions
):
    st.session_state.current_session_id = list(st.session_state.chat_sessions.keys())[0]


# =========================
# 🔥 BACKEND API (SAFE + SIMPLE)
# =========================
def call_backend_api(prompt, messages):
    url = "http://127.0.0.1:8000/chat"

    payload = {
        "user_query": prompt,
        "chat_history": messages
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()

        # backend must return plain text
        return response.text.strip()

    except Exception as e:
        return f"ERROR: {str(e)}"


# --- CSS (UNCHANGED) ---
st.markdown("""
<style>
    .stAppDeployButton { display: none !important; }
    footer { visibility: hidden; }
    .block-container { padding-top: 2rem; }

    [data-testid="stHorizontalBlock"] {
        gap: 0px !important;
        background-color: #1e1e1e; 
        border-radius: 8px;
        margin-bottom: 8px;
        border: 1px solid #333;
        align-items: center;
        padding-right: 5px;
    }

    [data-testid="stHorizontalBlock"] button {
        background-color: transparent !important;
        border: none !important;
        color: #e0e0e0 !important;
        box-shadow: none !important;
        width: 100% !important;
        text-align: left !important;
        height: 45px;
    }

    [data-testid="stHorizontalBlock"]:hover {
        background-color: #2b2b2b !important;
        border-color: #444;
    }
    
    [data-testid="stHorizontalBlock"]:has(button[disabled]) {
        border: 1px solid #00a67e !important;
        background-color: #262626;
    }

    [data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child(2) button {
        text-align: center !important;
    }
</style>
""", unsafe_allow_html=True)


# --- SIDEBAR ---
with st.sidebar:
    st.title("💬 Chat History")

    if st.button("➕ New Chat", use_container_width=True):
        create_new_chat()
        st.rerun()

    st.divider()

    for session_id in reversed(list(st.session_state.chat_sessions.keys())):
        session_data = st.session_state.chat_sessions[session_id]
        is_active = session_id == st.session_state.current_session_id

        col1, col2 = st.columns([0.82, 0.18])

        with col1:
            if st.button(
                f" {session_data['title']}",
                key=f"select_{session_id}",
                disabled=is_active
            ):
                st.session_state.current_session_id = session_id
                st.rerun()

        with col2:
            if st.button("🗑️", key=f"del_{session_id}"):
                del st.session_state.chat_sessions[session_id]

                if session_id == st.session_state.current_session_id:
                    if st.session_state.chat_sessions:
                        st.session_state.current_session_id = list(st.session_state.chat_sessions.keys())[0]
                    else:
                        create_new_chat()

                st.rerun()


# --- MAIN CHAT AREA ---
current_id = st.session_state.current_session_id

if current_id in st.session_state.chat_sessions:

    active_session = st.session_state.chat_sessions[current_id]

    st.title(active_session["title"])

    # Show chat history
    for message in active_session["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("Type your message..."):

        # first message = title
        if not active_session["messages"]:
            active_session["title"] = (
                prompt[:25] + ".." if len(prompt) > 25 else prompt
            )

        # save user message
        active_session["messages"].append({
            "role": "user",
            "content": prompt
        })

        # call backend
        with st.spinner("Thinking..."):
            print(active_session["messages"])
            reply = call_backend_api(prompt, active_session["messages"])

        # save assistant reply
        active_session["messages"].append({
            "role": "assistant",
            "content": reply
        })

        st.rerun()

else:
    st.warning("No active chat session found. Please create a new chat.")