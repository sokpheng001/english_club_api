# schemas.py
from pydantic import BaseModel
from typing import List, Optional
from app.database.schemas.lesson import ResponseLessonDto

class CreateGrammarDto(BaseModel):
    title: str
    description: str
    thumbnail: Optional[str] = None
    lesson_uuids: Optional[list[str]] = None

class ResponseGrammarDto(BaseModel):
    grammar_uuid: str
    title: str
    description: str
    thumbnail: Optional[str] = None
    grammar_level: Optional[str]
    lessons: Optional[list[ResponseLessonDto]]