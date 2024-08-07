from fastapi import FastAPI
from app.routers import user, lesson, exercise, question, skill, file, auth, section,grammer, vocabulary, submit_answer
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import Base, engine
import os

app = FastAPI(title="CSTAD - English Club API")




# mount file for preview
app.mount("/files", StaticFiles(directory="/uploads"), name="uploads")

# # 
# app.mount("/static", StaticFiles(directory="static"), name="static")
# Include routers
app.include_router(auth.auth_router, tags=["Authentication"])
app.include_router(file.file_router, tags=["File"])
app.include_router(user.user_router, tags=["User"])
app.include_router(question.question_router,tags=["Question"])
app.include_router(exercise.exercise_router,tags=["Exercise"])
app.include_router(skill.skill_router,tags=["Skill"])
app.include_router(section.section_router, tags=["Section"])
app.include_router(lesson.lesson_router,tags=["Lesson"])
app.include_router(grammer.grammar_router,tags=["Grammar"])
app.include_router(vocabulary.vocabulary_router,tags=["Vocabulary"])
app.include_router(submit_answer.submit_answer_router, tags=["Submit Answer"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Function to create tables if they do not exist
async def create_tables_if_not_exists():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Example of starting up your application
async def startup_event():
    await create_tables_if_not_exists()


from config import settings

# Create tables during application startup if they don't exist
@app.on_event("startup")
async def startup():
    print(f"HOST: {settings.HOST}")
    await startup_event()

import uvicorn
from datetime import datetime
if __name__ == "__main__":
    
    uvicorn.run("main:app", host=f"{settings.HOST}", port=int(settings.PORT), reload=True)
