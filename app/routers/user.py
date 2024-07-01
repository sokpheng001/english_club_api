
from fastapi import APIRouter, HTTPException, Depends, status
from app.database.schemas.payload import BaseResponse
from app.database.schemas.user import CreateUserDto, UpdateUserDto
from app.database.cruds.user import create_user, find_user_by_uuid, delete_user_by_uuid, get_list_all_users, update_user_by_uuid
from app.database.database import engine, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.schemas import payload

from typing import Annotated
from datetime import date
user_router = APIRouter()
from app.database.cruds.auth import get_current_user
user_dependency = Annotated[dict,Depends(get_current_user)]

# @user_router.get("/users/")
# def user_home():
#     return {"message": "Hello User"}

@user_router.get("/users")
async def get_all_users(db:AsyncSession=Depends(get_db)):
    users = await get_list_all_users(db)
    return payload.BaseResponse(
        date=date.today(),
        status=status.HTTP_200_OK,
        payload=users,
        message="Users are found 😎"
    )
# @user_router.post("/users/", response_model=BaseResponse)
# async def add_new_user(user: CreateUserDto,db: AsyncSession=Depends(get_db)):
#     new_user = await create_user(user,db)
#     return new_user

@user_router.get("/users/{id}",response_model=BaseResponse)
async def find_user(id:str,db:AsyncSession=Depends(get_db)):
    new_user = await find_user_by_uuid(id,db)
    return payload.BaseResponse(
        date=date.today(),
        status=status.HTTP_200_OK,
        payload=new_user,
        message="User Created successfully 🐵"
    )

@user_router.delete("/users/{id}")
async def delete_user(id:str, db:AsyncSession=Depends(get_db)):
    re = await delete_user_by_uuid(id,db)
    return payload.BaseResponse(
        date=date.today(),
        status=status.HTTP_200_OK,
        payload=re,
        message="User deleted successfully 🤔"  
    )

@user_router.put("/users/{id}",response_model=BaseResponse)
async def update_user(id:str,user:UpdateUserDto,authen:user_dependency,db:AsyncSession=Depends(get_db)):
    re = await update_user_by_uuid(id,user,db)
    return payload.BaseResponse(
        date=date.today(),
        status=status.HTTP_200_OK,
        payload=re,
        message="User updated successfully 😎"  
    )