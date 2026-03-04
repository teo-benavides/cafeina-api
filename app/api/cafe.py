from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.crud.cafe import create_cafe, get_cafes
from app.database import get_db
from app.schemas.cafe import CafeBase, CafeCreate, CafeResponse
# from app.crud.cafe import get_cafes
from app.services.places import search_cafes

router = APIRouter(prefix="/cafes", tags=["cafes"])

@router.get("", response_model=List[CafeResponse])
async def read_cafes(db: Session = Depends(get_db)):
    return get_cafes(db)

@router.get("/search", response_model=List[CafeBase])
async def get_nearby_cafes(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius: float = Query(..., description="Radius in meters"),
    db: Session = Depends(get_db),
):
    return await search_cafes((lat, lng), radius)

@router.post("", response_model=CafeResponse)
def add_cafe(cafe: CafeCreate, db: Session = Depends(get_db)):
    return create_cafe(db, cafe)