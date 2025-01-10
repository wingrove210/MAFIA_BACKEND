from pydantic import BaseModel
from typing import Optional

class BillboardBase(BaseModel):
    name: str
    description: Optional[str] = None
    image: Optional[str] = None
    text_color: Optional[str] = None
    background_color: Optional[str] = None

class BillboardCreate(BillboardBase):
    pass

class BillboardUpdate(BillboardBase):
    name: Optional[str] = None
    price: Optional[float] = None
    image: Optional[str] = None
    text_color: Optional[str] = None
    background_color: Optional[str] = None

class BillboardResponse(BillboardBase):
    id: int

    class Config:
        orm_mode = True
