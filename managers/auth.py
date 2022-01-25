from typing import Optional

import jwt
from datetime import datetime, timedelta

from decouple import config
from fastapi import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.requests import Request

from db import database
from models import user


class AuthManager:
    @staticmethod
    def encode_token(user):
        try:
            payload = {
                "sub": user["id"],
                "exp": datetime.utcnow() + timedelta(minutes=120)
            }

            return jwt.encode(payload, config("JWT_SECRET"), algorithm="HS256")
        except Exception as ex:
            # log the exception
            raise ex


class CustomHTTPBearer(HTTPBearer):
    async def __call__(
            self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        res = await super().__call__(request)
        from models import user
        try:
            payload = jwt.decode(res.credentials, config('JWT_SECRET'), algorithms=['HS256'])
            user = await database.fetch_one(user.select().where(user.c.id == payload["sub"]))
            request.state.user = user
            return user
        except jwt.ExpiredSignatureError:
            raise HTTPException(401, "Token is expired!")
        except jwt.InvalidTokenError:
            raise HTTPException(401, "Invalid token")


oauth_scheme = CustomHTTPBearer()
