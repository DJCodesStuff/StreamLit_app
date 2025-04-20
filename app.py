import streamlit as st
from agents.aggregator_agent import aggregate_health_response

st.set_page_config(page_title="Dual Health Assistant", page_icon="🧠💪")
st.title("🧠💪 Unified Health Assistant with RAG")

# Initialize session history
if "history" not in st.session_state:
    st.session_state.history = []

# Input box for user query
user_input = st.chat_input("Ask me anything about your health...")

if user_input:
    # Store user message
    st.session_state.history.append({"role": "user", "message": user_input})
    
    # Call aggregator agent
    chat_history = [msg["message"] for msg in st.session_state.history if msg["role"] == "user"]
    final_response = aggregate_health_response(user_input, history=chat_history)
    
    # Store assistant's response
    st.session_state.history.append({"role": "assistant", "message": final_response})

# Display full chat history
for msg in st.session_state.history:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["message"])
    else:
        st.chat_message("assistant").write(msg["message"])
