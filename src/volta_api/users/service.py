from sqlalchemy import select, update, func
from volta_api.core.database import database
from .models import User
from volta_api.core.security import hash_password
from volta_api.utils import generate_base64_id


# ===== Create Operations =====


async def create_user(email: str, password: str, role: str = "driver"):
    """Create a new user and return the user data."""
    public_id = generate_base64_id()

    query = User.__table__.insert().values(
        email=email,
        hashed_password=hash_password(password),
        role=role,
        is_active=True,
        is_email_verified=False,
        public_id=public_id,
    )
    await database.execute(query)

    return await get_user_by_public_id(public_id)


# ===== Read Operations =====


async def get_user_by_email(email: str):
    """Get a user by email address."""
    query = User.__table__.select().where(User.email == email)
    return await database.fetch_one(query)


async def get_user_by_public_id(public_id: str):
    """Get a user by their public ID."""
    query = User.__table__.select().where(User.public_id == public_id)
    return await database.fetch_one(query)


async def get_user_by_id(user_id: int):
    """Get a user by internal ID."""
    query = User.__table__.select().where(User.id == user_id)
    return await database.fetch_one(query)


async def get_users(
    skip: int = 0,
    limit: int = 100,
    role: str | None = None,
    is_active: bool | None = None,
):
    query = User.__table__.select()

    if role is not None:
        query = query.where(User.role == role)
    if is_active is not None:
        query = query.where(User.is_active == is_active)

    query = query.offset(skip).limit(limit)
    return await database.fetch_all(query)


async def get_users_count(role: str | None = None, is_active: bool | None = None) -> int:
    query = select(func.count()).select_from(User.__table__)

    if role is not None:
        query = query.where(User.role == role)
    if is_active is not None:
        query = query.where(User.is_active == is_active)

    result = await database.fetch_one(query)
    return result[0] if result else 0


# ===== Update Operations =====


async def update_user_password(public_id: str, new_password: str):
    """Update a user's password."""
    query = (
        update(User.__table__)
        .where(User.public_id == public_id)
        .values(hashed_password=hash_password(new_password))
    )
    await database.execute(query)
    return await get_user_by_public_id(public_id)


async def verify_user_email(public_id: str):
    """Mark user's email as verified."""
    query = (
        update(User.__table__)
        .where(User.public_id == public_id)
        .values(is_email_verified=True)
    )
    await database.execute(query)
    return await get_user_by_public_id(public_id)


async def update_user_active_status(public_id: str, is_active: bool):
    """Activate or deactivate a user."""
    query = (
        update(User.__table__)
        .where(User.public_id == public_id)
        .values(is_active=is_active)
    )
    await database.execute(query)
    return await get_user_by_public_id(public_id)


async def update_user_email(public_id: str, new_email: str):
    """Update a user's email address."""
    query = (
        update(User.__table__)
        .where(User.public_id == public_id)
        .values(email=new_email, is_email_verified=False)
    )
    await database.execute(query)
    return await get_user_by_public_id(public_id)


async def update_user(public_id: str, data: dict):
    """Update a user and return the updated user."""
    if not data:
        return await get_user_by_public_id(public_id)

    query = update(User.__table__).where(User.public_id == public_id).values(**data)
    await database.execute(query)
    return await get_user_by_public_id(public_id)
