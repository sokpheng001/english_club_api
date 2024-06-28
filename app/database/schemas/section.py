from typing import Optional
from pydantic import BaseModel, EmailStr
class CreateSectionDto(BaseModel):
    title: str
    description: str
    examples: list[str]