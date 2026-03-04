from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from app.database import Base
from sqlalchemy.orm import relationship

class Activity(Base):
    __tablename__ = "activities"

    activityId = Column(Integer, primary_key=True, index=True)
    cafeId = Column(Integer, ForeignKey("cafes.cafeId"), nullable=False)
    rating = Column(Integer, nullable=True)
    favorite = Column(Boolean, default=False, nullable=False)
    review = Column(String, nullable=True)

    cafe = relationship("Cafe")