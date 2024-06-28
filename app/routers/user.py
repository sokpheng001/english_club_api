from typing import Dict, Union
from fastapi import APIRouter, HTTPException, Depends
from app.database.schemas.payload import BaseResponse
from app.database.schemas.user import CreateUserDto, UpdateUserDto
from app.database.cruds.user import create_user, find_user_by_uuid, delete_user_by_uuid, get_list_all_users, update_user_by_uuid
from app.database.database import engine, get_db
from sqlalchemy.ext.asyncio import AsyncSession
user_router = APIRouter()


# @user_router.get("/users/")
# def user_home():
#     return {"message": "Hello User"}

@user_router.get("/users")
async def get_all_users(db:AsyncSession=Depends(get_db)):
    users = await get_list_all_users(db)
    return users

# @user_router.post("/users/", response_model=BaseResponse)
# async def add_new_user(user: CreateUserDto,db: AsyncSession=Depends(get_db)):
#     new_user = await create_user(user,db)
#     return new_user

@user_router.get("/users/{id}",response_model=BaseResponse)
async def find_user(id:str,db:AsyncSession=Depends(get_db)):
    new_user = await find_user_by_uuid(id,db)
    return new_user

@user_router.delete("/users/{id}")
async def delete_user(id:str, db:AsyncSession=Depends(get_db)):
    re = await delete_user_by_uuid(id,db)
    return re

@user_router.put("/users/{id}",response_model=BaseResponse)
async def update_user(id:str,user:UpdateUserDto,db:AsyncSession=Depends(get_db)):
    re = await update_user_by_uuid(id,user,db)
    return re