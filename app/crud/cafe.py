from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.cafe import Cafe
from app.schemas.cafe import CafeCreate
import re
import uuid
import unicodedata


def _slugify(value: str) -> str:
    # Normalize unicode and strip diacritics so "café" -> "cafe"
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value


def _generate_cafe_slug(db: Session, name: str, address: str) -> str:
    base_slug = _slugify(name)
    if not base_slug:
        base_slug = "cafe"

    # 1) Try just name
    existing = db.scalars(select(Cafe).where(Cafe.slug == base_slug)).first()
    if not existing:
        return base_slug

    # 2) Try name + address
    name_address_slug = _slugify(f"{name}-{address}")
    if not name_address_slug:
        name_address_slug = f"{base_slug}-addr"

    existing = db.scalars(select(Cafe).where(Cafe.slug == name_address_slug)).first()
    if not existing:
        return name_address_slug

    # 3) Fallback: name + address + short uid
    short_uid = uuid.uuid4().hex[:6]
    final_slug = _slugify(f"{name}-{address}-{short_uid}")
    return final_slug or f"{base_slug}-{short_uid}"


def get_cafe_by_maps_id(db: Session, maps_id: str):
    stmt = select(Cafe).where(Cafe.maps_id == maps_id)
    return db.scalars(stmt).one_or_none()


def get_cafe_by_slug(db: Session, slug: str):
    stmt = select(Cafe).where(Cafe.slug == slug)
    return db.scalars(stmt).one_or_none()


def get_cafes(db: Session):
    return db.scalars(
        select(Cafe)
    ).all()


def create_cafe(db: Session, cafe: CafeCreate) -> Cafe:
    existing = get_cafe_by_maps_id(db, cafe.maps_id)
    if existing:
        raise HTTPException(status_code=400, detail="Cafe already exists!")

    slug = _generate_cafe_slug(db, cafe.name, cafe.address)

    db_cafe = Cafe(**cafe.model_dump(), slug=slug)
    db.add(db_cafe)
    db.commit()
    db.refresh(db_cafe)
    return db_cafe