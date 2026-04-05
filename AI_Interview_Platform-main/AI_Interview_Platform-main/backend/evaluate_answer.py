import os
import app
from groq import Groq

# Add at top with other imports
client = None
if os.getenv("GROQ_API_KEY"):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.post("/evaluate_answer")
async def evaluate_answer(request: dict):
    global client
    data = request
    user_answer = data['user_answer']
    question_text = data['question_text']
    
    if not client:
        # Fallback to mock evaluation
        score = min(10, max(1, len(user_answer.split()) // 3 + 2))
        return {
            "feedback": {
                "score": score,
                "strengths": "Good structure and clarity" if score > 7 else "Basic understanding",
                "weaknesses": "Could elaborate more" if score < 8 else "Excellent response",
                "advice": "Practice speaking clearly with concrete examples."
            }
        }
    
    # REAL Groq AI Evaluation
    prompt = f"""You are an expert technical interviewer evaluating a job candidate.

QUESTION: {question_text}

CANDIDATE ANSWER: {user_answer}

Score 1-10 (10=perfect interview answer) and respond ONLY with valid JSON:

{{
  "score": 8,
  "strengths": "Clear explanation, good examples, structured answer",
  "weaknesses": "Missed key concepts, unclear examples", 
  "advice": "Use STAR method: Situation, Task, Action, Result"
}}

Be specific, constructive, and realistic for the role."""

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",  # Fast & powerful
            temperature=0.1,
            max_tokens=500
        )
        
        # Extract JSON from response
        response = chat_completion.choices[0].message.content.strip()
        import json
        feedback = json.loads(response)
        
        return {"feedback": feedback}
        
    except Exception as e:
        # Fallback if Groq fails
        return {
            "feedback": {
                "score": 7,
                "strengths": "Good effort",
                "weaknesses": "Technical issue",
                "advice": "Speak clearly and structure answers"
            }
        }