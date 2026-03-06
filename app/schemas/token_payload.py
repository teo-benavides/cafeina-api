from typing import Literal
from app.schemas.base import CamelModel

class TokenPayload(CamelModel):
    sub: str
    token_type: Literal["access", "refresh"]
    exp: int