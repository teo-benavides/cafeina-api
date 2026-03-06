from app.schemas.base import CamelModel

class CafeBase(CamelModel):
    name: str
    address: str
    maps_id: str
    maps_url: str

class CafeCreate(CafeBase):
    pass

class CafeResponse(CafeBase):
    id: int
    slug: str

    class Config:
        from_attributes = True