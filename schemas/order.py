from pydantic import BaseModel

class OrderCreate(BaseModel):
    user_id: int
    product_id: int # This is the product ID that will be used to look up the product in the database
    quantity: int = 1

class OrderResponse(BaseModel):
    order_id: int
    user_id: int
    product_id: int
    quantity: int
