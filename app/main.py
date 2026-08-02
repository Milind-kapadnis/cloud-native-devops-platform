from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Cloud Native DevOps Platform",
    version="1.0.0"
)


# -----------------------------
# Models
# -----------------------------

class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


# -----------------------------
# APIs
# -----------------------------

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


@app.post("/login")
def login(data: LoginRequest):
    if data.username == "admin" and data.password == "admin123":
        return {
            "message": "Login Successful"
        }

    return {
        "message": "Invalid Username or Password"
    }


@app.post("/register")
def register(data: RegisterRequest):
    return {
        "message": "User Registered Successfully",
        "username": data.username,
        "email": data.email
    }