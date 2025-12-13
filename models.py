# models.py
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    role: str = Field(default='basic')
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DeviceToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    token: str
    platform: Optional[str] = Field(default='android')
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Pedido(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uid: str = Field(index=True, unique=True)
    nit: Optional[str] = None
    fundacion: Optional[str] = None
    total: float = 0.0
    peaje: float = 0.0
    trans: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[int] = Field(default=None, foreign_key="user.id")

