from fastapi import APIRouter,UploadFile,File, status
import os
from app.database.cruds.submit_answer import submit_answer
from app.database.schemas import payload



submit_answer_router = APIRouter()

@submit_answer_router.post("/submit_answer/")
async def create_submit_answer():
    await submit_answer()