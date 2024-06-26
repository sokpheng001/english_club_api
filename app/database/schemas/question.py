# schemas.py
from pydantic import BaseModel
from typing import List, Optional
from app.database.schemas import choice

class CreateQuestionDto(BaseModel):
    text: str
    voice: Optional[str] = None
    video: Optional[str] = None
    type: Optional[str] # e.g., "multiple-choice", "fill-in-the-blank", "true-false"
    correct_answer: Optional[str]
    choices:Optional[list[choice.ResponseChoice]]

class ResponseQuestionDto(CreateQuestionDto):
    pass