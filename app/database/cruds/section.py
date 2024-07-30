from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.database import Base
import uuid
from datetime import date
from app.database.schemas.section import CreateSectionDto
from fastapi import HTTPException, status
from app.models.section import Section
from app.database.schemas import payload,section
from app.database.schemas.english_level import MyLevel
from app.utils.verify import is_valid_uuid

async def create_new_section(sec:CreateSectionDto, session:AsyncSession):
    voice = [v.dict() for v in sec.voice]

    #  verify not duplicated section title
    sss = select(Section).filter(Section.section_name.ilike(sec.title))
    re = await session.execute(sss)
    result_section:Section = re.scalars().first()
    if result_section:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Section with title ' {sec.title} ' already exists")
    #  verify that level is valid
    if sec.section_level.upper() not in MyLevel.__members__:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Level should be one of A1 to C2, but you given {sec.section_level}")
    examples = [exs.dict() for exs in sec.examples]
    sec_uuid = uuid.uuid4()
    new_section = Section(section_uuid=str(sec_uuid),section_name=sec.title,voice=voice,thumbnail=sec.thumbnail_url ,section_level=sec.section_level,description=sec.description,examples=examples)
    session.add(new_section)
    await session.commit()
    return section.ResponseSectionDto(
            title=new_section.section_name,
            section_uuid=new_section.section_uuid,
            section_level=new_section.section_level,
            description=new_section.description,
            examples=new_section.examples,
            thumbnail_url= new_section.thumbnail,
            voice=voice
        )
    

async def list_all_sections(session:AsyncSession):
    try:
        query = select(Section).order_by(Section.section_level)
        result = await session.execute(query)
        sections = result.scalars().all()
        return [section.ResponseSectionDto(
                title=sec.section_name,
                section_uuid=sec.section_uuid,
                section_level=sec.section_level,
                voice=sec.voice,
                description=sec.description,
                examples=sec.examples,
                thumbnail_url= sec.thumbnail
            ) for sec in sections]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
async def get_section_by_level(level: str, session:AsyncSession):
    if level.upper() not in MyLevel.__members__:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Level should be one of A1 to C2, but you given {level}")
    
    qq  = select(Section).filter(Section.section_level.ilike(level))
    result = await session.execute(qq)
    secs = result.scalars().all()
    if not secs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Section not found")
    return [section.ResponseSectionDto(
            section_uuid=sec.section_uuid,
            section_level=sec.section_level,
            title=sec.section_name,
            thumbnail_url=sec.thumbnail,
            description=sec.description,
            examples=sec.examples,
            voice=sec.voice
            ) for sec in secs]

async def get_section_by_uuid(s_uuid:str, session:AsyncSession):
    if not is_valid_uuid(s_uuid):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Section uuid is not valid")
    
    qq  = select(Section).filter(Section.section_uuid==s_uuid)
    result = await session.execute(qq)
    sec = result.scalars().first()
    if not sec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Section not found")
    return section.ResponseSectionDto(
            section_uuid=sec.section_uuid,
            section_level=sec.section_level,
            title=sec.section_name,
            thumbnail_url=sec.thumbnail,
            description=sec.description,
            examples=sec.examples,
            voice=sec.voice 
        )


async def remove_section(s_uuid:str, session:AsyncSession):
    if not is_valid_uuid(s_uuid):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Section uuid is not valid")
    query = select(Section).filter(Section.section_uuid == s_uuid)
    result = await session.execute(query)
    sec = result.scalars().first()
    if not sec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section is not found")
    await session.delete(sec)
    await session.commit()
    return s_uuid

