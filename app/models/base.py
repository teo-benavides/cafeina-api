from sqlalchemy import DateTime, func
from sqlalchemy.orm import mapped_column, Mapped

class TimestampMixin:
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), index=True)

class IdMixin:
    id: Mapped[int] = mapped_column(primary_key=True, index=True)