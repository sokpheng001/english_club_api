from fastapi import APIRouter, HTTPException, Depends
from app.database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.cruds.lesson import create_new_lessons
from app.database.schemas.lesson import CreateLessonDto

lesson_router = APIRouter()


@lesson_router.post("/lessons/")
async def add_new_lesson(lesson:CreateLessonDto, db:AsyncSession=Depends(get_db)):
    return await create_new_lessons(lesson, get_db)

