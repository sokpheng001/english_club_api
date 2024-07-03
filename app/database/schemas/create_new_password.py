from pydantic import BaseModel

class CreateNewPasswordDto(BaseModel):
    email:str
    new_password: str
    confirm_password: str