from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User
from models.order import Order
from models.product import Product
from schemas.order import OrderCreate, OrderResponse
# Роутер для работы с заказами
order_router = APIRouter()

# Получение сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Утилита для получения пользователя по ID
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_product_by_id(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()

# Утилита для получения заказа по ID
def get_order_by_id(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()

# Функция для начисления баллов
def add_points(db: Session, user_id: int, points: int):
    user = get_user_by_id(db, user_id)
    if user:
        user.points += points
        db.commit()
        db.refresh(user)
    return user

# Создание заказа
@order_router.post("/", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    user = get_user_by_id(db, order.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Получаем продукт по ID
    product = get_product_by_id(db, order.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Создание нового заказа
    new_order = Order(user_id=order.user_id, product_id=order.product_id, quantity=order.quantity)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    # Рассчитываем стоимость заказа и начисляем баллы (25% от стоимости)
    order_value = new_order.quantity * product.price  # Используем цену из модели Product
    points_to_add = int(order_value * 0.25)  # 25% от стоимости
    
    # Начисляем баллы пользователю
    add_points(db, user.id, points_to_add)
    
    return {"order_id": new_order.id, "user_id": new_order.user_id, "product_id": product.id, "order_price": order_value, "quantity": new_order.quantity, "points_added": points_to_add}

# Получение всех заказов
@order_router.get("/", response_model=list[OrderResponse])
def get_all_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    return [{"order_id": order.id, "user_id": order.user_id, "product_id": order.product_id, "quantity": order.quantity} for order in orders]

# Получение заказа по ID
@order_router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"order_id": order.id, "user_id": order.user_id, "product_id": order.product_id, "quantity": order.quantity}

# Удаление заказа по ID
@order_router.delete("/{order_id}", response_model=dict)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db.delete(order)
    db.commit()
    return {"message": "Order deleted successfully"}
