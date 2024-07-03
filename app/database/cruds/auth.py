from datetime import datetime, timedelta

from passlib.context import CryptContext
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.database.schemas import user as ur
from fastapi.security import OAuth2PasswordBearer
from app.database.schemas.token import TokenData
from app.database.schemas.user import CreateUserDto
from app.database.schemas.create_new_password import CreateNewPasswordDto
from fastapi import Depends, HTTPException, status,Header
from app.database.database import get_db
import jwt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from fastapi.templating import Jinja2Templates
import smtplib
from  datetime import date
import uuid
from app.models.otp import OTPModel
from fastapi import Request
from app.utils.otp import generate_otp

from itsdangerous import URLSafeTimedSerializer

SECRET_KEY = "fc5af23b3d9b9e0cd45773cd2f08263f440df72def83b0356a6626fe611d3b2b"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme =  OAuth2PasswordBearer(tokenUrl="" )
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="app/templates")
sender_email = "kimchansokpheng123@gmail.com"
sender_password = "mpqy wwdh oszi csaw"


async def reset_new_password(new_pass: CreateNewPasswordDto, session:AsyncSession):
    otp_entry = select(OTPModel).filter(OTPModel.email==new_pass.email, OTPModel.is_used==True).order_by(OTPModel.created_at.desc())
    result = await session.execute(otp_entry)
    otp_model:OTPModel = result.scalars().first()

    if not otp_model:
        raise HTTPException(status_code=400, detail=f"The email {new_pass.email} is not verified on OTP")
    
    # verify user
    user = select(User).filter(User.email==new_pass.email)
    re = await session.execute(user)
    u:User = re.scalars().first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    
    # update user password
    u.password = get_password_hash(new_pass.new_password)

    await session.delete(otp_model)
    await session.commit() 

    
    return True

async def verify_email_for_user(request:Request,token:str, db:AsyncSession):
    email = confirm_verification_token(token, SECRET_KEY)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    u = select(User).filter(User.email == email)
    result = await db.execute(u)
    user:User = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_verified = True
    user.verification_token = None
    await db.commit()
    await db.refresh(user)

    # create a html page for showing user have been verified 😉
    return templates.TemplateResponse("notification.html", {"request": request, "message": "User has been verified"})



def generate_verification_token(email, secret_key):
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(email, salt='email-confirmation-salt')

def confirm_verification_token(token, secret_key, expiration=3600):
    serializer = URLSafeTimedSerializer(secret_key)
    try:
        email = serializer.loads(token, salt='email-confirmation-salt', max_age=expiration)
    except:
        return False
    return email

async def send_mail_with_otp(email:str, session=AsyncSession):
    receiver_email = email
       # Set up the Jinja2 environment for HTML email template
    env = Environment(loader=FileSystemLoader('app/templates'))
    template = env.get_template('otp.html')
    otp = generate_otp(6)
    # Render the HTML template with the OTP code
    html_content = template.render(otp_code=otp)
    message = MIMEMultipart("alternative")
    message["Subject"] = "Email Verification"
    message["From"] = sender_email
    message["To"] = receiver_email
 
    part1 = MIMEText(html_content, "html")
    message.attach(part1)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
    
    new_otp = OTPModel(otp=otp,email=email, expires_at=datetime.utcnow()+timedelta(minutes=15))
    session.add(new_otp)
    await session.commit()

async def verify_otp(email:str, otp:str,session:AsyncSession):
    u = select(OTPModel).filter(OTPModel.email == email, OTPModel.otp==otp)
    result = await session.execute(u)
    otp_model: OTPModel = result.scalars().first()

    if not otp_model:
        raise HTTPException(status_code=404, detail="OTP not found")
    
    if otp_model.expires_at < datetime.utcnow():
        raise HTTPException(status_code=403, detail="OTP is expired")
    
    if otp_model.otp!= otp:
        raise HTTPException(status_code=403, detail="Invalid OTP")
    
    otp_model.is_used = True
    # otp_model.delete()
    await session.commit()
    return True

async def send_verification_email(email:str, token:str):

    receiver_email = email
       # Set up the Jinja2 environment for HTML email template
    env = Environment(loader=FileSystemLoader('app/templates'))
    template = env.get_template('verify_email.html')
    verification_link = f"http://localhost:50005/verify-email/?token={token}"
    html_content = template.render(verification_link=verification_link)
    message = MIMEMultipart("alternative")
    message["Subject"] = "Email Verification"
    message["From"] = sender_email
    message["To"] = receiver_email
 
    part1 = MIMEText(html_content, "html")
    message.attach(part1)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())

async def get_user_by_email(db: AsyncSession, email: str):
    async with db.begin():
        result = await db.execute(select(User).filter(User.email == email))
        us = result.scalars().first()
        if not us:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not found")
        return us

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
    if user.is_verified== False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not verified 😏")
    if not verify_password(password, user.password):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
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


async def register_new_user(create_user:CreateUserDto, db:AsyncSession):
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
    new_user.verification_token = generate_verification_token(new_user.email, SECRET_KEY)
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user