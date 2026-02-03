import math

from fastapi import APIRouter, Depends, HTTPException, Query

from volta_api.auth.dependencies import get_current_admin_user
from volta_api.core.api_response import ApiResponse, PaginationMeta, success_response
from .schemas import (
    UserCreate,
    UserDeleteConfirm,
    UserUpdate,
    UserRole,
)
from .service import (
    create_user,
    get_user_by_email,
    get_user_by_public_id,
    get_users,
    get_users_count,
    delete_user,
    update_user,
)

router = APIRouter()
register_router = APIRouter(prefix="/volta/api/auth/register", tags=["users"])
users_router = APIRouter(
    prefix="/volta/api/users",
    tags=["users"],
    dependencies=[Depends(get_current_admin_user)],
)


@register_router.post("", response_model=ApiResponse, response_model_exclude_none=True)
async def register_user(payload: UserCreate):
    existing = await get_user_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await create_user(
        payload.email,
        payload.password,
        role=payload.role.value,
    )
    return success_response(message="User created", data=user)


@users_router.get("", response_model=ApiResponse, response_model_exclude_none=True)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    role: UserRole | None = Query(None, description="Filter by role"),
    is_active: bool | None = Query(None, description="Filter by active status"),
):
    skip = (page - 1) * page_size
    role_value = role.value if role else None

    users = await get_users(
        skip=skip,
        limit=page_size,
        role=role_value,
        is_active=is_active,
    )
    total = await get_users_count(role=role_value, is_active=is_active)
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    meta = PaginationMeta(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
    return success_response(data=users, meta=meta)


@users_router.post("", response_model=ApiResponse, response_model_exclude_none=True, status_code=201)
async def create_user_admin(payload: UserCreate):
    existing = await get_user_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await create_user(
        payload.email,
        payload.password,
        role=payload.role.value,
    )
    return success_response(message="User created", data=user)


@users_router.get("/{public_id}", response_model=ApiResponse, response_model_exclude_none=True)
async def read_user(public_id: str):
    user = await get_user_by_public_id(public_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return success_response(data=user)


@users_router.put("/{public_id}", response_model=ApiResponse, response_model_exclude_none=True)
async def edit_user(public_id: str, payload: UserUpdate):
    user = await get_user_by_public_id(public_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.email:
        existing = await get_user_by_email(payload.email)
        if existing and existing.public_id != public_id:
            raise HTTPException(status_code=400, detail="Email already registered")

    update_data = payload.model_dump(exclude_unset=True)
    if "role" in update_data and update_data["role"]:
        update_data["role"] = update_data["role"].value

    updated = await update_user(public_id, update_data)
    return success_response(message="User updated", data=updated)


@users_router.delete("/{public_id}", response_model=ApiResponse, response_model_exclude_none=True)
async def deactivate_user(public_id: str, payload: UserDeleteConfirm):
    user = await get_user_by_public_id(public_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.confirm != public_id:
        raise HTTPException(status_code=400, detail="Confirmation does not match user")
    await delete_user(public_id)
    return success_response(message="User deleted")


router.include_router(register_router)
router.include_router(users_router)
