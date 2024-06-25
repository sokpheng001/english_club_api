from typing import Optional
from pydantic import BaseModel, EmailStr


class CreateUserDto(BaseModel):
    user_name:str
    email: EmailStr
    password: str

class LoginUserDto(BaseModel):
    email: EmailStr
    password: str

class UpdateUserDto(BaseModel):
    user_name:str | None
    email: EmailStr | None
    password: str | None
    profile: str | None
    bio: str | None
    
class RepsonseUserDto(BaseModel):
    user_uuid: str | None
    user_name: str | None
    email: EmailStr | None
    profile: str | None
    bio: str | None
    is_deleted: bool | None