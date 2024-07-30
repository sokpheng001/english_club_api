from fastapi import APIRouter, Depends, status
from app.database.database import get_db
from app.database.cruds.submit_answer import answer_submission,get_submit_exercise_on_user_uuid,get_submit_exercise_on_user_uuid_and_level,try_again_submit_exercise
from app.database.schemas import submit_answer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.schemas import payload
from datetime import date
from typing import Annotated
from app.database.cruds.auth import get_current_user

submit_answer_router = APIRouter()
user_dependency = Annotated[dict,Depends(get_current_user)]

@submit_answer_router.post("/exercise/{exercise_id}/submit_answer")
async def create_submit_answer(exercise_id:str,answer:submit_answer.SubmitAnswerDto, session: AsyncSession=Depends(get_db)):
    return payload.BaseResponse(
        date=date.today(),
        status=status.HTTP_200_OK,
        payload= await answer_submission(exercise_id,answer, session),
        message="Answer has been submitted successfully"
    )


@submit_answer_router.get("/exercise/submit_answer/user")
async def find_submit_exercise_by_user_uuid(id:str, authen:user_dependency,db:AsyncSession=Depends(get_db)):
    return payload.BaseResponse(
        date=date.today(),
        status=status.HTTP_200_OK,
        payload=await get_submit_exercise_on_user_uuid(id, db),
        message="List all submit exercises successfully"
    )


@submit_answer_router.get("/exercise/submit_answer/userId={uid}/level={level}")
async def find_submit_exercise_by_uuid_and_level(uid:str,level:str, authen:user_dependency,db:AsyncSession=Depends(get_db)):    
    return payload.BaseResponse(
        date=date.today(),
        status=status.HTTP_200_OK,
        payload=await get_submit_exercise_on_user_uuid_and_level(uid,level, db),
        message= f"List all submit exercises by user {uid} at level {level}"
    )

from pydantic import BaseModel
from typing import List, Optional

class Ex_UUIDs(BaseModel):
    user_uuid:str
    exercises_uuids:Optional[list[str]] = ["exercise_uuid","exercise_uuid"]

@submit_answer_router.put("/exercise/submit_answer/try_again")
async def try_again_submit_answer(re_submit:Ex_UUIDs ,db:AsyncSession=Depends(get_db)):
    return payload.BaseResponse(
        date=date.today(),
        status=status.HTTP_200_OK,
        payload=await try_again_submit_exercise(re_submit,db),
        message="User can try the question again again"
    )