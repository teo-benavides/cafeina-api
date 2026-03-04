from pydantic import BaseModel

class CafeBase(BaseModel):
    name: str
    address: str
    mapsId: str
    mapsUrl: str

class CafeCreate(CafeBase):
    pass

class CafeResponse(CafeBase):
    cafeId: int

    class Config:
        from_attributes = True