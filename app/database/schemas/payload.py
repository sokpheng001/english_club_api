from psycopg2 import Date
from pydantic import BaseModel
from datetime import date

class BaseResponse(BaseModel):
    date: date | None
    status: int | None
    payload: object | None
    message: str | None