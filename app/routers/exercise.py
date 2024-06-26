from fastapi import APIRouter, HTTPException, Depends
from app.database.schemas.exercise import CreateExerciseDto
from app.database.database import engine, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.cruds.exercise import  create_exercise
exercise_router = APIRouter()


@exercise_router.post("/exercises/")
async def add_new_exercise(ex:CreateExerciseDto, db:AsyncSession=Depends(get_db)):
    return await create_exercise(ex, db)