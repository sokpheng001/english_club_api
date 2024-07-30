from app.database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship


class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True,nullable=False, index=True)
    section_uuid = Column(String, unique=True, nullable=False)
    section_name = Column(String, unique=True,nullable=False)
    voice = Column(JSON, unique=True, nullable=True)
    thumbnail = Column(String, nullable=True)
    description = Column(String, nullable=True)
    examples = Column(JSON, nullable=True)
    section_level = Column(String, nullable=False)
    # relationship
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=True)
    lesson = relationship("Lesson", back_populates="sections")

    def __init__(self, section_uuid=None, section_name=None, voice=None ,thumbnail=None, description=None, section_level=None, examples=None):
        self.section_uuid = section_uuid
        self.section_name = section_name
        self.voice = voice
        self.thumbnail = thumbnail
        self.description = description
        self.section_level = section_level
        self.examples = examples
