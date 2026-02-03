from fastapi import APIRouter, HTTPException
from .schemas import UserCreate, UserOut
from .service import create_user, get_user_by_email

router = APIRouter(prefix="/volta/api/auth/register", tags=["users"])


@router.post("", response_model=UserOut)
async def register_user(payload: UserCreate):
    existing = await get_user_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await create_user(payload.email, payload.password)
    return user
