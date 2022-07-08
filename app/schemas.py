from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# Auth
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Base
class UserBase(BaseModel):
    class Config:
        orm_mode = True

class TaskBase(BaseModel):
    description: str
    class Config:
        orm_mode = True
    
class TagBase(BaseModel):
    description: str
    class Config:
        orm_mode = True
        
# Res
class UserRes(UserBase):
    id: int
    email: EmailStr
    created_at: datetime

class TaskRes(TaskBase):
    id: int
    created_at: datetime
    owner: UserRes
    owner_id: int
    tags: List[TagBase]
        
class TagRes(TagBase):
    id: int
    created_at: datetime
    owner: UserRes
    owner_id: int
    tasks: List[TaskRes]

#Req
class TaskCreate(TaskBase):
    owner: Optional[UserRes]
    pass

class TagCreate(TagBase):
    owner: Optional[UserRes]
    pass

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None