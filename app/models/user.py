from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    email: Mapped[str] = mapped_column(unique=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)

    full_name: Mapped[str | None]

    hashed_password: Mapped[str]

    activities: Mapped[list["Activity"]] = relationship(back_populates="user")