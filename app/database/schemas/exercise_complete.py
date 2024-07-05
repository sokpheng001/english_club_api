# schemas.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class ExerciseCompleteDto(BaseModel):
    ex_uuid: str
    ex_title: Optional[str] = None
    ex_level:Optional[str] = None
    ex_description: Optional[str] = None
    ex_thumbnail: Optional[str] = None
    scores: Decimal
    complete_date: datetime

class NewResponseCompleteExerciseDto(ExerciseCompleteDto):
    user_uuid: str

class ResponseExerciseCompleteDto(BaseModel):
    user_uuid: str
    complete_date: datetime
    exercises: ExerciseCompleteDto
    scores:  Decimal