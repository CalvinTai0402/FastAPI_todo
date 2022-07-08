from fastapi import APIRouter, Body, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from .. import database, schemas, models, utils
from ..config import settings
from ..database import get_db

router = APIRouter(tags=['Authentication'])

@AuthJWT.load_config
def get_config():
    return settings

@router.post('/login', response_model=schemas.Token)
def login(user_credentials: dict = Body(...), db: Session = Depends(database.get_db), Authorize: AuthJWT = Depends()):
    user = db.query(models.User).filter(models.User.email == user_credentials.get("username")).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    if not utils.verify(user_credentials.get("password"), user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    access_token = Authorize.create_access_token(subject=user.id, algorithm=settings.algorithm, expires_time=settings.access_token_expire_minutes*60)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=schemas.UserRes)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    users = db.query(models.User).all()
    for user in users:
        if user.email == new_user.email:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=f"Email is used by another user")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user