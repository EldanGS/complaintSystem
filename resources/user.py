from typing import Optional, List

from fastapi import APIRouter, Depends

from managers.auth import oauth_scheme
from managers.complaint import is_admin
from managers.user import UserManager
from models import RoleType
from schemas.response.user import UserOut

router = APIRouter(tags=["Users"])


@router.get(
    "/users",
    dependencies=[Depends(oauth_scheme), Depends(is_admin)],
    response_model=List[UserOut],
)
async def get_users(email: Optional[str] = None):
    if email:
        return await UserManager.get_user_by_email(email)
    return await UserManager.get_all_users()


@router.put(
    "/users/{user_id}/{role}",
    dependencies=[Depends(oauth_scheme), Depends(is_admin)],
    status_code=204,
)
async def change_user_role(user_id: int, role: RoleType):
    await UserManager.change_role(user_id, role)
