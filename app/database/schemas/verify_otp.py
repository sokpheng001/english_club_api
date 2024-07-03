from pydantic import BaseModel

class CreateVerifyOTPDto(BaseModel):
    email:str
    otp:str