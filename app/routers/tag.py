from fastapi import Body, Response, status, HTTPException, Depends, APIRouter
from typing import List, Optional
from fastapi_jwt_auth import AuthJWT
from .. import models, schemas
from ..database import get_db
from sqlmodel import Session, select


router = APIRouter(
    prefix="/tags",
    tags=['Tags']
)

@router.get("/", response_model=List[schemas.TagRes])
def get_tags(db: Session = Depends(get_db), Authorize: AuthJWT = Depends(), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    Authorize.jwt_required()
    statement = select(models.Tag).where(models.Tag.description.contains(search)).where(models.Tag.owner_id==Authorize.get_jwt_subject()).offset(skip).limit(limit)
    results = db.exec(statement)
    tags = results.all()
    return tags

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_tag(tag: schemas.TagCreate, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    current_user = db.exec(select(models.User).where(models.User.id == Authorize.get_jwt_subject())).first()
    new_tag = models.Tag(owner_id=Authorize.get_jwt_subject(), **tag.dict())
    new_tag.owner = current_user
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag

@router.get("/{id}", response_model=schemas.TagRes)
def get_tag(id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    statement = select(models.Tag).where(models.Tag.id == id)
    results = db.exec(statement)
    tag = results.first()
    if tag == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"tag with id: {id} was not found")
    if tag.owner_id != Authorize.get_jwt_subject():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    return tag

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    statement = select(models.Tag).where(models.Tag.id == id)
    results = db.exec(statement)
    tag = results.first()
    if tag == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"tag with id: {id} does not exist")
    if tag.owner_id != Authorize.get_jwt_subject():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    db.delete(tag)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}")
def update_tag(id: int, updated_tag: schemas.TagCreate, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    statement = select(models.Tag).where(models.Tag.id == id)
    results = db.exec(statement)
    tag = results.first()
    if tag == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"tag with id: {id} does not exist")
    if tag.owner_id != Authorize.get_jwt_subject():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    updated_tag_data = updated_tag.dict(exclude_unset=True)
    for key, value in updated_tag_data.items():
        setattr(tag, key, value)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag