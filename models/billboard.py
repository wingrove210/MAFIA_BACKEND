from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base

class Billboard(Base):
    __tablename__ = "billboards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    image = Column(String, nullable=True)
    text_color = Column(String, nullable=True)
    background_color = Column(String, nullable=True)
