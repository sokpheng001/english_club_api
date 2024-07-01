from fastapi import APIRouter, HTTPException, Depends,UploadFile,File
from fastapi.responses import FileResponse
import os
from app.database.cruds.file import upload_multiple_files
from app.database.schemas import payload
import mimetypes

file_router = APIRouter()

@file_router.post("/files/upload")
async def upload_files(files:list[UploadFile]=File(...)):
    return await upload_multiple_files(files)

@file_router.get("/files/{filename}")
async def get_file(filename: str):
    file_path = os.path.join("./uploads/", filename)
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    content_type = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = 'application/octet-stream'
    return FileResponse(path=file_path, media_type=content_type)