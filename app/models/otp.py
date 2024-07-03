from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
from app.database.database import Base

class OTPModel(Base):

    __tablename__ = 'otps'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    otp = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_used = Column(Boolean, default=False)

    def __init__(self, otp, email, expires_at=None):
        self.otp = otp
        self.email = email
        self.expires_at = expires_at