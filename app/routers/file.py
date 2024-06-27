from fastapi import APIRouter, HTTPException, Depends,UploadFile,File
from fastapi.responses import FileResponse
import os
from app.database.cruds.file import upload_multiple_files

file_router = APIRouter()


@file_router.post("/files/upload")
async def upload_files(files:list[UploadFile]=File(...)):
    return await upload_multiple_files(files)

@file_router.get("/files/{filename}")
async def get_file(filename: str):
    file_path = os.path.join("./uploads/", filename)
    return FileResponse(path=file_path, filename=filename)