import os
import uuid

from fastapi import HTTPException
from starlette.requests import Request

from constants import TEMP_FILE_FOLDER
from db import database
from models import complaint, RoleType, State, transaction
from services.s3 import S3Service
from services.ses import SESService
from services.wise import WiseService
from utils.helpers import decode_photo

s3 = S3Service()
ses = SESService()
wise = WiseService()


class ComplaintManager:
    @staticmethod
    async def get_complaints(user):
        q = complaint.select()
        if user["role"] == RoleType.complainer:
            q = q.where(complaint.c.complainer_id == user["id"])
        elif user["role"] == RoleType.approver:
            q = q.where(complaint.c.status == State.pending)
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

        async with database.transaction() as tconn:
            id_: int = await tconn._connection.execute(
                complaint.insert().values(**data)
            )

            await ComplaintManager.issue_transaction(
                tconn,
                data["amount"],
                f"{user['first_name']} {user['last_name']}",
                user["iban"],
                id_,
            )
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
        transaction_data = await database.fetch_one(
            transaction.select().where(transaction.c.complaint_id == id_)
        )
        wise.fund_transfer(transaction_data["transfer_id"])

        ses.send_email(
            "Complaint approved",
            ["eldan.abdrashim@gmail.com", "eldan.king@gmail.com"],
            "Congrants you have buy a new item!",
        )

    @staticmethod
    async def reject(id_: int):
        transaction_data = await database.fetch_one(
            transaction.select().where(transaction.c.complaint_id == id_)
        )

        wise.cancel_funds(transaction_data["transfer_id"])

        await database.execute(
            complaint.update()
            .where(complaint.c.id == id_)
            .values(status=State.rejected)
        )

    @staticmethod
    async def issue_transaction(connection, amount, full_name, iban, complaint_id):
        quote_id: str = wise.create_quote(amount)
        recipient_id: int = wise.create_recipient_account(full_name, iban)
        transfer_id: int = wise.create_transfer(recipient_id, quote_id)
        data = {
            "quote_id": quote_id,
            "transfer_id": transfer_id,
            "target_account_id": str(recipient_id),
            "amount": amount,
            "complaint_id": complaint_id,
        }

        await connection._connection.execute(transaction.insert().values(**data))


def is_complainer(request: Request):
    if request.state.user["role"] != RoleType.complainer:
        raise HTTPException(403, "Forbidden")


def is_admin(request: Request):
    if request.state.user["role"] != RoleType.admin:
        raise HTTPException(403, "Forbidden")


def is_approver(request: Request):
    if request.state.user["role"] != RoleType.approver:
        raise HTTPException(403, "Forbidden")
