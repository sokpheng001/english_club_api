from datetime import timedelta
from fastapi import Depends, HTTPException, status,APIRouter, Request, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.cruds.auth import reset_new_password,verify_otp,send_mail_with_otp,get_user_by_email,register_new_user,authenticate_user, create_access_token,get_current_user, send_verification_email, verify_email_for_user
from app.database.database import get_db
from app.database.schemas.token import Token
from app.database.schemas.user import LoginUserDto, CreateUserDto
from app.database.schemas import payload, token
from app.database.schemas.create_new_password import CreateNewPasswordDto
from datetime import date
from app.database.schemas.verify_otp import CreateVerifyOTPDto
from pydantic import EmailStr

auth_router = APIRouter()



SECRET_KEY = "fc5af23b3d9b9e0cd45773cd2f08263f440df72def83b0356a6626fe611d3b2b"

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

@auth_router.post("/login", response_model=Token)
async def login_for_access_token(form_data: LoginUserDto, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/users/me")
async def read_users_me(tok: token.TokenForVerifyMe , db: AsyncSession = Depends(get_db)):
    return payload.BaseResponse(
        date=date.today(),
        status=status.HTTP_200_OK,
        payload = await get_current_user(token=tok.token,db=db),
        message="User information found"
    )
@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(create_user: CreateUserDto, db: AsyncSession = Depends(get_db)):

    new_user = await register_new_user(create_user, db)

    # sending email notification
    await send_verification_email(new_user.email, new_user.verification_token)
    # 
    return payload.BaseResponse(
        date= date.today(),
        status=int(status.HTTP_201_CREATED),
        payload = f"Please check your email to verify your account 😉: {new_user.email}",
        message= " User has been register successfully"
    )

@auth_router.get("/verify-email/")
async def verify_email(request: Request, token: str, db: AsyncSession = Depends(get_db)):
    return await verify_email_for_user(request,token, db)

@auth_router.post("/request/reset-password")
async def reset_password(email:EmailStr = Query(None, max_length=50), db:AsyncSession = Depends(get_db)):
    user =  await get_user_by_email(db, email)
    await send_mail_with_otp(user.email, db)
    return payload.BaseResponse(
        date=date.today(),
        status=status.HTTP_200_OK,
        payload="The verification code was sent to your email, Please check your email",
        message="Email sent successfully"
    )

@auth_router.post("/request/reset-password/otp-verify")
async def otp_verify(votp:CreateVerifyOTPDto, db:AsyncSession=Depends(get_db)):
    return await verify_otp(email=votp.email, otp=votp.otp,session=db)
@auth_router.post("/reset-password")
async def reset_user_new_password(new_pass:CreateNewPasswordDto, db:AsyncSession=Depends(get_db)):
    result = await reset_new_password(new_pass, db)
    if result == True:
        return payload.BaseResponse(
            date=date.today(),
            status=status.HTTP_200_OK,
            payload="Password has been updated successfully",
            message="Password reset successfully"
        )
    return payload.BaseResponse(
        date=date.today(),
        status=status.HTTP_401_UNAUTHORIZED,
        payload="Incorrect email or OTP",
        message="Password reset failed"
    )