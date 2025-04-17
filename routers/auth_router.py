from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Union
from pydantic import BaseModel
from models.user import User
from models.order import Order
from database import get_db

# Настройки безопасности и токенов
SECRET_KEY = "your_secret_key"  # Замените на ваш секретный ключ
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Blacklist для токенов
token_blacklist = set()

# Инициализация роутера
auth_router = APIRouter()

# Схемы данных
class UserCreate(BaseModel):
    username: str
    password: str
    points: Optional[int] = 0
    orders: Optional[int] = []

class Token(BaseModel):
    access_token: str
    token_type: str

# Утилиты
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_all_users(db: Session):
    return db.query(User).all()

def delete_user_by_id(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False

def delete_all_users(db: Session):
    users = db.query(User).all()
    for user in users:
        db.delete(user)
    db.commit()
# Маршруты
@auth_router.post("/register", response_model=dict)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    create_user(db, user)
    return {"message": "User registered successfully"}

@auth_router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/users/me", response_model=dict)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=403, detail="Invalid token")
        user = get_user_by_username(db, username=username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"id": user.id, "username": user.username, "points": user.points}
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")


@auth_router.get("/verify-token/{token}")
def verify_token(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if not username:
            raise HTTPException(status_code=403, detail="Invalid token")
        
        user = get_user_by_username(db, username=username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        expiration = datetime.utcfromtimestamp(payload.get("exp"))
        if expiration < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token has expired")
        
        return {"message": "Token is valid"}
    
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")

@auth_router.post("/logout")
def logout_user(token: str = Depends(oauth2_scheme)):
    if token in token_blacklist:
        raise HTTPException(status_code=403, detail="Token is already invalidated")
    token_blacklist.add(token)
    return {"message": "User successfully logged out"}

@auth_router.get("/users", response_model=list)
def get_users(db: Session = Depends(get_db)):
    users = get_all_users(db)
    result = []
    for user in users:
        orders = [{
            "order_id": order.id,
            "product_id": order.product_id,
            "quantity": order.quantity
        } for order in user.orders]
        result.append({
            "id": user.id,
            "username": user.username,
            "points": user.points,
            "orders": orders
        })
    return result

@auth_router.delete("/users/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    success = delete_user_by_id(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User successfully deleted"}

@auth_router.delete("/users", response_model=dict)
def delete_all_users_route(db: Session = Depends(get_db)):
    delete_all_users(db)
    return {"message": "All users have been deleted"}
