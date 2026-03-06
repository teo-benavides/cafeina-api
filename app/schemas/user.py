from pydantic import BaseModel, EmailStr
from app.schemas.base import CamelModel

class UserCreate(CamelModel):
    email: EmailStr
    password: str
    username: str
    full_name: str | None

class UserLogin(CamelModel):
    email_or_username: str
    password: str

class UserResponse(CamelModel):
    username: str
    full_name: str | None

    class Config:
        from_attributes = True

class UserMe(CamelModel):
    id: int
    username: str
    full_name: str | None

    class Config:
        from_attributes = True