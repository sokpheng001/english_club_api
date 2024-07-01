from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    username: str
    email: EmailStr
    disabled: bool

class UserCreate(UserBase):
    email: EmailStr
    password: str

class UserInDB(UserBase):
    id: int
    hashed_password: str
    class Config:
        orm_mode = True

class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class TokenForVerifyMe(BaseModel):
    token:str