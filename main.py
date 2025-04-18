from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.auth_router import auth_router
from routers.product_router import product_router
from routers.billboard_router import billboard_router
from database import Base, engine
from routers.points_router import points_router
from routers.order_router import order_router
# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение маршрутов
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(product_router, prefix="/product", tags=["Products"])
app.include_router(billboard_router, prefix="/billboards", tags=["billboards"])
app.include_router(points_router, prefix="/points", tags=["points"])
app.include_router(order_router, prefix="/order", tags=["order"])
