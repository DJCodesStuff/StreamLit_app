import os
import uuid
import google.generativeai as genai
from dotenv import load_dotenv
from utils.web_search import simple_web_search

load_dotenv()
genai.configure(api_key=os.getenv("API_KEY"))
model = genai.GenerativeModel(os.getenv("MODEL_NAME"))

PHYSICAL_PROMPT = """You are a professional and caring AI assistant focused on physical health.

Start by answering the user's health-related question using the given context. If needed, ask **up to three follow-up questions** to better assess symptoms or habits. Your goal is to help the user understand potential causes or provide basic guidance.

Finish with a conclusive recommendation or insight, even if limited due to incomplete information.

---

User's Question:
{user_input}

Relevant Information:
{context}

Instructions:
1. Give a clear, factual answer based on the user's question.
2. Ask no more than **three** concise follow-up questions to gather more relevant details (e.g., duration, habits, history).
3. Conclude your response with a summary or recommendation that reflects your current understanding.
4. Be professional, calm, and respectful, and encourage the user to seek medical advice if needed.
5. Focus more on the context provided under Relevant Information as it takes precedence if there is relevant information to the user's query.
"""

from utils.rag_session_context import retrieve_context_from_store
from utils.web_search import simple_web_search

def query_physical_agent(user_input: str, session_id: str, history: list[str] = None) -> str:
    context = retrieve_context_from_store(user_input, category="physical", k=5)
    memory = "\n".join(history) if history else ""
    web_context = simple_web_search(user_input)

    prompt = (
        f"{PHYSICAL_PROMPT}\n\n"
        f"Conversation History:\n{memory}\n\n"
        f"User: {user_input}\n\n"
        f"Context from Documents:\n{context}\n\n"
        f"Live Web Search Results:\n{web_context}"
    )

    messages = [{"role": "user", "parts": prompt}]
    try:
        response = model.generate_content(messages)
        return response.candidates[0].content.parts[0].text
    except Exception as e:
        return f"❌ Physical Agent Error: {e}"

