from fastapi import APIRouter, HTTPException, Depends, status
from datetime import date
from app.database.schemas import payload
from app.database.database import get_db
from app.database.schemas.section import CreateSectionDto
from app.database.cruds.section import create_new_section,list_all_sections,get_section_by_level, remove_section
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from app.database.cruds.auth import get_current_user
user_dependency = Annotated[dict,Depends(get_current_user)]
section_router = APIRouter()


@section_router.post("/sections/")
async def add_new_section(sec:CreateSectionDto,db:AsyncSession=Depends(get_db)):
    return payload.BaseResponse(
        date=date.today(),
        status=int(status.HTTP_201_CREATED),
        payload=await create_new_section(sec, db),
        message= "Section created successfully 😉"
    )

@section_router.get("/sections")
async def get_all_sections(db:AsyncSession=Depends(get_db)):
    return payload.BaseResponse(
        date=date.today(),
        status=int(status.HTTP_200_OK),
        payload= await list_all_sections(db),
        message= "Sections have been retrieved."
    )


@section_router.delete("/sections/{id}")
async def delete_section(id:str,db:AsyncSession=Depends(get_db)):
    return payload.BaseResponse(
        date=date.today(),
        status=int(status.HTTP_204_NO_CONTENT),
        payload= await remove_section(id, db),
        message=f"Section deleted successfully"
    )

@section_router.get("/sections/{level}")
async def find_section_by_level(level:str, db:AsyncSession=Depends(get_db)):
    return payload.BaseResponse(
        date=date.today(),
        status=int(status.HTTP_200_OK),
        payload= await get_section_by_level(level, db),
        message= "Section has been found."
    )