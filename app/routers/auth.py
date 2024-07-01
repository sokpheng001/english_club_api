from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status,APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.cruds.auth import authenticate_user, create_access_token,get_user_by_email,get_password_hash,get_current_user
from app.database.database import get_db
from app.database.schemas.token import Token, UserOut, TokenData,UserCreate
from app.database.schemas.user import LoginUserDto, CreateUserDto, RepsonseUserDto
from app.database.schemas import payload, token
from datetime import date
import jwt
from app.models.user import User
import uuid

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
    return await get_current_user(token=tok.token,db=db)
@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(create_user: CreateUserDto, db: AsyncSession = Depends(get_db)):
    if create_user.password !=create_user.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password do not match 😒",
        )
    existing_user = await get_user_by_email(db, create_user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    hashed_password = get_password_hash(create_user.password)
    new_user = User(str(uuid.uuid4()),
                     create_user.username,
                     create_user.email,
                       hashed_password,
                       created_date=date.today(),
                         updated_date=date.today())

    db.add(new_user)
    await db.commit()
    return payload.BaseResponse(
        date= date.today(),
        status=int(status.HTTP_201_CREATED),
        payload = RepsonseUserDto(
               user_uuid = new_user.uuid,
               user_name = new_user.user_name,
               email = new_user.email,
               profile = new_user.profile,
               bio= new_user.bio,
               created_date=new_user.created_date,
               updated_date= new_user.updated_date,
               is_deleted = new_user.is_deleted,
          ),
        message= " User has been register successfully"
    )