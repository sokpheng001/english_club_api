from psycopg2 import Date

from fastapi import HTTPException, status, File,UploadFile
from app.database.schemas.file import FileResponse
from datetime import date
import os
import uuid
from config import settings



UPLOAD_DIRECTORY = "/uploads/"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

async def upload_multiple_files(files:list[UploadFile]=File(...)):
    file_urls:FileResponse = []
    for file in files:
        file_extension =os.path.splitext(file.filename)[-1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_location = os.path.join(UPLOAD_DIRECTORY, unique_filename)
        with open(file_location,"wb") as f:
            f.write(await file.read())
        file_urls.append(FileResponse(
            file_name=unique_filename,
            file_path=f"{settings.FILE_SERVER}/{unique_filename}",
            file_size=file.size,
        ))
        
    return {"file_urls": file_urls}
