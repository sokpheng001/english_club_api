from sqlalchemy import Column, ForeignKey, Integer, String, Boolean,Date
from app.database.database import Base
from sqlalchemy.orm import relationship
from app.models.skill import Skill

class Exercise(Base):
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True,nullable=False, index=True)
    ex_uuid = Column(String,unique=True)
    title = Column(String, nullable=False)
    thumbnail = Column(String, nullable=True)
    description = Column(String, nullable=True)
    #
    skill_id = Column(Integer, ForeignKey("skills.id"))
    # skill = relationship("Skill",back_populates="exercises")
    questions = relationship("Question",back_populates="exercise")

    def __init__(self, title=None, thumbnail=None, description=None, skill_id=None):
        self.title = title
        self.thumbnail = thumbnail
        self.description = description
        self.skill_id = skill_id