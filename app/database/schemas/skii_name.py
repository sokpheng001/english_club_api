from enum import Enum

from pydantic import BaseModel

class Skill(Enum):
    READING = "READING",
    WRITING = "WRITING",
    LISTENING = "LISTENING",

