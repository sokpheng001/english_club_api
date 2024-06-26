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
from app.database.schemas.user import RepsonseUserDto 
 # Import asyncpg's UniqueViolationError

async def create_user( create_user: user.CreateUserDto,session: AsyncSession):
    user_uuid = str(uuid.uuid4())
    new_user = User(user_uuid, create_user.user_name, create_user.email, create_user.password)
    
    try:
        session.add(new_user)
        await session.commit()
        return BaseResponse (
         date= date.today(),
         status=int(status.HTTP_204_NO_CONTENT),
         payload = RepsonseUserDto(
               user_uuid = new_user.uuid,
            user_name = new_user.user_name,
            email = new_user.email,
             profile = new_user.profile,
            bio= new_user.bio,
            is_deleted = new_user.is_deleted,
         ),
         message=f"Created new user successfully",
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
    return BaseResponse(
         date= date.today(),
         status=int(status.HTTP_204_NO_CONTENT),
         payload = RepsonseUserDto(
            user_uuid = u.uuid,
            user_name = u.user_name,
            email = u.email,
            profile =u.profile,
            bio= u.bio,
            is_deleted = u.is_deleted,
        ),
         message=f"User with ID {id} has been found",
    )

async def delete_user_by_uuid(id:str, session:AsyncSession):
    query = select(User).filter(User.uuid == id)
    result = await session.execute(query)
    u = result.scalars().first()
    if not u:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not found")
    else:
        await session.delete(u)
        await session.commit()
        content = f"User with ID {id} has deleted succcessfully"
        response = BaseResponse(
             date= date.today(),
             status=int(status.HTTP_204_NO_CONTENT),
             payload=None,
             message=content,
        )
        return response 
 
async def update_user_by_uuid(id:str, session:AsyncSession):
    pass