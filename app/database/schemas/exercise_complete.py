# schemas.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ExerciseCompleteDto(BaseModel):
    ex_uuid: str
    ex_title: str
    ex_level:str
    ex_description: str
    ex_thumbnail: Optional[str] = None

class ResponseExerciseCompleteDto(BaseModel):
    user_uuid: str
    complete_date: datetime
    exercises: ExerciseCompleteDto
    scores: str