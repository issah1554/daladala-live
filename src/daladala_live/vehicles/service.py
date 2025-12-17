from sqlalchemy import select, update, delete, func, and_, or_
from typing import Optional
from daladala_live.core.database import database
from .models import Vehicle, VehicleUser


# ===== Vehicle CRUD Operations =====


async def create_vehicle(data: dict):
    """Create a new vehicle and return the created vehicle."""
    query = Vehicle.__table__.insert().values(**data)
    vehicle_id = await database.execute(query)
    return await get_vehicle_by_id(vehicle_id)


async def get_vehicles(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    vehicle_type: Optional[str] = None,
    is_sharing_location: Optional[bool] = None,
):
    """Get all vehicles with optional filtering and pagination."""
    query = Vehicle.__table__.select()

    # Apply filters
    filters = []
    if status:
        filters.append(Vehicle.status == status)
    if vehicle_type:
        filters.append(Vehicle.type == vehicle_type)
    if is_sharing_location is not None:
        filters.append(Vehicle.is_sharing_location == is_sharing_location)

    if filters:
        query = query.where(and_(*filters))

    query = query.offset(skip).limit(limit)
    return await database.fetch_all(query)


async def get_vehicles_count(
    status: Optional[str] = None,
    vehicle_type: Optional[str] = None,
    is_sharing_location: Optional[bool] = None,
) -> int:
    """Get total count of vehicles with optional filtering."""
    query = select(func.count()).select_from(Vehicle.__table__)

    filters = []
    if status:
        filters.append(Vehicle.status == status)
    if vehicle_type:
        filters.append(Vehicle.type == vehicle_type)
    if is_sharing_location is not None:
        filters.append(Vehicle.is_sharing_location == is_sharing_location)

    if filters:
        query = query.where(and_(*filters))

    result = await database.fetch_one(query)
    return result[0] if result else 0


async def get_vehicle_by_id(vehicle_id: int):
    """Get a single vehicle by ID."""
    query = Vehicle.__table__.select().where(Vehicle.id == vehicle_id)
    return await database.fetch_one(query)


async def get_vehicle_by_plate_number(plate_number: str):
    """Get a single vehicle by plate number."""
    query = Vehicle.__table__.select().where(Vehicle.plate_number == plate_number)
    return await database.fetch_one(query)


async def search_vehicles(search_term: str, skip: int = 0, limit: int = 100):
    """Search vehicles by plate number or type."""
    search_pattern = f"%{search_term}%"
    query = (
        Vehicle.__table__.select()
        .where(
            or_(
                Vehicle.plate_number.ilike(search_pattern),
                Vehicle.type.ilike(search_pattern),
            )
        )
        .offset(skip)
        .limit(limit)
    )
    return await database.fetch_all(query)


async def update_vehicle(vehicle_id: int, data: dict):
    """Update a vehicle and return the updated vehicle."""
    if not data:
        return await get_vehicle_by_id(vehicle_id)

    query = update(Vehicle.__table__).where(Vehicle.id == vehicle_id).values(**data)
    await database.execute(query)
    return await get_vehicle_by_id(vehicle_id)


async def delete_vehicle(vehicle_id: int):
    """Delete a vehicle by ID."""
    # First delete related VehicleUser entries
    await delete_vehicle_users_by_vehicle(vehicle_id)

    query = delete(Vehicle.__table__).where(Vehicle.id == vehicle_id)
    await database.execute(query)
    return {"deleted": vehicle_id}


async def update_vehicle_location_sharing(vehicle_id: int, is_sharing: bool):
    """Toggle vehicle location sharing status."""
    query = (
        update(Vehicle.__table__)
        .where(Vehicle.id == vehicle_id)
        .values(is_sharing_location=is_sharing)
    )
    await database.execute(query)
    return await get_vehicle_by_id(vehicle_id)


# ===== VehicleUser CRUD Operations =====


async def assign_user_to_vehicle(data: dict):
    """Assign a user to a vehicle with a specific role."""
    query = VehicleUser.__table__.insert().values(**data)
    await database.execute(query)
    return await get_vehicle_user(data["vehicle_id"], data["user_id"])


async def get_vehicle_user(vehicle_id: int, user_id: str):
    """Get a specific vehicle-user assignment."""
    query = VehicleUser.__table__.select().where(
        and_(
            VehicleUser.vehicle_id == vehicle_id,
            VehicleUser.user_id == user_id,
        )
    )
    return await database.fetch_one(query)


async def get_users_by_vehicle(vehicle_id: int):
    """Get all users assigned to a vehicle."""
    query = VehicleUser.__table__.select().where(VehicleUser.vehicle_id == vehicle_id)
    return await database.fetch_all(query)


async def get_vehicles_by_user(user_id: str):
    """Get all vehicles assigned to a user."""
    query = VehicleUser.__table__.select().where(VehicleUser.user_id == user_id)
    return await database.fetch_all(query)


async def update_vehicle_user_role(vehicle_id: int, user_id: str, role: str):
    """Update a user's role for a specific vehicle."""
    query = (
        update(VehicleUser.__table__)
        .where(
            and_(
                VehicleUser.vehicle_id == vehicle_id,
                VehicleUser.user_id == user_id,
            )
        )
        .values(role=role)
    )
    await database.execute(query)
    return await get_vehicle_user(vehicle_id, user_id)


async def remove_user_from_vehicle(vehicle_id: int, user_id: str):
    """Remove a user assignment from a vehicle."""
    query = delete(VehicleUser.__table__).where(
        and_(
            VehicleUser.vehicle_id == vehicle_id,
            VehicleUser.user_id == user_id,
        )
    )
    await database.execute(query)
    return {"removed": {"vehicle_id": vehicle_id, "user_id": user_id}}


async def delete_vehicle_users_by_vehicle(vehicle_id: int):
    """Delete all user assignments for a vehicle."""
    query = delete(VehicleUser.__table__).where(VehicleUser.vehicle_id == vehicle_id)
    await database.execute(query)
