# app.py
import os
import streamlit as st
from memory import MemoryStore
from agent_langchain import ChatAgent
from dotenv import load_dotenv

load_dotenv()  # load .env if present

st.set_page_config(page_title="Chatbot with Memory (LangChain)", layout="wide")
st.title("Chatbot With User Memory — (OpenAI / Groq + LangChain + Streamlit)")

# --- Configuration
OPENAI_API_KEY = (
    st.secrets.get("OPENAI_API_KEY") if hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")
)
GROQ_API_KEY = (
    st.secrets.get("GROQ_API_KEY") if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets else os.getenv("GROQ_API_KEY")
)
if not OPENAI_API_KEY and not GROQ_API_KEY:
    st.warning("No OPENAI_API_KEY or GROQ_API_KEY found. Set one in Streamlit secrets or .env.")
st.sidebar.header("Session & Settings")

session_id = st.sidebar.text_input("Session ID", value="demo_user")
model_choice = st.sidebar.selectbox("Model / Provider",
                                    options=["openai/gpt-4o-mini", "openai/gpt-4o", "openai/gpt-3.5-turbo", "groq/groq-model (placeholder)"])
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.2)
memory_window = st.sidebar.slider("Memory window (most recent items)", 1, 30, 5)

if "history" not in st.session_state:
    st.session_state.history = []

# initialize memory
mem = MemoryStore("memory.json")

# initialize agent (constructed lazily so UI loads faster)
agent = ChatAgent(openai_api_key=OPENAI_API_KEY, groq_api_key=GROQ_API_KEY)

st.subheader("Memory (recent items)")
items = mem.get_session_memory(session_id)
if items:
    for i, it in enumerate(items[-memory_window:], start=1):
        st.write(f"{i}. {it}")
else:
    st.info("No memory yet for this session.")

st.subheader("Chat")
col1, col2 = st.columns([3,1])
with col1:
    user_input = st.text_input("You:", key="user_input")
    send = st.button("Send")
with col2:
    if st.button("Clear memory for this session"):
        mem.clear_session(session_id)
        st.success(f"Cleared memory for {session_id}")

# handle send
if send and user_input.strip():
    # store user message
    mem.append_session_memory(session_id, f"User: {user_input}")
    # prepare memory context
    context = "\n".join(mem.get_session_memory(session_id)[-memory_window:])
    # ask the agent for reply
    try:
        reply = agent.run(
            user_input=user_input,
            memory_context=context,
            model_choice=model_choice,
            temperature=temperature,
            memory_window=memory_window,
        )
    except Exception as e:
        reply = f"(Error running agent: {e})"

    # append assistant message to memory and history
    mem.append_session_memory(session_id, f"Assistant: {reply}")
    st.session_state.history.append(("You", user_input))
    st.session_state.history.append(("Assistant", reply))

# display chat from newest to oldest
for who, text in st.session_state.history[::-1]:
    if who == "You":
        st.markdown(f"**You:** {text}")
    else:
        st.markdown(f"**Assistant:** {text}")
