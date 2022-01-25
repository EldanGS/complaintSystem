from datetime import datetime

from models import State
from schemas.base import ComplaintBase


class ComplaintOut(ComplaintBase):
    id: int

    created_at: datetime
    status: State
