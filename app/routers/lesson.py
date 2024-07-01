from fastapi import APIRouter, HTTPException, Depends, status
from datetime import date
from app.database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.cruds.lesson import create_new_lessons, lis_all_lessons, get_lesson_by_level, delete_lesson_by_uuid
from app.database.schemas.lesson import CreateLessonDto
from app.database.schemas import payload
from typing import Annotated
from app.database.cruds.auth import get_current_user
user_dependency = Annotated[dict,Depends(get_current_user)] # to get security
lesson_router = APIRouter()


@lesson_router.post("/lessons/is-include-exercises={answer}")
async def add_new_lesson(answer:bool,lesson:CreateLessonDto,db:AsyncSession=Depends(get_db)):
    return payload.BaseResponse(
            date=date.today(),
            status=int(status.HTTP_201_CREATED),
            payload=await create_new_lessons(an,lesson, db),
            message="Creates a new Lesson successfully"
        )
@lesson_router.get("/lessons/")
async def get_all_lessons(db:AsyncSession=Depends(get_db)):
    return payload.BaseResponse(
            date=date.today(),
            status=int(status.HTTP_200_OK),
            payload=await lis_all_lessons(db),
            message="List all lessons successfully"
        )

@lesson_router.get("/lessons/{level}")
async def find_lesson_by_level(level:str, db:AsyncSession=Depends(get_db)):
    return payload.BaseResponse(
        date=date.today(),
        status=int(status.HTTP_200_OK),
        payload=await get_lesson_by_level(level, db),
        message="Lesson found"
    )

@lesson_router.delete("/lessons/{id}")
async def delete_lesson(id:str, db:AsyncSession=Depends(get_db)):
    return payload.BaseResponse(
        date=date.today(),
        status=int(status.HTTP_200_OK),
        payload=await delete_lesson_by_uuid(id, db),
        message="Lesson deleted successfully"
    )