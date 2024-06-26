from fastapi import APIRouter, HTTPException, Depends
from app.database.schemas import question
from app.database.database import get_db
from app.database.cruds.question import add_question, list_all_questions
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