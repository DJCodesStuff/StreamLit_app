import os
import uuid
import google.generativeai as genai
from dotenv import load_dotenv
from utils.web_search import simple_web_search

load_dotenv()
genai.configure(api_key=os.getenv("API_KEY"))
model = genai.GenerativeModel(os.getenv("MODEL_NAME"))

MENTAL_PROMPT = """You are a compassionate and insightful AI assistant focused on mental health.

Your goal is to help the user understand and address their emotional or psychological concerns. Begin by answering the user's question thoughtfully. If more clarity is needed, you may ask follow-up questions — but limit yourself to no more than **three**.

You must also provide a helpful and empathetic summary or conclusion at the end of your response, based on what you’ve learned so far.

---

User's Question:
{user_input}

Relevant Information:
{context}

Instructions:
1. Provide a direct, empathetic answer based on the user's input and available context.
2. Ask up to **one** thoughtful follow-up questions only if needed to better understand the user's possible diagnosis.
3. End with a clear and supportive conclusion, summarizing insights or suggesting actionable next steps.
4. Use a calm, non-judgmental tone throughout.
5. Focus more on the context provided under Relevant Information as it takes precedence if there is relevant information to the user's query.
"""

from utils.rag_session_context import retrieve_context_from_store
from utils.web_search import simple_web_search

def query_mental_agent(user_input: str, session_id: str, history: list[str] = None) -> str:
    context = retrieve_context_from_store(user_input, category="mental", k=5)
    memory = "\n".join(history) if history else ""
    web_context = simple_web_search(user_input)

    prompt = (
        f"{MENTAL_PROMPT}\n\n"
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
        return f"❌ Mental Agent Error: {e}"

