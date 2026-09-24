from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)


class UpdateUserRequest(BaseModel):
    username: str
    email: str
