# schemas.py
from pydantic import BaseModel
from typing import List, Optional


class CreateChoiceDto(BaseModel):
    text:str
    is_correct:bool

class ResponseChoiceDto(CreateChoiceDto):
    choice_uuid:str