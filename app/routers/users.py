from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas import UserResponse, UpdateUserRequest
from app import models
from app import crud

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/", response_model=list[UserResponse])
def get_all_users(
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.User).all()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UpdateUserRequest,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.update_user(
        db=db,
        user_id=user_id,
        username=data.username,
        email=data.email
    )


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.delete_user(
        db=db,
        user_id=user_id
    )
