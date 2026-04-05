from pydantic import BaseModel
from typing import Optional, List

class SignUpRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class StartInterviewRequest(BaseModel):
    role: str

class EvaluateAnswerRequest(BaseModel):
    interview_id: int
    question_index: int
    question_text: str
    user_answer: str

class QuestionFeedback(BaseModel):
    score: float
    strengths: str
    weaknesses: str
    advice: str

class InterviewResult(BaseModel):
    interview_id: int
    role: str
    final_score: float
    questions: List[dict]