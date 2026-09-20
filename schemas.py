from pydantic import BaseModel
from datetime import datetime

from pydantic import BaseModel

# You already have this one for the input:
class AccountCreate(BaseModel):
    username: str
    password: str

    @property
    def user_id(self) -> str:
        return self.username

# ADD THIS ONE for the output:
class AccountResponse(BaseModel):
    id: int      # Assuming your DB gives them an ID
    username: str
    
    # Notice: No password field here!

    class Config:
        from_attributes = True  # Tells Pydantic to read data from a SQLAlchemy model
class Token(BaseModel):
    access_token: str
    token_type: str

class MessageCreate(BaseModel):
    receiver_id: str
    content: str

class MessageResponse(BaseModel):
    id: int
    sender_id: str
    receiver_id: str
    content: str
    is_read: bool
    timestamp: datetime

    class Config:
        from_attributes = True

class UnreadCount(BaseModel):
    sender_id: str
    count: int