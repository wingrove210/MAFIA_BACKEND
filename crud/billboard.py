from sqlalchemy.orm import Session
from models.billboard import Billboard
from schemas.billboard import BillboardCreate, BillboardUpdate

def create_billboard(db: Session, billboard: BillboardCreate):
    db_billboard = Billboard(**billboard.dict())
    db.add(db_billboard)
    db.commit()
    db.refresh(db_billboard)
    return db_billboard

def get_billboard(db: Session, billboard_id: int):
    return db.query(Billboard).filter(Billboard.id == billboard_id).first()

def get_billboards(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Billboard).offset(skip).limit(limit).all()

def update_billboard(db: Session, billboard_id: int, billboard_update: BillboardUpdate):
    db_billboard = get_billboard(db, billboard_id)
    if not db_billboard:
        return None
    for key, value in billboard_update.dict(exclude_unset=True).items():
        setattr(db_billboard, key, value)
    db.commit()
    db.refresh(db_billboard)
    return db_billboard

def delete_billboard(db: Session, billboard_id: int):
    db_billboard = get_billboard(db, billboard_id)
    if not db_billboard:
        return None
    db.delete(db_billboard)
    db.commit()
    return db_billboard
