from fastapi import APIRouter, HTTPException, Depends
from app.database.schemas import skill
from app.database.database import get_db
from app.database.cruds.skill import create_new_skill, list_all_skills, get_all_skills_by_skill_name,get_skill_by_name_and_level, delete_skill_by_uuid
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from app.database.cruds.auth import get_current_user

user_dependency = Annotated[dict,Depends(get_current_user)]
skill_router = APIRouter()


@skill_router.post("/skills/")
async def add_new_skill(sk:skill.CreateSkillDto, db:AsyncSession=Depends(get_db)):
    return await create_new_skill(sk, db)


@skill_router.delete("/skills/{id}")
async def delete_skill(id:str,db:AsyncSession=Depends(get_db),):
    return await delete_skill_by_uuid(id, db)

@skill_router.get("/skills/")
async def get_all_skills(db:AsyncSession=Depends(get_db)):
    return await list_all_skills(db)

@skill_router.get("/skills/{name}")

async def get_skill_by_name(name:str, db:AsyncSession=Depends(get_db)):
    skill = await get_all_skills_by_skill_name(name, db)
    return skill

@skill_router.get("/skills/skill_name={name}/level={level}")
async def get_skills_by_name_and_level_(name:str,level:str, db:AsyncSession=Depends(get_db)):
    skill = await get_skill_by_name_and_level(name, level, db)
    return skill