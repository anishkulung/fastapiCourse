from fastapi import Response, status, HTTPException
from fastapi.params import Depends
from fastapi.routing import APIRouter

from app import utils
from .. import schemas, models
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/users",tags=["users"])

@router.post("/", status_code = status.HTTP_201_CREATED,response_model= schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hash_password = utils.hash(user.password)
    user.password = hash_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/", status_code = status.HTTP_200_OK, response_model=List[schemas.User])
def read_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

@router.get("/{id}", response_model=schemas.User)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User with {id} not found")
    return user