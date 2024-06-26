
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.database import Base
import uuid
from fastapi import HTTPException, status
from sqlalchemy import exc
from app.models.skill import Skill
from datetime import date
from app.database.schemas import skill, payload


async def create_new_skill(sk:skill.CreateSkillDto, session=AsyncSession):
    sk_uuid =str(uuid.uuid4())
    new_skill = Skill(sk_uuid, sk.skill_name, sk.thumbnail, sk.description, sk.skill_level,False)
    try:
        session.add(new_skill) # add to database
        await session.commit()
        await session.refresh(new_skill)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error while creating new skill")
    return payload.BaseResponse(
        date=date.today(),
        status=int(status.HTTP_200_OK),
        payload=skill.ResponseSkillDto(
            skill_uuid=new_skill.skill_uuid,
            skill_name=new_skill.skill_name,
            thumbnail=new_skill.thumbnail,
            description=new_skill.description,
            skill_level=new_skill.skill_level,
            is_deleted=new_skill.is_deleted,
            exercises=[]
        ),
        message=f"Created new skill successfully",
    )

async def list_all_skills(session:AsyncSession):
    query = select(Skill).where(Skill.is_deleted == False)
    re = await session.execute(query)
    skills = re.scalars().all()
    skls:skill.ResponseSkillDto = []
    for sk in skills:
        skls.append(skill.ResponseSkillDto(
            skill_uuid=sk.skill_uuid,
            skill_name=sk.skill_name,
            thumbnail=sk.thumbnail,
            description=sk.description,
            skill_level=sk.skill_level,
            is_deleted=sk.is_deleted,
            exercises=[]
        ))
    return payload.BaseResponse(
        date=date.today(),
        status=int(status.HTTP_200_OK),
        payload=skls,
        message=f"List all skills",
    )