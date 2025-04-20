import os
import google.generativeai as genai
from dotenv import load_dotenv
from utils.context_loader import load_context_from_folder
from utils.web_search import simple_web_search

load_dotenv()
genai.configure(api_key=os.getenv("API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

MENTAL_DOCS_FOLDER = "./mental_docs"

MENTAL_PROMPT = (
    "You are a calm, empathetic mental health assistant. "
    "Offer emotional support, self-care suggestions, and compassionate advice. "
    "Use kind language. Keep replies under 100 words."
)

def query_mental_agent(user_input: str, history: list[str] = None) -> str:
    context = load_context_from_folder(MENTAL_DOCS_FOLDER)
    memory = "\n".join(history) if history else ""
    web_context = simple_web_search(user_input)

    prompt = (
        f"{MENTAL_PROMPT}\n\n"
        f"Conversation History:\n{memory}\n\n"
        f"User: {user_input}\n\n"
        f"Context from Documents:\n{context}\n\n"
        f"Live Web Search Results:\n{web_context}"
    )
    print("🔍 Web context used:\n", web_context)


    messages = [{"role": "user", "parts": prompt}]
    try:
        response = model.generate_content(messages)
        return response.candidates[0].content.parts[0].text
    except Exception as e:
        return f"❌ Mental Agent Error: {e}"

