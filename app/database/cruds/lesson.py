
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.schemas.lesson import CreateLessonDto
from app.models.lesson import Lesson
import uuid

async def create_new_lessons(less:CreateLessonDto, session: AsyncSession):
    new_lesson = Lesson(name=less.name, description=less.description,thumbnail=less.thumbnail,lesson_level="A1",is_deleted=False)
    session.add(new_lesson)
    await session.commit()
    await session.refresh(new_lesson)