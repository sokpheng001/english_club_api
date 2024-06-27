from fastapi import APIRouter, HTTPException, Depends
from app.database.schemas import question
from app.database.database import get_db
from app.database.cruds.question import add_question, list_all_questions, delete_question_by_uuid,get_question_by_uuid
from sqlalchemy.ext.asyncio import AsyncSession
question_router = APIRouter()


@question_router.post("/questions/")

async def create_question(q:question.CreateQuestionDto, db:AsyncSession=Depends(get_db)):
    q = await add_question(q, db)
    return q

@question_router.get("/questions/")
async def get_all_questions(db:AsyncSession=Depends(get_db)):
    data = await list_all_questions(db)
    return data

@question_router.delete("/questions/{id}")
async def delete_question(id:str,db:AsyncSession=Depends(get_db)):
    re = await delete_question_by_uuid(id,db)
    return re

@question_router.get("/questions/{id}")
async def find_question(id:str,db:AsyncSession=Depends(get_db)):
    re = await get_question_by_uuid(id,db)
    return re