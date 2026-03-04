from sqlalchemy import Column, Integer, String
from app.database import Base

class Cafe(Base):
    __tablename__ = "cafes"

    cafeId = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    mapsId = Column(String, nullable=False)
    mapsUrl = Column(String, nullable=False)
