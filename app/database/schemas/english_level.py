from enum import Enum

from pydantic import BaseModel

class MyLevel(Enum):
    A1 = "A1",
    A2 = "A2",
    B1 = "B1",
    B2 = "B2",
    C1 = "C1",
    C2 = "C2",

class EnglishLevel(BaseModel):
    selection: MyLevel
