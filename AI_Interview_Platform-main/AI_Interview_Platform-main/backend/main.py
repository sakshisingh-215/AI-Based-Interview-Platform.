from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from datetime import datetime
import hashlib
import jwt
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "super-secret-key"

class User(BaseModel):
    email: str
    password: str

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

# CREATE TABLE ON STARTUP
conn = sqlite3.connect("app.db", check_same_thread=False)
conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
""")
conn.commit()
conn.close()

@app.post("/signup")
def signup(user: User):
    conn = sqlite3.connect("app.db")
    hashed = hash_password(user.password)
    
    try:
        conn.execute(
            "INSERT INTO users (email, password, created_at) VALUES (?, ?, ?)",
            (user.email, hashed, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        return {"message": "Signup success!", "email": user.email}
    except:
        conn.close()
        return {"error": "Email exists"}

@app.post("/login")
def login(user: User):
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    cur.execute("SELECT id, password FROM users WHERE email = ?", (user.email,))
    row = cur.fetchone()
    conn.close()
    
    if row and hash_password(user.password) == row[1]:
        token = jwt.encode({"sub": row[0]}, SECRET_KEY)
        return {"access_token": token, "message": "✅ Login success!"}
    return {"error": "Invalid credentials"}

@app.post("/start_interview")
async def start_interview(request: dict):
    role = request.get("role", "Software Engineer")
    questions = {
        "Data Scientist": [
            "Explain gradient descent and its variants like SGD and Adam optimizer.",
            "How would you handle imbalanced datasets? Mention SMOTE and undersampling.",
            "Walk me through a complete machine learning project from data to deployment.",
            "What is cross-validation? Why is it better than train-test split?",
            "Explain overfitting and how L1/L2 regularization prevents it."
        ],
        "Software Engineer": [
            "Explain REST APIs vs GraphQL. When would you use each?",
            "How does async/await work in JavaScript? Show with example.",
            "What is a closure in JavaScript? Provide a practical example.",
            "Explain let, const, var differences with scope examples.",
            "How would you optimize a slow REST API endpoint?"
        ],
        "Product Manager": [  # NEW - REAL PM QUESTIONS!
            "How do you prioritize features in a product roadmap?",
            "Walk me through how you'd launch a new feature.",
            "How do you handle conflicting stakeholder priorities?",
            "What metrics would you track for a new mobile app feature?",
            "Describe a product you love and why it succeeds."
        ]
    }.get(role, ["Tell me about yourself."] * 5)
    
    return {
        "interview_id": f"interview_{int(datetime.now().timestamp())}",
        "role": role,
        "questions": questions,
        "current_question": 0,
        "max_questions": 5
    }

@app.post("/evaluate_answer")
async def evaluate_answer(request: dict):
    data = request
    user_answer = data.get("user_answer", "").lower()
    question_text = data.get("question_text", "").lower()
    
    answer_words = user_answer.split()
    
    # ENHANCED SMART SCORING - More roles!
    if "imbalanced" in question_text:
        keywords = ["smote", "oversample", "undersample", "resample", "balance"]
        score = sum(1 for word in answer_words if any(kw in word for kw in keywords))
        weakness = "Mention SMOTE/oversampling"
    elif "gradient" in question_text:
        keywords = ["gradient", "descent", "learning", "rate", "sgd", "adam"]
        score = sum(1 for word in answer_words if any(kw in word for kw in keywords))
        weakness = "Explain SGD/Adam variants"
    elif "overfitting" in question_text:
        keywords = ["overfit", "regularization", "l1", "l2", "ridge"]
        score = sum(1 for word in answer_words if any(kw in word for kw in keywords))
        weakness = "Discuss L1/L2 regularization"
    elif "prioritize" in question_text or "roadmap" in question_text:
        keywords = ["rice", "impact", "effort", "reach", "customer", "priority", "score"]
        score = sum(1 for word in answer_words if any(kw in word for kw in keywords))
        weakness = "Use RICE framework or mention customer feedback"
    elif "launch" in question_text or "feature" in question_text:
        keywords = ["mvp", "beta", "metrics", "test", "iterate", "kpi"]
        score = sum(1 for word in answer_words if any(kw in word for kw in keywords))
        weakness = "Outline MVP → Beta → Launch → Iterate steps"
    else:
        score = max(1, min(5, len(answer_words) // 3))
        weakness = "Answer the specific question"
    
    if len(answer_words) < 8: score = max(1, score - 2)
    if len(answer_words) > 20: score += 1
    score = min(10, max(1, score))
    
    return {
        "feedback": {
            "score": int(score),
            "strengths": "Good technical depth" if score > 7 else "Good effort",
            "weaknesses": weakness,
            "advice": "Use technical terms + project examples"
        }
    }

@app.get("/")
def root():
    return {"message": "✅ AI Interview Backend READY!"}
