from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.cafe import Cafe
from app.schemas.cafe import CafeCreate

def get_cafe_by_maps_id(db: Session, maps_id: str):
    stmt = select(Cafe).where(Cafe.maps_id == maps_id)
    return db.scalars(stmt).one_or_none()

def get_cafes(db: Session):
    return db.scalars(
        select(Cafe)
    ).all()

def create_cafe(db: Session, cafe: CafeCreate):
    existing = get_cafe_by_maps_id(db, cafe.maps_id)
    if existing:
        raise HTTPException(status_code=400, detail="Cafe already exists!")

    db_cafe = Cafe(**cafe.model_dump())
    db.add(db_cafe)
    db.commit()
    db.refresh(db_cafe)
    return db_cafe