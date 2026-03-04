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
    username: str
    fullName: str | None

    class Config:
        from_attributes = True

class UserMe(BaseModel):
    userId: int
    username: str
    fullName: str | None

    class Config:
        from_attributes = True