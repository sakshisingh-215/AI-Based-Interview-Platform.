import os
import requests
import json

# backend/ai_logic.py

GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # free tier key from https://console.groq.com

def evaluate_answer_with_groq(role: str, question: str, answer: str) -> dict:
    PROMPT_TEMPLATE = """
You are a professional technical interviewer.
You are interviewing for the role: {role}.

Question:
"{question}"

Answer:
"{answer}"

1. Give a short evaluation.
2. Return a JSON in this exact format (no additional text):

{{
  "score": <number>,
  "strengths": "<short text>",
  "weaknesses": "<short text>",
  "advice": "<short text>"
}}
    """.strip()

    prompt = PROMPT_TEMPLATE.format(role=role, question=question, answer=answer)

    res = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama3-8b-8192",  # or mistral, etc.
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        },
    )

    if not res.ok:
        print(res.text)
        raise Exception("Groq API failed")

    data = res.json()
    text = data["choices"][0]["message"]["content"]

    # Remove Markdown backticks and any extra whitespace
    text = text.strip().strip("```").strip("```json").strip()
    return json.loads(text)
