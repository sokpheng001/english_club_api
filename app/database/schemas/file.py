from typing import Optional
from pydantic import BaseModel


class FileResponse(BaseModel):
    file_name: str
    file_path: str
    file_size: int