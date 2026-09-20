from fastapi import HTTPException, status
import schemas
from text_repository import TextRepository
from security import SecurityHandler

class TextManager:
    def __init__(self, repo: TextRepository):
        self.repo = repo
        self.security = SecurityHandler()

    def register_user(self, account: schemas.AccountCreate):
        if self.repo.get_user_by_id(account.user_id):
            raise HTTPException(status_code=400, detail="User already registered")
        hashed_pw = self.security.get_password_hash(account.password)
        return self.repo.create_account(account, hashed_pw)

    def authenticate_user(self, user_id: str, password: str):
        user = self.repo.get_user_by_id(user_id)
        if not user or not self.security.verify_password(password, user.hashed_password):
            return False
        return user

    def send_message(self, sender_id: str, message: schemas.MessageCreate):
        if not self.repo.get_user_by_id(message.receiver_id):
            raise HTTPException(status_code=404, detail="Receiver not found")
        return self.repo.create_message(sender_id, message)

    def get_unread(self, user_id: str):
        results = self.repo.get_unread_grouped(user_id)
        return [{"sender_id": r.sender_id, "count": r.count} for r in results]

    def get_chat(self, current_user_id: str, peer_id: str):
        return self.repo.get_conversation(current_user_id, peer_id)

    def delete_message(self, message_id: int):
        return self.repo.delete_message(message_id)