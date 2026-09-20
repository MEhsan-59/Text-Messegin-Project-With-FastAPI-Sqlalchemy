from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from database import Base
from datetime import datetime
from pydantic import BaseModel, Field

class AccountCreate(BaseModel):
    username: str
    # Restrict the password to a maximum of 72 characters
    password: str = Field(..., max_length=72)

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    @property
    def username(self):
        return self.user_id

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(String, ForeignKey("accounts.user_id"), nullable=False)
    receiver_id = Column(String, ForeignKey("accounts.user_id"), nullable=False)
    content = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)