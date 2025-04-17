from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

# Модель пользователя
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    points = Column(Integer, default=0)  
    orders = relationship("Order", back_populates="user")
    role = Column(String, default="default")