from fastapi import Response, status, HTTPException, Depends, APIRouter
from typing import List, Optional
from fastapi_jwt_auth import AuthJWT
from .. import models, schemas
from ..database import get_db
from sqlmodel import Session, select


router = APIRouter(
    prefix="/tasks",
    tags=['Tasks']
)

@router.get("/", response_model=List[schemas.TaskRes])
def get_tasks(db: Session = Depends(get_db), Authorize: AuthJWT = Depends(), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    Authorize.jwt_required()
    statement = select(models.Task).where(models.Task.description.contains(search)).where(models.Task.owner_id==Authorize.get_jwt_subject()).offset(skip).limit(limit)
    results = db.exec(statement)
    tasks = results.all()
    return tasks

@router.get("/with_tag")
def get_tasks_of_tag(tag_description: str = "", db: Session = Depends(get_db), Authorize: AuthJWT = Depends(), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    Authorize.jwt_required()
    statement = select(models.Tag, models.Task).where(models.Tag.description==tag_description).where(models.Task.owner_id==Authorize.get_jwt_subject())\
                .where(models.Tag.owner_id==Authorize.get_jwt_subject()).offset(skip).limit(limit)
    results = db.exec(statement)
    tasks = results.all()
    return tasks

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_task(task: schemas.TaskCreate, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    current_user = db.exec(select(models.User).where(models.User.id == Authorize.get_jwt_subject())).first()
    new_task = models.Task(owner_id=Authorize.get_jwt_subject(), **task.dict())
    new_task.owner = current_user
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/{id}")
def get_task(id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    statement = select(models.Task).where(models.Task.id == id)
    results = db.exec(statement)
    task = results.first()
    if task == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"task with id: {id} was not found")
    if task.owner_id != Authorize.get_jwt_subject():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    return task

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    statement = select(models.Task).where(models.Task.id == id)
    results = db.exec(statement)
    task = results.first()
    if task == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"task with id: {id} does not exist")
    if task.owner_id != Authorize.get_jwt_subject():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    db.delete(task)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}")
def update_task(id: int, updated_task: schemas.TaskCreate, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    statement = select(models.Task).where(models.Task.id == id)
    results = db.exec(statement)
    task = results.first()
    if task == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"task with id: {id} does not exist")
    if task.owner_id != Authorize.get_jwt_subject():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    updated_task_data = updated_task.dict(exclude_unset=True)
    for key, value in updated_task_data.items():
        setattr(task, key, value)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.post("/attach/{task_id}/{tag_id}", status_code=status.HTTP_201_CREATED, response_model=schemas.TaskRes)
def attach_tag_to_task(tag_id: int, task_id: int, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    task = db.exec(select(models.Task).where(models.Task.id == task_id)).first()
    tag = db.exec(select(models.Tag).where(models.Tag.id == tag_id)).first()
    if task == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"task with id: {task_id} does not exist")
    elif tag == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"tag with id: {tag_id} does not exist")
    if tag.owner_id != Authorize.get_jwt_subject() or task.owner_id != Authorize.get_jwt_subject():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    task.tags.append(tag)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.delete("/detach/{task_id}/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def detach_tag_from_task(tag_id: int, task_id: int, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    task = db.exec(select(models.Task).where(models.Task.id == task_id)).first()
    tag = db.exec(select(models.Tag).where(models.Tag.id == tag_id)).first()
    if task == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"task with id: {task_id} does not exist")
    elif tag == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"tag with id: {tag_id} does not exist")
    if tag.owner_id != Authorize.get_jwt_subject() or task.owner_id != Authorize.get_jwt_subject():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    task.tags.remove(tag)
    db.add(task)
    db.commit()
    db.refresh(task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)