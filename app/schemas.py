from pydantic import BaseModel


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True
class UpdateUserRequest(BaseModel):
    username: str
    email: str
class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class UpdateUserRequest(BaseModel):
    username: str
    email: str
