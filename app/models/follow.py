from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import IdMixin, TimestampMixin


class Follow(Base, IdMixin, TimestampMixin):
    __tablename__ = "follows"
    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="uq_follower_following"),
    )

    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    following_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    follower: Mapped["User"] = relationship(
        foreign_keys=[follower_id], back_populates="following"
    )
    following: Mapped["User"] = relationship(
        foreign_keys=[following_id], back_populates="followers"
    )
