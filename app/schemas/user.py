from pydantic import BaseModel, EmailStr, field_validator
from app.schemas.base import CamelModel


class UserCreate(CamelModel):
    email: EmailStr
    password: str
    username: str
    full_name: str | None

    @field_validator("full_name", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: str | None) -> str | None:
        if v == "":
            return None
        return v

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