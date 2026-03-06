from app.schemas.base import CamelModel
from app.schemas.cafe import CafeResponse

class ActivityBase(CamelModel):
    rating: int | None
    favorite: bool
    review: str | None

class ActivityCreate(ActivityBase):
    user_id: int
    cafe_id: int

class ActivityResponse(ActivityBase):
    id: int
    cafe: CafeResponse

    class Config:
        from_attributes = True  # required for SQLAlchemy → Pydantic