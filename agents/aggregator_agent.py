import os
import google.generativeai as genai
from dotenv import load_dotenv
from agents.mental_agent import query_mental_agent
from agents.physical_agent import query_physical_agent

load_dotenv()
genai.configure(api_key=os.getenv("API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

CLASSIFICATION_PROMPT = (
    "You are a classifier that decides whether a health-related query is about mental health, physical health, or both. "
    "Only return one word: 'mental', 'physical', or 'both'."
)

AGGREGATOR_PROMPT = (
    "You are a women's health assistant combining insights from both mental and physical health experts. "
    "Summarize the input clearly and empathetically, avoid duplication, and focus on clarity."
)

def classify_query(user_input: str) -> str:
    messages = [
        {"role": "user", "parts": CLASSIFICATION_PROMPT},
        {"role": "user", "parts": f"User query: {user_input}"}
    ]
    try:
        response = model.generate_content(messages)
        label = response.candidates[0].content.parts[0].text.strip().lower()
        return label if label in ["mental", "physical", "both"] else "both"
    except:
        return "both"

def aggregate_health_response(user_input: str, history: list[str]) -> str:
    classification = classify_query(user_input)
    mental_response = ""
    physical_response = ""

    if classification in ["mental", "both"]:
        mental_response = query_mental_agent(user_input, history)

    if classification in ["physical", "both"]:
        physical_response = query_physical_agent(user_input, history)

    combined = (
        f"User: {user_input}\n\n"
        f"Mental:\n{mental_response}\n\n"
        f"Physical:\n{physical_response}"
    )

    summary_prompt = f"{AGGREGATOR_PROMPT}\n\n{combined}"
    messages = [{"role": "user", "parts": summary_prompt}]

    try:
        response = model.generate_content(messages)
        return response.candidates[0].content.parts[0].text
    except Exception as e:
        return (
            f"⚠️ Aggregator error. Using raw responses.\n\n"
            f"Mental:\n{mental_response}\n\n"
            f"Physical:\n{physical_response}\n\n"
            f"Error: {e}"
        )
