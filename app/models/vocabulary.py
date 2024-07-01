from app.database.database import Base
from sqlalchemy import Column, Integer, String, Boolean
from app.database.database import Base
from sqlalchemy.orm import relationship



class Vocabulary(Base):
    __tablename__ = "vocabularies"

    id = Column(Integer, primary_key=True,nullable=False,unique=True)
    vocab_uuid = Column(String, unique=True, nullable=False)
    vocab_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    thumbnail = Column(String, nullable=True)
    vocabulary_level = Column(String, nullable=True)
    # relationship
    lessons = relationship("Lesson", back_populates="vocabulary")

    def __init__(self, vocab_uuid, vocabulary_name, description, thumbnail, vocabulary_level=None):
        self.vocab_uuid = vocab_uuid
        self.vocab_name = vocabulary_name
        self.description = description
        self.thumbnail = thumbnail
        self.vocabulary_level = vocabulary_level