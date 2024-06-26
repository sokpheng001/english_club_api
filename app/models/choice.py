from sqlalchemy import Column, ForeignKey, Integer, String, Boolean,Date
from app.database.database import Base
from sqlalchemy.orm import relationship

class Choice(Base):
    __tablename__ = "choices"

    id = Column(Integer, primary_key=True,nullable=False, index=True)
    choice_uuid = Column(String, unique=True, nullable=False)
    choice_text = Column(String, nullable=False)
    is_correct = Column(Boolean,nullable=False)

    # relationship
    question_id = Column(Integer, ForeignKey("questions.id"))
    question = relationship("Question", back_populates="choices")