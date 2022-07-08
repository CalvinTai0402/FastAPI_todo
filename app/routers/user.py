from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas
from ..database import get_db
from sqlmodel import Session, select

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.get('/{id}', response_model=schemas.UserRes)
def get_user(id: int, db: Session = Depends(get_db)):
    statement = select(models.User).where(models.User.id == id)
    results = db.exec(statement)
    user = results.first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} does not exist")
    return user