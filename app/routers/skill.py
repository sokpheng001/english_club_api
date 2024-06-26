from fastapi import APIRouter, HTTPException, Depends
from app.database.schemas import skill
from app.database.database import get_db
from app.database.cruds.skill import create_new_skill, list_all_skills
from sqlalchemy.ext.asyncio import AsyncSession
skill_router = APIRouter()


@skill_router.post("/skills/")
async def add_new_skill(sk:skill.CreateSkillDto, db:AsyncSession=Depends(get_db)):
    return await create_new_skill(sk, db)

@skill_router.get("/skills/")
async def get_all_skills(db:AsyncSession=Depends(get_db)):
    return await list_all_skills(db)