from fastapi import APIRouter, HTTPException, Depends
from app.database.schemas.exercise import CreateExerciseDto
from app.database.database import engine, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.cruds.exercise import  create_exercise,list_all_exercises,get_exercises_by_skill_id
exercise_router = APIRouter()


@exercise_router.post("/exercises/")
async def add_new_exercise(ex:CreateExerciseDto, db:AsyncSession=Depends(get_db)):
    return await create_exercise(ex, db)

@exercise_router.get("/exercises/")
async def get_all_exercises(db:AsyncSession=Depends(get_db)):
    return await list_all_exercises(db)
                      

@exercise_router.get("/exercises/skill/{skill_id}")
async def get_exercises_by_skill(skill_id:str, db:AsyncSession=Depends(get_db)):
    return await get_exercises_by_skill_id(skill_id, db)