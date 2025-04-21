import os
import google.generativeai as genai
from dotenv import load_dotenv
from agents.mental_agent import query_mental_agent
from agents.physical_agent import query_physical_agent

load_dotenv()
genai.configure(api_key=os.getenv("API_KEY"))
model = genai.GenerativeModel(os.getenv("MODEL_NAME"))

CLASSIFICATION_PROMPT = """You are an intelligent AI assistant combining insights from mental and physical health domains in under 100 words. You are really good at summarizing multiple expert opinions and making it sound like its coming from you to help the user feel comforatable and trustable when listening to you response.

You must summarize the key findings from each assistant’s response and, if needed, ask up to **three** follow-up questions to deepen understanding or refine the solution.

Finish with a comprehensive, supportive conclusion that brings mental and physical aspects together into holistic suggestions if the user feels comfortable to receive them.

---

User's Question:
{user_input}

Mental Health Response:
{mental_response}

Physical Health Response:
{physical_response}

Instructions:
1. Combine the mental and physical health insights into one cohesive summary.
2. Ask **no more than one** follow-up questions to fill gaps in understanding.
3. Provide a thoughtful, complete conclusion or recommendation to guide the user.
4. Maintain a kind, respectful, and clear tone.
6. Ensure all the content required is retained but your repsonse shouldnt exceed **100 words**.
7. Dont give recommendations in every response since the key is to make it feel like a conversation.
"""

AGGREGATOR_PROMPT = """You are an intelligent AI assistant combining insights from mental and physical health domains in under 100 words. You are really good at summarizing multiple expert opinions and making it sound like its coming from you to help the user feel comforatable and trustable when listening to you response.

You must summarize the key findings from each assistant’s response and, if needed, ask up to **three** follow-up questions to deepen understanding or refine the solution.

Finish with a comprehensive, supportive conclusion that brings mental and physical aspects together into holistic suggestions if the user feels comfortable to receive them.

---

User's Query:
{user_input}

Mental Health Response:
{mental_response}

Physical Health Response:
{physical_response}

Instructions:
1. Combine the mental and physical health insights into one cohesive summary.
2. Ask **no more than one** follow-up questions to fill gaps in understanding.
3. Provide a thoughtful, complete conclusion or recommendation to guide the user.
4. Maintain a kind, respectful, and clear tone.
6. Ensure all the content required is retained but your repsonse shouldnt exceed **100 words**.
7. Dont give recommendations in every response since the key is to make it feel like a conversation.
"""





def classify_query(user_input: str) -> str:
    # messages = [
    #     {"role": "user", "parts": CLASSIFICATION_PROMPT},
    #     {"role": "user", "parts": f"User query: {user_input}"}
    # ]
    # try:
    #     response = model.generate_content(messages)
    #     # label = response.candidates[0].content.parts[0].text.strip().lower()
    #     return "both"
    #     # return label if label in ["mental", "physical", "both"] else "both"
    # except:
    #     return "both"
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
