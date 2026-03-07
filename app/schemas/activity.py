from datetime import datetime

from app.schemas.base import CamelModel
from app.schemas.cafe import CafeResponse
from app.schemas.user import UserResponse

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
    created_at: datetime

    class Config:
        from_attributes = True  # required for SQLAlchemy → Pydantic


class ActivityFeedResponse(ActivityResponse):
    user: UserResponse

    class Config:
        from_attributes = True