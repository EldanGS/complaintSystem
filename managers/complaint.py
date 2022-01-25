from fastapi import HTTPException
from starlette.requests import Request

from db import database
from models import complaint, RoleType, State


class ComplaintManager:
    @staticmethod
    async def get_complaints(user):
        q = complaint.select()
        if user["role"] == RoleType.complainer:
            q = q.where(complaint.c.complainer_id == user["id"])
        elif user["role"] == RoleType.approver:
            q = q.where(complaint.c.state == State.pending)
        return await database.fetch_all(q)

    @staticmethod
    async def create_complaints(user, complaint_data):
        data = complaint_data.dict()
        data["complainer_id"] = user["id"]
        id_: int = await database.execute(complaint.insert().values(**data))
        return await database.fetch_one(complaint.select().where(complaint.c.id == id_))

    @staticmethod
    async def delete(id_: int):
        await database.execute(complaint.delete().where(complaint.c.id == id_))

    @staticmethod
    async def approve(id_: int):
        await database.execute(complaint.update().where(complaint.c.id == id_).values(status=State.approved))

    @staticmethod
    async def reject(id_: int):
        await database.execute(complaint.update().where(complaint.c.id == id_).values(status=State.rejected))


def is_complainer(request: Request):
    if request.state.user["role"] != RoleType.complainer:
        raise HTTPException(403, "Forbidden")


def is_admin(request: Request):
    if request.state.user["role"] != RoleType.admin:
        raise HTTPException(403, "Forbidden")


def is_approver(request: Request):
    if request.state.user["role"] != RoleType.approver:
        raise HTTPException(403, "Forbidden")
