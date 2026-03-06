from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Cafe(Base):
    __tablename__ = "cafes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str]
    address: Mapped[str]
    maps_id: Mapped[str] = mapped_column(unique=True)
    maps_url: Mapped[str]