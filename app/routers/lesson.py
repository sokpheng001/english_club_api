from fastapi import APIRouter, HTTPException

lesson_router = APIRouter()


@lesson_router.get("/lessons/")
async def lesson_home() -> dict[str, str]:
    return {"message": "Hello Lesson"}

