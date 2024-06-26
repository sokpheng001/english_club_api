# schemas.py
from pydantic import BaseModel
from typing import List, Optional
from app.database.schemas import exercise

class CreateSkillDto(BaseModel):
    skill_name:str
    thumbnail:Optional[str]=None
    description:str
    skill_level:str
    exercises:Optional[list[exercise.RepsonseExerciseDto]]