from enum import Enum

from pydantic import BaseModel

class QuestionType(Enum):
    MULTIPLE_CHOICES = "Multiple Choices",
    TRUE_OR_FALSE = "True or False",
    FILL_IN_THE_BLANK = "Fill in the blank",

