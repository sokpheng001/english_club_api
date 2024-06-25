from sqlalchemy import Column, Integer, String, Boolean
from app.database.database import Base

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

    def __init__(self, uuid=None, user_name=None, email=None, password=None, profile=None, bio=None,is_deleted=False):
        self.uuid = uuid
        self.user_name = user_name
        self.email = email
        self.password =  password
        self.profile = profile
        self.bio = bio
        self.is_deleted = is_deleted
