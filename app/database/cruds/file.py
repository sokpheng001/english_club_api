from psycopg2 import Date

from fastapi import HTTPException, status, File,UploadFile
from datetime import date
import os
import uuid
UPLOAD_DIRECTORY = "./uploads/"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

async def upload_multiple_files(files:list[UploadFile]=File(...)):
    file_urls = []
    for file in files:
        file_extension =os.path.splitext(file.filename)[-1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_location = os.path.join(UPLOAD_DIRECTORY, unique_filename)

        with open(file_location,"wb") as f:
            f.write(await file.read())
        file_url = f"/upload/{unique_filename}"
        file_urls.append(file_url)
        
    return {"file_urls": file_urls}
