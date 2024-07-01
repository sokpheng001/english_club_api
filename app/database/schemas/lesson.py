from typing import Optional
from pydantic import BaseModel, EmailStr
from app.database.schemas.section import ResponseSectionDto
from app.database.schemas.exercise import RepsonseExerciseDto

class CreateLessonDto(BaseModel):
    name:Optional[str]
    description:Optional[str]
    thumbnail: Optional[str]
    sections_uuids: Optional[list[str]]
    exercises_uuids: Optional[list[str]]

class ResponseLessonDto(BaseModel):
    lesson_uuid:Optional[str]
    lesson_title:Optional[str]
    description:Optional[str]
    thumbnail: Optional[str]
    lesson_level:str
    sections: Optional[list[ResponseSectionDto]]
    exercises: Optional[list[RepsonseExerciseDto]]

class ResponseLessonWithoutSectionsDto(BaseModel):
    lesson_uuid:Optional[str]
    lesson_title:Optional[str]
    description:Optional[str]
    thumbnail: Optional[str]
    lesson_level:str