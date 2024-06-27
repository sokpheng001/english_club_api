from typing import Optional
from pydantic import BaseModel, EmailStr

class CreateLessonDto():

    name:Optional[str]
    description:Optional[str]
    thumbnail: Optional[str]
    lesson_level: Optional[str]
    