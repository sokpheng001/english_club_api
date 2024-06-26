# schemas.py
from pydantic import BaseModel
from typing import List, Optional


class CreateChoiceDto(BaseModel):
    tex:str
    is_correct:bool

class ResponseChoice(CreateChoiceDto):
    pass