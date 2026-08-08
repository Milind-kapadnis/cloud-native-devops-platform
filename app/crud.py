from sqlalchemy.orm import Session
from fastapi import HTTPException

from app import models
from app.core.security import hash_password, verify_password


def create_user(db: Session, username: str, email: str, password: str):
    existing_username = db.query(models.User).filter(
        models.User.username == username
    ).first()

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    existing_email = db.query(models.User).filter(
        models.User.email == email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    hashed_password = hash_password(password)

    user = models.User(
        username=username,
        email=email,
        password=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter(
        models.User.username == username
    ).first()

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user


def update_user(db: Session, user_id: int, username: str, email: str):
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.username = username
    user.email = email

    db.commit()
    db.refresh(user)

    return user


def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }
