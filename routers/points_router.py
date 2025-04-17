from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User
from schemas.points import PointsTransaction, PointsResponse

# Роутер для работы с баллами
points_router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# Начисление баллов
@points_router.post("/add", response_model=PointsResponse)
def add_points(user_id: int, points: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.points += points
    db.commit()
    db.refresh(user)
    return {"user_id": user.id, "points": user.points, "message": "Points added successfully"}

# Списание баллов
@points_router.post("/redeem", response_model=PointsResponse)
def redeem_points(user_id: int, points: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.points < points:
        raise HTTPException(status_code=400, detail="Not enough points")
    
    user.points -= points
    db.commit()
    db.refresh(user)
    return {"user_id": user.id, "points": user.points, "message": "Points redeemed successfully"}

# Получение текущего количества баллов
@points_router.get("/{user_id}", response_model=PointsResponse)
def get_user_points(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"user_id": user.id, "points": user.points, "message": "User points retrieved successfully"}
