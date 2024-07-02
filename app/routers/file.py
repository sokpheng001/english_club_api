from fastapi import APIRouter,UploadFile,File, status
import os
from app.database.cruds.file import upload_multiple_files
from app.database.schemas import payload
from datetime import date
from dotenv import load_dotenv


file_router = APIRouter()



@file_router.post("/files")
async def upload_files(files:list[UploadFile]=File(...)):
    return payload.BaseResponse(
        date=date.today(),
        status=status.HTTP_200_OK,
        payload=await upload_multiple_files(files),
        message="Files uploaded successfully 😉"
    )

