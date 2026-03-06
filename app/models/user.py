from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import IdMixin, TimestampMixin


class User(Base, IdMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)

    full_name: Mapped[str | None]

    hashed_password: Mapped[str]

    activities: Mapped[list["Activity"]] = relationship(back_populates="user")

    following: Mapped[list["Follow"]] = relationship(
        "Follow", foreign_keys="Follow.follower_id", back_populates="follower"
    )
    followers: Mapped[list["Follow"]] = relationship(
        "Follow", foreign_keys="Follow.following_id", back_populates="following"
    )