from fastapi import FastAPI
from app.routers import user, lesson


app = FastAPI()

# Include routers

app.include_router(user.user_router)

app.include_router(lesson.lesson_router)

import uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000,reload=True)