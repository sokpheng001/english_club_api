# schemas.py
from pydantic import BaseModel
from typing import List, Optional
from app.database.schemas.lesson import ResponseLessonDto


class CreateVocabularyDto(BaseModel):
    title:str
    thumbnail_url:str
    description:str
    lesson_uuids: Optional[list[str]] = None

class ResponseVocabularyDto(BaseModel):
    vocabulary_uuid:str
    titles:str
    thumbnail_url:str
    vocab_level: Optional[str] = None
    description:str
    lessons: Optional[list[ResponseLessonDto]] = None