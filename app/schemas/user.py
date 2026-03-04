from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str
    fullName: str | None

class UserLogin(BaseModel):
    emailOrUsername: str
    password: str

class UserResponse(BaseModel):
    userId: int
    email: EmailStr
    username: str
    fullName: str | None

    class Config:
        from_attributes = True