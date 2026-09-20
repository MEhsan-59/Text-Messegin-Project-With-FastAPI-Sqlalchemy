from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
import models, schemas

class TextRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: str):
        return self.db.query(models.Account).filter(models.Account.user_id == user_id).first()

    def create_account(self, account: schemas.AccountCreate, hashed_password: str):
        db_account = models.Account(user_id=account.user_id, hashed_password=hashed_password)
        self.db.add(db_account)
        self.db.commit()
        self.db.refresh(db_account)
        return db_account

    def create_message(self, sender_id: str, message: schemas.MessageCreate):
        db_message = models.Message(
            sender_id=sender_id,
            receiver_id=message.receiver_id,
            content=message.content
        )
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return db_message

    def get_unread_grouped(self, receiver_id: str):
        return self.db.query(
            models.Message.sender_id,
            func.count(models.Message.id).label('count')
        ).filter(
            models.Message.receiver_id == receiver_id,
            models.Message.is_read == False
        ).group_by(models.Message.sender_id).all()

    def get_conversation(self, user1_id: str, user2_id: str):
        messages = self.db.query(models.Message).filter(
            or_(
                and_(models.Message.sender_id == user1_id, models.Message.receiver_id == user2_id),
                and_(models.Message.sender_id == user2_id, models.Message.receiver_id == user1_id)
            )
        ).order_by(models.Message.timestamp).all()
        
        unread = [m for m in messages if m.receiver_id == user1_id and not m.is_read]
        for m in unread:
            m.is_read = True
        if unread:
            self.db.commit()
            
        return messages

    def delete_message(self, message_id: int):
        message = self.db.query(models.Message).filter(models.Message.id == message_id).first()
        
        if message:
            self.db.delete(message) 
            self.db.commit()        
            return True
        return False 