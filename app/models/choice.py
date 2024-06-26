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

    def __init__(self, choice_uuid, choice_text, is_correct, question_id):
        self.choice_uuid = choice_uuid
        self.choice_text = choice_text
        self.is_correct = is_correct
        self.question_id = question_id