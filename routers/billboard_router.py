from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from crud.billboard import (
    create_billboard, get_billboards, get_billboard, update_billboard, delete_billboard
)
from schemas.billboard import BillboardCreate, BillboardUpdate, BillboardResponse
from fastapi.middleware.cors import CORSMiddleware
billboard_router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@billboard_router.post("/", response_model=BillboardResponse)
def create_new_billboard(billboard: BillboardCreate, db: Session = Depends(get_db)):
    return create_billboard(db, billboard)

@billboard_router.get("/", response_model=list[BillboardResponse])
def read_billboards(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_billboards(db, skip=skip, limit=limit)

@billboard_router.get("/{billboard_id}", response_model=BillboardResponse)
def read_billboard(billboard_id: int, db: Session = Depends(get_db)):
    billboard = get_billboard(db, billboard_id)
    if not billboard:
        raise HTTPException(status_code=404, detail="billboard not found")
    return billboard

@billboard_router.put("/{billboard_id}", response_model=BillboardResponse)
def update_existing_billboard(
    billboard_id: int, billboard_update: BillboardUpdate, db: Session = Depends(get_db)
):
    updated_billboard = update_billboard(db, billboard_id, billboard_update)
    if not updated_billboard:
        raise HTTPException(status_code=404, detail="billboard not found")
    return updated_billboard

@billboard_router.delete("/{billboard_id}", response_model=BillboardResponse)
def delete_existing_billboard(billboard_id: int, db: Session = Depends(get_db)):
    deleted_billboard = delete_billboard(db, billboard_id)
    if not deleted_billboard:
        raise HTTPException(status_code=404, detail="billboard not found")
    return deleted_billboard