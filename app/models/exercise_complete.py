from sqlalchemy import Column, ForeignKey, Integer,Date, DECIMAL, String
from app.database.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship


class ExerciseComplete(Base):
    __tablename__ = "exercises_completes"
    
    id = Column(Integer, primary_key=True,nullable=False, index=True)
    ex_complete_uuid = Column(String(255), nullable=False, index=True)
    complete_date = Column(Date, nullable=False, default=datetime.utcnow)
    score = Column(DECIMAL, index=True, nullable=False)
    complete_level = Column(String, index=True, nullable=False)
    #  relationship
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    exercise = relationship("Exercise", back_populates="exercise_completes")
    # 
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="exercise_completes")

    def __init__(self, ex_complete_uuid,score, complete_level,exercise_id, user_id=None):
        self.ex_complete_uuid = ex_complete_uuid
        self.score = score
        self.exercise_id = exercise_id
        self.user_id = user_id
        self.complete_level = complete_level