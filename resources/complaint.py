from typing import List

from fastapi import APIRouter, Depends
from starlette.requests import Request

from managers.auth import oauth_scheme
from managers.complaint import ComplaintManager, is_complainer, is_admin, is_approver
from schemas.request.complaint import ComplaintIn
from schemas.response.complaint import ComplaintOut

router = APIRouter(tags=["Complaints"])


@router.get(
    "/complaints",
    dependencies=[Depends(oauth_scheme)],
    response_model=List[ComplaintOut],
)
async def get_all_complaints(request: Request):
    user = request.state.user
    return await ComplaintManager.get_complaints(user)


@router.post(
    "/complaints",
    dependencies=[Depends(oauth_scheme), Depends(is_complainer)],
    response_model=ComplaintOut,
)
async def create_complaint(request: Request, complaint: ComplaintIn):
    user = request.state.user
    return await ComplaintManager.create_complaints(user, complaint)


@router.delete(
    "/complaints/{complaint_id}",
    dependencies=[Depends(oauth_scheme), Depends(is_admin)],
    status_code=204,
)
async def delete_complaint(complaint_id: int):
    await ComplaintManager.delete(complaint_id)


@router.put(
    "/complaints/{complaint_id}/approve",
    dependencies=[Depends(oauth_scheme), Depends(is_approver)],
    status_code=204,
)
async def approve_complaint(complaint_id: int):
    await ComplaintManager.approve(complaint_id)


@router.put(
    "/complaints/{complaint_id}/reject",
    dependencies=[Depends(oauth_scheme), Depends(is_approver)],
    status_code=204,
)
async def approve_complaint(complaint_id: int):
    await ComplaintManager.reject(complaint_id)
