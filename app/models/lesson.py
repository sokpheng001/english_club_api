from sqlalchemy import Column, Integer, String, Boolean
from database.database import Base

class Lesson(Base):
    __tablename__= "lessons"
    
    id = Column(int, primary_key=True,nullable=False,unique=True)
    name = Column(String, unique=True)
    description = Column(String, nullable=False)
    thumbnail = Column(String, nullable=True)
    lesson_level = Column(String, nullable=False)
    is_deleted = Column(Boolean, default=False)

    def __init__(self, name=None, description=None, thumbnail=None, lesson = None, is_deleted=False ):
        self.name = name
        self.description = description
        self.thumbnail = thumbnail
        self.lesson_level = lesson
        self.is_deleted = is_deleted

