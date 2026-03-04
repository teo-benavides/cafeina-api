from sqlalchemy.orm import Session
from app.models.cafe import Cafe
from app.schemas.cafe import CafeCreate

def get_cafes(db: Session):
    return db.query(Cafe).all()

def create_cafe(db: Session, cafe: CafeCreate):
    db_cafe = Cafe(**cafe.model_dump())
    db.add(db_cafe)
    db.commit()
    db.refresh(db_cafe)
    return db_cafe