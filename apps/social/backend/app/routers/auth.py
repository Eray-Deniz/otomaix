from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.schemas import OkResponse, UserMe

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=OkResponse)
async def me(user: dict = Depends(get_current_user)):
    """Return the authenticated user's id and email."""
    return OkResponse(data=UserMe(id=user["sub"], email=user.get("email", "")))
