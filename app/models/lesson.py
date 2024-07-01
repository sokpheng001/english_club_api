from app.database.database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.section import Section
from app.models.vocabulary import Vocabulary
from app.models.grammar import Grammar

class Lesson(Base):
    __tablename__= "lessons"
    
    id = Column(Integer, primary_key=True,nullable=False,unique=True)
    lesson_uuid = Column(String, nullable=False)
    name = Column(String, unique=True)
    description = Column(String, nullable=False)
    thumbnail = Column(String, nullable=True)
    lesson_level = Column(String, nullable=False)
    is_deleted = Column(Boolean, default=False)
    # relationship
    sections = relationship("Section",back_populates="lesson")
    
    grammar_id = Column(Integer, ForeignKey("grammars.id"))
    grammar = relationship("Grammar", back_populates="lessons")
    
    vocabulary_id = Column(Integer, ForeignKey("vocabularies.id"))
    vocabulary = relationship("Vocabulary", back_populates="lessons")

    def __init__(self,lesson_uuid, name=None, description=None, thumbnail=None, lesson_level = None, is_deleted=False ):
        self.lesson_uuid = lesson_uuid
        self.name = name
        self.description = description
        self.thumbnail = thumbnail
        self.lesson_level = lesson_level
        self.is_deleted = is_deleted

