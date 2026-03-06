from sqlalchemy import ForeignKey, false
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import IdMixin, TimestampMixin

class Activity(Base, IdMixin, TimestampMixin):
    __tablename__ = "activities"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    cafe_id: Mapped[int] = mapped_column(ForeignKey("cafes.id"))

    rating: Mapped[int | None]
    favorite: Mapped[bool] = mapped_column(server_default=false())
    review: Mapped[str | None]

    user: Mapped["User"] = relationship(back_populates="activities")
    cafe: Mapped["Cafe"] = relationship()