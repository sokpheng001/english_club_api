from sqlalchemy import Column, ForeignKey, Integer, String, Boolean,Date, ARRAY, JSON
from app.database.database import Base
from sqlalchemy.orm import relationship


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True,nullable=False, index=True)
    q_uuid = Column(String, nullable=False, unique=True)
    text = Column(String, index=True)
    voice = Column(String,nullable=True)
    video = Column(String,nullable=True)
    image = Column(String, nullable=True)
    type = Column(String,nullable=False)  # e.g., "multiple-choice", "fill-in-the-blank", "true-false"
    correct_answer = Column(JSON,nullable=False) 
    question_level = Column(String, nullable=False)

    #relationsip
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=True)
    exercise = relationship("Exercise",back_populates="questions")
    choices = relationship("Choice",back_populates="question")

    def __init__(self, q_uuid=None, text=None, voice=None, video=None, image=None, type=None, correct_answer=None, exercise_id = None, question_level=None):
        self.q_uuid = q_uuid
        self.text = text
        self.voice = voice
        self.video = video
        self.image = image
        self.type = type
        self.correct_answer = correct_answer
        self.exercise_id = exercise_id
        self.question_level = question_level
