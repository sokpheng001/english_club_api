# schemas.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AnswerDto(BaseModel):
    q_uuid: str = "Question uuid"
    answers: Optional[list[str]] = ["Answer1", "Answer2"]
    # submit_date: Optional[datetime]
    # 

class  SubmitAnswerDto(BaseModel):
    user_uuid: Optional[str] = None
    user_answer: Optional[list[AnswerDto]]
