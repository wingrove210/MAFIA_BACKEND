from pydantic import BaseModel

class PointsTransaction(BaseModel):
    user_id: int
    points: int

class PointsResponse(BaseModel):
    user_id: int
    points: int
    message: str
