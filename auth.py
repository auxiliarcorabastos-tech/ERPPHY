
import os
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import select
from db import get_async_session
from models import User

router = APIRouter()

SECRET_KEY = os.environ.get('SECRET_KEY','change_this_secret')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*7  # 7 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Token(BaseModel):
    access_token: str
    token_type: str

class UserIn(BaseModel):
    username: str
    password: str

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post('/register')
async def register(u: UserIn):
    async with get_async_session() as session: 
        q = await session.exec(select(User).where(User.username == u.username))
        existing = q.first()
        if existing:
            raise HTTPException(status_code=400, detail='User already exists')
        user = User(username=u.username, hashed_password=get_password_hash(u.password), role='admin' if u.username=='admin' else 'basic')
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return {'ok': True, 'username': user.username}

@router.post('/login', response_model=Token)
async def login(u: UserIn):
    async with get_async_session() as session:
        q = await session.exec(select(User).where(User.username == u.username))
        user = q.first()
        if not user or not verify_password(u.password, user.hashed_password):
            raise HTTPException(status_code=401, detail='Invalid credentials')
        token = create_access_token({'sub': user.username, 'role': user.role})
        return {'access_token': token, 'token_type':'bearer'}
