from typing import Optional
from pydantic import BaseModel, EmailStr

class CreateLessonDto(BaseModel):
    name:Optional[str]
    description:Optional[str]
    thumbnail: Optional[str]
    sections_uuids: Optional[list[str]]