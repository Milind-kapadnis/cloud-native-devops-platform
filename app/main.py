from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import engine, Base
from dependencies import get_db
from schemas import RegisterRequest, LoginRequest, UserResponse
from routers import users

import models
import crud
from core.security import create_access_token

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cloud Native DevOps Platform",
    version="1.0.0"
)

# Include Routers
app.include_router(users.router)


@app.get("/")
def root():
    return {
        "message": "Cloud Native DevOps Platform is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/register", response_model=UserResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = crud.create_user(
        db=db,
        username=data.username,
        email=data.email,
        password=data.password
    )

    return user


@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = crud.authenticate_user(
        db=db,
        username=data.username,
        password=data.password
    )

    if not user:
        return {
            "message": "Invalid username or password"
        }

    token = create_access_token(
        {"sub": user.username}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }