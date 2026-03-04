from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    userId: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    fullName: Mapped[str | None] = mapped_column(String, nullable=True)
    hashedPassword: Mapped[str] = mapped_column(String, nullable=False)

    activities = relationship("Activity")