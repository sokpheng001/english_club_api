from fastapi import FastAPI
from app.routers import user, lesson,exercise, question,skill
from app.database.database import Base, engine
from sqlalchemy import create_engine, inspect

app = FastAPI()

# Include routers

app.include_router(user.user_router)
app.include_router(question.question_router)
app.include_router(exercise.exercise_router)
app.include_router(skill.skill_router)
app.include_router(lesson.lesson_router)



# Function to create tables if they do not exist
async def create_tables_if_not_exists():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Example of starting up your application
async def startup_event():
    await create_tables_if_not_exists()
#Create tables during application startup if they don't exist

@app.on_event("startup")
async def startup():
    await startup_event()


import uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000,reload=True)