from sqlalchemy import Column, Integer, String, Boolean,Date
from app.database.database import Base
from app.models.exercise import Exercise
from sqlalchemy.orm import relationship

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True,nullable=False, index=True)
    skill_uuid = Column(String, nullable= False,unique=True)
    skill_name = Column(String, nullable=False)
    thumbnail = Column(String, nullable=True)
    description = Column(String, nullable=True)
    skill_level = Column(String, nullable = False)
    is_deleted = Column(Boolean, default=False)
    # exercise 
    exercises = relationship("Exercise",back_populates="skill")

    def __init__(self, skill_name=None, thumbnail=None, description=None, skill_level=None, is_deleted=False):
        self.skill_name = skill_name
        self.thumbnail = thumbnail
        self.description = description
        self.skill_level = skill_level