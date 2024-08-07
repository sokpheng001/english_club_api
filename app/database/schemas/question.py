# schemas.py
from pydantic import BaseModel
from typing import List, Optional
from app.database.schemas import choice
from app.database.schemas.answer import Answer

class CreateQuestionDto(BaseModel):
    question_text: str
    voice: Optional[str] = "link"
    video: Optional[str] = "link"
    image: Optional[str] = "link"
    type: Optional[str] = "Multiple_Choices or Fill_in_the_blank or True_or_False" # e.g., "multiple-choice", "fill-in-the-blank", "true-false"
    question_level: Optional[str] = "A1"
    correct_answer: Optional[list[Answer]] 
    choices: Optional[list[choice.CreateChoiceDto]]
    # exercise_uuid: Optional[str] =  "optional"
    
class ResponseQuestionDto(BaseModel):
    q_uuid: str
    question_text: str
    voice: Optional[str] = None
    video: Optional[str] = None
    image: Optional[str] = None
    type: Optional[str] # e.g., "multiple-choice", "fill-in-the-blank", "true-false"
    question_level: Optional[str]
    correct_answer: Optional[list[Answer]]
    choices:Optional[list[choice.ResponseChoiceDto]]
    