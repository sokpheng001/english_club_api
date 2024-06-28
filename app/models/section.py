from app.database.database import Base
from sqlalchemy import Column, Integer, String, Boolean,Date, ForeignKey, JSON
from sqlalchemy.orm import Relationship

class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True,nullable=False, index=True)
    section_uuid = Column(String, unique=True, nullable=False)
    section_name = Column(String, nullable=False)
    thumbnail = Column(String, nullable=True)
    description = Column(String, nullable=True)
    example = Column(JSON, nullable=True)
    section_level = Column(String, nullable=False)
    # relationship
    lesson_id = Column(Integer, ForeignKey("lesson_id"), nullable=True)
    lesson = Relationship("Lesson", back_populates="sections")

    def __init__(self, section_uuid=None, section_name=None, thumbnail=None, description=None, section_level=None):
        self.section_uuid = section_uuid
        self.section_name = section_name
        self.thumbnail = thumbnail
        self.description = description
        self.section_level = section_level
