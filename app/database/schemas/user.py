from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class CreateUserDto(BaseModel):
    username:str
    email: EmailStr
    password: str

class LoginUserDto(BaseModel):
    email: EmailStr
    password: str

class UpdateUserDto(BaseModel):
    user_name:Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    profile:  Optional[str] = None
    updated_date: datetime = None
    bio: Optional[str] = None
    
class RepsonseUserDto(BaseModel):
    user_uuid: str | None
    user_name: str | None
    email: EmailStr | None
    profile: str | None
    bio: str | None
    created_date: datetime
    updated_date: datetime
    is_deleted: bool | None