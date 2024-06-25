from sqlalchemy import Column, Integer, String, Boolean
from database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True,nullable=False, index=True)
    uuid = Column(String, nullable=False)
    user_name = Column(String,nullable=False ,index=True)
    email = Column(String, unique=True, nullable=False,index=True)
    password = Column(String, unique=False,nullable=False)
    profile = Column(String,nullable=True )
    bio = Column(String(255),nullable=True)

    is_deleted = Column(Boolean, default=False)
