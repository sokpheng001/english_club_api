from typing import Optional
from pydantic import BaseModel, EmailStr
from app.database.schemas.example import Example

class VoiceUrl(BaseModel):
    voice_url: str
class CreateSectionDto(BaseModel):

    title: str
    description: str
    section_level: str
    voice: Optional[list[VoiceUrl]]
    examples: list[Example]
    thumbnail_url: Optional[str] = None

class ResponseSectionDto(CreateSectionDto):
    section_uuid: str
    pass