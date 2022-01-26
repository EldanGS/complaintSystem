import os
import uuid

from fastapi import HTTPException
from starlette.requests import Request

from constants import TEMP_FILE_FOLDER
from db import database
from models import complaint, RoleType, State
from services.s3 import S3Service
from services.ses import SESService
from utils.helpers import decode_photo

s3 = S3Service()
ses = SESService()


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
        encoded_photo = data.pop("encoded_photo")
        extension = data.pop("extension")
        name = f"{uuid.uuid4()}.{extension}"
        path = os.path.join(TEMP_FILE_FOLDER, name)
        decode_photo(path, encoded_photo)
        data["photo_url"] = s3.upload(path, name, extension)
        os.remove(path)
        id_: int = await database.execute(complaint.insert().values(**data))
        return await database.fetch_one(complaint.select().where(complaint.c.id == id_))

    @staticmethod
    async def delete(id_: int):
        await database.execute(complaint.delete().where(complaint.c.id == id_))

    @staticmethod
    async def approve(id_: int):
        await database.execute(
            complaint.update()
            .where(complaint.c.id == id_)
            .values(status=State.approved)
        )
        ses.send_email("Complaint approved",
                       ["your@emails.com"],
                       "congrants!")


    @staticmethod
    async def reject(id_: int):
        await database.execute(
            complaint.update()
            .where(complaint.c.id == id_)
            .values(status=State.rejected)
        )


def is_complainer(request: Request):
    if request.state.user["role"] != RoleType.complainer:
        raise HTTPException(403, "Forbidden")


def is_admin(request: Request):
    if request.state.user["role"] != RoleType.admin:
        raise HTTPException(403, "Forbidden")


def is_approver(request: Request):
    if request.state.user["role"] != RoleType.approver:
        raise HTTPException(403, "Forbidden")
