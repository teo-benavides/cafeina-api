from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.models.base import IdMixin, TimestampMixin

class Cafe(Base, IdMixin, TimestampMixin):
    __tablename__ = "cafes"

    name: Mapped[str]
    address: Mapped[str]
    maps_id: Mapped[str] = mapped_column(unique=True)
    maps_url: Mapped[str]