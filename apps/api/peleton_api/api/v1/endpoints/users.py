from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from peleton_api.core.database import get_db
from peleton_api.models import models
from peleton_api.schemas import user as schemas

router = APIRouter()


@router.get("", response_model=list[schemas.UserResponse], summary="List alle brukere")
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


@router.post("", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED, summary="Opprett ny bruker")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-postadresse er allerede i bruk"
        )

    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user