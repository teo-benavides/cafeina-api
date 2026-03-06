from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from app.models.refresh_token import RefreshToken

def get_refresh_token_by_hash(db: Session, token_hash: str):
    stmt = select(RefreshToken).where(
        RefreshToken.token_hash == token_hash
    )
    return db.scalars(stmt).one_or_none()

def delete_refresh_token_by_hash(db: Session, token_hash: str):
    stmt = delete(RefreshToken).where(
        RefreshToken.token_hash == token_hash
    )
    db.execute(stmt)
    db.commit()
