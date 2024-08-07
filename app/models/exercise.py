from sqlalchemy import Column, ForeignKey, Integer, String, Boolean,Date,JSON
from app.database.database import Base
from sqlalchemy.orm import relationship
from app.models.skill import Skill
from app.models.exercise_complete import ExerciseComplete

class Exercise(Base):
    __tablename__ = "exercises"
    
    id = Column(Integer, primary_key=True,nullable=False, index=True)
    ex_uuid = Column(String,unique=True)
    title = Column(String, nullable=False)
    thumbnail = Column(String, nullable=True)
    description = Column(String, nullable=True)
    tip = Column(String, nullable=True)
    reading_text = Column(String(1000), nullable=True)
    voice = Column(String, nullable=True)
    transcript = Column(String(1000), nullable=True)
    exercise_level = Column(String, nullable=False)
    #
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True)
    skill = relationship("Skill",back_populates="exercises")
    questions = relationship("Question",back_populates="exercise")
    # 
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=True)
    lesson = relationship("Lesson",back_populates="exercises")
    # 
    exercise_completes = relationship("ExerciseComplete",back_populates="exercise")

    def __init__(self,uuid ,title=None, thumbnail=None, description=None,tip=None,reading_text=None,voice=None,transcript=None, skill_id=None, exercise_level=None):
        self.ex_uuid = uuid
        self.title = title
        self.thumbnail = thumbnail
        self.description = description
        self.skill_id = skill_id
        self.exercise_level = exercise_level
        self.tip = tip
        # add new
        self.reading_text = reading_text
        self.voice = voice
        self.transcript = transcript
