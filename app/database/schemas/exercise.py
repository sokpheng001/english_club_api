# schemas.py
from pydantic import BaseModel
from typing import List, Optional
from app.database.schemas import question


class CreateExerciseDto(BaseModel):
    title: str
    thumbnail:str
    description: str
    questions = Optional[list[question.ResponseQuestionDto]]

class RepsonseExerciseDto(CreateExerciseDto):
    pass
