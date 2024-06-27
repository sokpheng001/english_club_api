# schemas.py
from pydantic import BaseModel
from typing import List, Optional
from app.database.schemas import exercise

class CreateSkillDto(BaseModel):
    skill_name:str = "Reading"
    thumbnail:Optional[str]= "cstad.jpg"
    description:str = "This skill will help you"
    skill_level:str="A1"
    exercises_uuid: Optional[List[str]] = None

class ResponseSkillDto(BaseModel):
    skill_uuid:Optional[str]
    skill_name:str
    thumbnail:Optional[str]=None
    description:str
    skill_level:str
    exercises:Optional[list[exercise.RepsonseExerciseDto]]

class ResponseSkillWithoutQuestionDto(BaseModel):
    skill_uuid:Optional[str]
    skill_name:str
    thumbnail:Optional[str]=None
    description:str
    skill_level:str
    exercises:Optional[list[exercise.RepsonseExerciseWithoutQuestionDto]]
