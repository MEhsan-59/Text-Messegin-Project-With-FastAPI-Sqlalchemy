from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError
import models, schemas
from database import Database, engine
from text_repository import TextRepository
from text_manager import TextManager
from security import SecurityHandler
from database import get_db


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Text Messaging API - OOP Edition")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
security_handler = SecurityHandler()

def get_repository(db: Session = Depends(get_db)) -> TextRepository:
    return TextRepository(db)

def get_manager(repo: TextRepository = Depends(get_repository)) -> TextManager:
    return TextManager(repo)

def get_current_user(token: str = Depends(oauth2_scheme), manager: TextManager = Depends(get_manager)):
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id = security_handler.decode_token(token)
        if user_id is None:
            raise exception
    except JWTError:
        raise exception
    
    user = manager.repo.get_user_by_id(user_id)
    if user is None:
        raise exception
    return user



@app.post("/accounts", response_model=schemas.AccountResponse)
def create_account(account: schemas.AccountCreate, manager: TextManager = Depends(get_manager)):
    return manager.register_user(account)

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), manager: TextManager = Depends(get_manager)):
    user = manager.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    access_token = security_handler.create_access_token(data={"sub": user.user_id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/messages", response_model=schemas.MessageResponse)
def send_message(message: schemas.MessageCreate, manager: TextManager = Depends(get_manager), current_user = Depends(get_current_user)):
    return manager.send_message(current_user.user_id, message)

@app.get("/messages/unread", response_model=list[schemas.UnreadCount])
def get_unread_messages(manager: TextManager = Depends(get_manager), current_user = Depends(get_current_user)):
    return manager.get_unread(current_user.user_id)

@app.get("/messages/conversation/{peer}", response_model=list[schemas.MessageResponse])
def get_conversation(peer: str, manager: TextManager = Depends(get_manager), current_user = Depends(get_current_user)):
    return manager.get_chat(current_user.user_id, peer)

@app.delete("/messages/{message_id}")
def delete_message(message_id: int, manager: TextManager = Depends(get_manager)):
    success = manager.delete_message(message_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
        
    return {"message": "Message deleted successfully!"}