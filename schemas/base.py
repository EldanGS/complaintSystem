from pydantic import BaseModel


class ComplaintBase(BaseModel):
    title: str
    description: str
    photo_url: str
    amount: float


class UserBase(BaseModel):
    email: str