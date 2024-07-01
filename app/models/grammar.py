from app.database.database import Base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship


class Grammar(Base):
    __tablename__= "grammars"
    
    id = Column(Integer, primary_key=True,nullable=False,unique=True)
    grammar_uuid = Column(String, nullable=False,unique=True)
    grammar_name = Column(String, unique=True)
    description = Column(String, nullable=False)
    thumbnail = Column(String, nullable=True)
    grammar_level = Column(String)
    # relationship
    lessons = relationship("Lesson" ,back_populates="grammar")

    def __init__(self, grammar_uuid=None, grammar_name=None, description=None, thumbnail=None, grammar_level=None):
        self.grammar_uuid = grammar_uuid
        self.grammar_name = grammar_name
        self.description = description
        self.thumbnail = thumbnail
        self.grammar_level = grammar_level
