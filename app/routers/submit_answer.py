from fastapi import APIRouter, Depends, status
from app.database.database import get_db
from app.database.cruds.submit_answer import answer_submission
from app.database.schemas import submit_answer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.schemas import payload
from datetime import date

submit_answer_router = APIRouter()

@submit_answer_router.post("/exercise/{exercise_id}/submit_answer")
async def create_submit_answer(exercise_id:str,answer:submit_answer.SubmitAnswerDto, session: AsyncSession=Depends(get_db)):
    return payload.BaseResponse(
        date=date.today(),
        status=status.HTTP_200_OK,
        payload= await answer_submission(exercise_id,answer, session),
        message="Answer has been submitted successfully"
    )