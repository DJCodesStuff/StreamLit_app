import streamlit as st
import requests
import json

# -----------------------------
# Config
# -----------------------------
st.set_page_config(page_title="Ollama Chatbot", page_icon="🤖")
st.title("🤖 Chat with Ollama")

# -----------------------------
# Sidebar Settings
# -----------------------------
def sidebar_settings():
    st.sidebar.title("⚙️ Settings")
    model = st.sidebar.text_input("Model name", value="llama3", help="Enter the name of the model you started with `ollama run`.")
    return model

# -----------------------------
# Initialize Session State
# -----------------------------
def init_session():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

# -----------------------------
# Display Chat
# -----------------------------
def display_chat():
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# -----------------------------
# Send Message to Ollama API
# -----------------------------
def query_ollama(model: str, messages: list) -> str:
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={"model": model, "messages": messages},
            stream=True,
        )
        response.raise_for_status()

        reply = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode("utf-8"))
                    reply += data.get("message", {}).get("content", "")
                except json.JSONDecodeError:
                    continue
        return reply.strip()
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# -----------------------------
# Main App Logic
# -----------------------------
def main():
    model_name = sidebar_settings()
    init_session()
    display_chat()

    user_input = st.chat_input("Type your message...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Call Ollama and display response
        response = query_ollama(model_name, st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "assistant", "content": response})

        with st.chat_message("assistant"):
            st.markdown(response)

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    main()


# ------------------------
# Install : 'pip install streamlit requests' and download ollama from https://ollama.com/
# Run : ollama pull llama3
# Run : ollama run llama3
# Run : streamlit run trial.py
# It will open a new tab in your browser.
# -----------------------------