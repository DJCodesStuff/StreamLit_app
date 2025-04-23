import streamlit as st
from agents.aggregator_agent import aggregate_health_response
import threading
from utils.rag_session_context import start_monitoring
import time

# Start background monitoring for document changes
threading.Thread(target=start_monitoring, daemon=True).start()

# Page setup
st.set_page_config(
    page_title="Unified Health Assistant",
    page_icon="🧠💪",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for theme
st.markdown("""
    <style>
        html, body {
            font-family: 'Segoe UI', sans-serif;
        }

        .stChatInputContainer {
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
        }

        .stChatMessage:nth-child(odd) {
            background-color: rgba(255, 182, 193, 0.2); /* user */
            color: var(--text-color);
            border-radius: 12px;
            padding: 10px;
            margin-bottom: 8px;
        }

        .stChatMessage:nth-child(even) {
            background-color: rgba(135, 206, 250, 0.15); /* assistant */
            color: var(--text-color);
            border-radius: 12px;
            padding: 10px;
            margin-bottom: 8px;
        }

        body {
            background-color: var(--background-color);
            color: var(--text-color);
        }
    </style>
""", unsafe_allow_html=True)

# App title
st.title("💖 Rosa: Your Unified Health Assistant")
st.caption("Feel free to ask anything about your body, mood, or mind — we're here for you 💬")

# Initialize state
if "history" not in st.session_state:
    st.session_state.history = []

if "chat_phase" not in st.session_state:
    st.session_state.chat_phase = "idle"  # idle | show_animation | generate_response

# Handle user input
user_input = st.chat_input("Ask me anything about your health...")

if user_input and st.session_state.chat_phase == "idle":
    st.session_state.history.append({"role": "user", "message": user_input})
    st.session_state.history.append({"role": "assistant", "message": "💬 Typing..."})
    st.session_state.chat_phase = "show_animation"
    st.rerun()

# Display history (skip typing if animating)
for i, msg in enumerate(st.session_state.history):
    if msg["message"].startswith("💬 Typing") and i == len(st.session_state.history) - 1 and st.session_state.chat_phase in ["show_animation", "generate_response"]:
        continue
    if msg["role"] == "user":
        st.chat_message("user").write(msg["message"])
    else:
        st.chat_message("👩").write(msg["message"])

# Show animated typing dots
if st.session_state.chat_phase == "show_animation":
    with st.chat_message("👩"):
        placeholder = st.empty()
        for i in range(6):
            dots = "." * ((i % 3) + 1)
            placeholder.markdown(f"💬 Typing{dots}")
            time.sleep(0.4)
    st.session_state.chat_phase = "generate_response"
    st.rerun()

# Generate and display response
if st.session_state.chat_phase == "generate_response":
    user_messages = [msg["message"] for msg in st.session_state.history if msg["role"] == "user"]
    last_user_input = user_messages[-1]
    final_response = aggregate_health_response(last_user_input, history=user_messages)
    st.session_state.history[-1]["message"] = final_response
    st.session_state.chat_phase = "idle"
    st.rerun()

# Sidebar
st.sidebar.markdown("### 💬 About this app")
st.sidebar.info("This assistant provides both medical and emotional health support using AI agents. \nAll your conversations remain private.")
st.sidebar.success("📡 Vector store monitoring active")
