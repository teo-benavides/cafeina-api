from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    refreshTokenId = Column(Integer, primary_key=True)
    userId = Column(Integer, ForeignKey("users.userId"), nullable=False)
    tokenHash = Column(String, nullable=False)
    expiresAt = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User")