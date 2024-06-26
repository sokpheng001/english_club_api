from sqlalchemy import Column, ForeignKey, Integer, String, Boolean,Date
from app.database.database import Base
from sqlalchemy.orm import relationship


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True,nullable=False, index=True)
    q_uuid = Column(String, nullable=False, unique=True)
    text = Column(String, index=True)
    voice = Column(String,nullable=True)
    video = Column(String,nullable=True)
    type = Column(String,nullable=False)  # e.g., "multiple-choice", "fill-in-the-blank", "true-false"
    correct_answer = Column(String,nullable=False) 

    #relationsip
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    # exercise = relationship("Exercise",back_populates="")
    choices = relationship("Choice",back_populates="question")
