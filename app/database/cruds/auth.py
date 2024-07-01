from datetime import datetime, timedelta
# from jose import JWTError, jwt
import fastapi.security
from passlib.context import CryptContext
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.database.schemas import user as ur
from fastapi.security import OAuth2PasswordBearer
from app.database.schemas.token import TokenData

from fastapi import Depends, HTTPException, status,Header
from app.database.database import get_db
import jwt

SECRET_KEY = "fc5af23b3d9b9e0cd45773cd2f08263f440df72def83b0356a6626fe611d3b2b"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme =  OAuth2PasswordBearer(tokenUrl="" )
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user_by_email(db: AsyncSession, email: str):
    async with db.begin():
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = None
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"expire": expire.isoformat(), "type": "refresh"})
    encoded_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_token


async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    print(token)
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        # Additional checks or validations here if needed
        token_data = TokenData(email=email)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWKError as e:
        print(f"JWT Decode Error: {str(e)}")
        raise credentials_exception
    except Exception as e:
        print(f"Error validating token: {str(e)}")
        raise credentials_exception
    user = await get_user_by_email(db, email=token_data.email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return ur.RepsonseUserDto(
        user_uuid = user.uuid,
        user_name = user.user_name,
        email = user.email,
        profile=user.profile,
        created_date= user.created_date,
        updated_date = user.updated_date,
        is_deleted=user.is_deleted,
        bio=user.bio
    )
