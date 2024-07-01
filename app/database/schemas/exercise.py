# schemas.py
from pydantic import BaseModel
from typing import List, Optional
from app.database.schemas import question



class CreateExerciseDto(BaseModel):
    title: str
    thumbnail:str
    description: str
    tip:str
    # skill_uuid: Optional[str]=None
    q_uuids: Optional[list[str]]
    # exercise_level: Optional[str] = "A1"
    

class RepsonseExerciseDto(BaseModel):
    ex_uuid:str
    title: str
    thumbnail:str
    description: str
    tip:str
    exercise_level: Optional[str]
    # skill_uuid: Optional[str]=None
    questions:Optional[list[question.ResponseQuestionDto]]

class RepsonseExerciseWithoutQuestionDto(BaseModel):
    ex_uuid:str
    title: str
    thumbnail:str
    description: str
    tip:str
    exercise_level: Optional[str]
    # skill_uuid: Optional[str]=None
    # questions:Optional[list[question.ResponseQuestionDto]]
