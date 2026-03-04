from pydantic import BaseModel

from app.schemas.cafe import CafeResponse

class ActivityBase(BaseModel):
    rating: int | None
    favorite: bool
    review: str | None

class ActivityCreate(ActivityBase):
    cafeId: int

class ActivityResponse(ActivityBase):
    activityId: int
    cafe: CafeResponse

    class Config:
        from_attributes = True  # required for SQLAlchemy → Pydantic