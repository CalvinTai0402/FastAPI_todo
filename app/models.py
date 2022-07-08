from typing import List, Optional
from sqlalchemy import Column, String
from sqlalchemy.sql.sqltypes import TIMESTAMP
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel
# from .database import Base

# class Task(Base):
#     __tablename__ = "tasks"
#     id = Column(Integer, primary_key=True, nullable=False)
#     description = Column(String, nullable=False)
#     created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
#     owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
#     owner = relationship("User")
#     tags = relationship("Tag", secondary="task_tags", back_populates='tasks')

# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, nullable=False)
#     email = Column(String, nullable=False, unique=True)
#     password = Column(String, nullable=False)
#     created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
# class Tag(Base):
#     __tablename__ = "tags"
#     id = Column(Integer, primary_key=True, nullable=False)
#     description = Column(String, nullable=False)
#     created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
#     owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
#     owner = relationship("User")
#     tasks = relationship("Task", secondary="task_tags", back_populates='tags')

# class TaskTags(Base):
#     __tablename__ = 'task_tags'
#     task_id = Column(ForeignKey('tasks.id'), primary_key=True)
#     tag_id = Column(ForeignKey('tags.id'), primary_key=True)

class TaskTagLink(SQLModel, table=True):
    task_id: Optional[int] = Field(default=None, foreign_key="task.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)
    
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    email: str = Field(sa_column=Column("email", String, unique=True, nullable=False))
    password: str = Field(nullable=False)
    created_at: datetime = Field(default=datetime.utcnow(), nullable=False)
    tasks: Optional[List["Task"]] = Relationship(back_populates="owner")
    tags: Optional[List["Tag"]] = Relationship(back_populates="owner")

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    description: str = Field(nullable=False)
    owner_id: Optional[int] = Field(nullable=False,  foreign_key="user.id")
    created_at: datetime = Field(default=datetime.utcnow(), nullable=False)
    owner: User = Relationship(back_populates="tasks")
    tags: Optional[List["Tag"]] = Relationship(back_populates="tasks", link_model=TaskTagLink)
    
class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    description: str = Field(nullable=False)
    created_at: datetime = Field(default=datetime.utcnow(), nullable=False)
    owner_id: Optional[int] = Field(nullable=False,  foreign_key="user.id")
    owner: User = Relationship(back_populates="tags")
    tasks: Optional[List["Task"]] = Relationship(back_populates="tags", link_model=TaskTagLink)
    

