import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from pwdlib import PasswordHash

class SecurityHandler:  # <--- Renamed this to match your import
    def __init__(self):
        # Initialize pwdlib with bcrypt
        self.pwd_context = PasswordHash.recommended()
        self.secret_key = os.getenv("SECRET_KEY", "development-secret-key-change-me")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict) -> str:
        payload = data.copy()
        payload["exp"] = datetime.now(timezone.utc) + timedelta(
            minutes=self.access_token_expire_minutes
        )
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> str | None:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload.get("sub")
        except JWTError:
            return None