from psycopg2 import Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.database import Base
from app.database.schemas import user
from app.models.user import User
import uuid
from fastapi import HTTPException, status
from sqlalchemy import exc
from datetime import date
from app.database.schemas.payload import BaseResponse
from app.database.schemas.user import RepsonseUserDto, UpdateUserDto
from app.utils.verify import is_valid_uuid
 # Import asyncpg's UniqueViolationError


async def get_list_all_users(session:AsyncSession):
     query = select(User).where(User.is_deleted == False).order_by(User.created_date.desc())
     result = await session.execute(query)
     users = result.scalars().all()
     users_repsonse:RepsonseUserDto = []
     for user in users:
          users_repsonse.append(RepsonseUserDto(
               user_uuid = user.uuid,
               user_name = user.user_name,
               email = user.email,
               profile = user.profile,
               bio= user.bio,
               created_date=user.created_date,
               updated_date= user.updated_date,
               is_deleted = user.is_deleted,
          ))
     return users_repsonse

async def create_user( create_user: user.CreateUserDto,session: AsyncSession):
    user_uuid = str(uuid.uuid4())
    new_user = User(user_uuid, create_user.user_name, create_user.email, create_user.password,created_date=date.today(), updated_date=date.today())
    
    try:
        session.add(new_user)
        await session.commit()
        return RepsonseUserDto(
               user_uuid = new_user.uuid,
               user_name = new_user.user_name,
               email = new_user.email,
               profile = new_user.profile,
               bio= new_user.bio,
               created_date= new_user.created_date,
               updated_date= new_user.updated_date,
               is_deleted = new_user.is_deleted,
         )
    except exc.IntegrityError as e:
        detail_message = ""
        db_error_msg = str(e.orig)
 # Parse the error message to extract the detail after "DETAIL:"
# Extract the specific detail message indicating email duplication
        if 'Key (' in db_error_msg and 'already exists' in db_error_msg:
            detail_message = db_error_msg.split('Key (')[1].split(')')[0] + " already exists."
        else:
            detail_message = db_error_msg
        await session.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail_message)
        # Rollback the session explicitly
        
async def find_user_by_uuid(id:str,session: AsyncSession):
    query = select(User).filter(User.uuid == id)
    result = await session.execute(query)
    u = result.scalars().first()
    if not u:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return RepsonseUserDto(
            user_uuid = u.uuid,
            user_name = u.user_name,
            email = u.email,
            profile =u.profile,
            bio= u.bio,
            created_date= u.created_date,
            updated_date= u.updated_date,
            is_deleted = u.is_deleted,
        )

async def delete_user_by_uuid(id:str, session:AsyncSession):
    if not is_valid_uuid(id):
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user uuid 🤔")
    query = select(User).filter(User.uuid == id)
    result = await session.execute(query)
    u = result.scalars().first()
    if not u:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not found")
    else:
        await session.delete(u)
        await session.commit()
        content = f"User with ID {id} has deleted succcessfully"
        return id
 
async def update_user_by_uuid(id:str, user_update: UpdateUserDto ,session:AsyncSession):
    if not is_valid_uuid(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user uuid 🤔")
    user = select(User).filter(User.uuid == id)
    result = await session.execute(user)
    u:User = result.scalars().first()

    if not u:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not found")
    
    u.updated_date = date.today() # set updated date

    update_data = user_update.dict(exclude_unset=True)  # Exclude fields that were not set
    for key, value in update_data.items():
        setattr(u, key, value)
    await session.commit()
    await session.refresh(u)
    return RepsonseUserDto(
                  user_uuid = u.uuid,
                  user_name = u.user_name,
                  email = u.email,
                  profile = u.profile,
                  bio= u.bio,
                  created_date= u.created_date,
                  updated_date= u.updated_date,
                  is_deleted = u.is_deleted,
    )
        