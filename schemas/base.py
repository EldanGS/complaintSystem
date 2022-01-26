from pydantic import BaseModel


class ComplaintBase(BaseModel):
    title: str
    description: str
    amount: float


class UserBase(BaseModel):
    email: str
