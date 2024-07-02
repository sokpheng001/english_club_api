from fastapi import FastAPI
from app.routers import user, lesson, exercise, question, skill, file, auth, section,grammer, vocabulary
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import Base, engine

app = FastAPI()


# # 
# app.mount("/static", StaticFiles(directory="static"), name="static")
# Include routers
app.include_router(auth.auth_router)
app.include_router(file.file_router)
app.include_router(user.user_router)
app.include_router(question.question_router)
app.include_router(exercise.exercise_router)
app.include_router(skill.skill_router)
app.include_router(section.section_router)
app.include_router(lesson.lesson_router)
app.include_router(grammer.grammar_router)
app.include_router(vocabulary.vocabulary_router)


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

# Create tables during application startup if they don't exist
@app.on_event("startup")
async def startup():
    await startup_event()

import uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=4000, reload=True)
