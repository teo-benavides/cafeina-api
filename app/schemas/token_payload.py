from pydantic import BaseModel
from typing import Literal

class TokenPayload(BaseModel):
    sub: str
    token_type: Literal["access", "refresh"]
    exp: int