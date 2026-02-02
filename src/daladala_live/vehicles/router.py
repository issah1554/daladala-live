import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from daladala_live.auth.dependencies import get_current_active_user
from .schemas import (
    VehicleCreate,
    VehicleUpdate,
    VehicleOut,
    VehicleListOut,
    VehicleStatus,
    VehicleUserCreate,
    VehicleUserUpdate,
    VehicleUserOut,
)
from .service import (
    create_vehicle,
    get_vehicles,
    get_vehicles_count,
    get_vehicle_by_id,
    get_vehicle_by_plate_number,
    search_vehicles,
    update_vehicle,
    delete_vehicle,
    update_vehicle_location_sharing,
    assign_user_to_vehicle,
    get_vehicle_user,
    get_users_by_vehicle,
    get_vehicles_by_user,
    update_vehicle_user_role,
    remove_user_from_vehicle,
)

router = APIRouter(
    prefix="/volta/api/vehicles",
    tags=["vehicles"],
    dependencies=[Depends(get_current_active_user)],
)

    
# ===== Vehicle Endpoints =====


@router.post("", response_model=VehicleOut, status_code=201)
async def register_vehicle(payload: VehicleCreate):
    """Create a new vehicle."""
    # Check for duplicate plate number
    existing = await get_vehicle_by_plate_number(payload.plate_number)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Vehicle with plate number '{payload.plate_number}' already exists",
        )

    vehicle = await create_vehicle(payload.model_dump())
    return vehicle


@router.get("", response_model=VehicleListOut)
async def list_vehicles(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[VehicleStatus] = Query(None, description="Filter by status"),
    vehicle_type: Optional[str] = Query(None, description="Filter by vehicle type"),
    is_sharing_location: Optional[bool] = Query(
        None, description="Filter by location sharing status"
    ),
):
    """List all vehicles with pagination and filtering."""
    skip = (page - 1) * page_size
    status_value = status.value if status else None

    vehicles = await get_vehicles(
        skip=skip,
        limit=page_size,
        status=status_value,
        vehicle_type=vehicle_type,
        is_sharing_location=is_sharing_location,
    )

    total = await get_vehicles_count(
        status=status_value,
        vehicle_type=vehicle_type,
        is_sharing_location=is_sharing_location,
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return VehicleListOut(
        items=vehicles,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/search", response_model=list[VehicleOut])
async def search_vehicles_endpoint(
    q: str = Query(..., min_length=1, description="Search term"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Search vehicles by plate number or type."""
    skip = (page - 1) * page_size
    vehicles = await search_vehicles(search_term=q, skip=skip, limit=page_size)
    return vehicles


@router.get("/plate/{plate_number}", response_model=VehicleOut)
async def read_vehicle_by_plate(plate_number: str):
    """Get a vehicle by its plate number."""
    vehicle = await get_vehicle_by_plate_number(plate_number)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.get("/{vehicle_id}", response_model=VehicleOut)
async def read_vehicle(vehicle_id: int):
    """Get a vehicle by ID."""
    vehicle = await get_vehicle_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.put("/{vehicle_id}", response_model=VehicleOut)
async def edit_vehicle(vehicle_id: int, payload: VehicleUpdate):
    """Update a vehicle."""
    vehicle = await get_vehicle_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # Check for duplicate plate number if updating plate_number
    if payload.plate_number and payload.plate_number != vehicle.plate_number:
        existing = await get_vehicle_by_plate_number(payload.plate_number)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Vehicle with plate number '{payload.plate_number}' already exists",
            )

    update_data = payload.model_dump(exclude_unset=True)
    # Convert enum to string value if present
    if "status" in update_data and update_data["status"]:
        update_data["status"] = update_data["status"].value

    updated = await update_vehicle(vehicle_id, update_data)
    return updated


@router.patch("/{vehicle_id}/location-sharing", response_model=VehicleOut)
async def toggle_location_sharing(vehicle_id: int, is_sharing: bool):
    """Toggle location sharing for a vehicle."""
    vehicle = await get_vehicle_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    updated = await update_vehicle_location_sharing(vehicle_id, is_sharing)
    return updated


@router.delete("/{vehicle_id}")
async def remove_vehicle(vehicle_id: int):
    """Delete a vehicle."""
    vehicle = await get_vehicle_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return await delete_vehicle(vehicle_id)


# ===== VehicleUser Endpoints =====


@router.post("/{vehicle_id}/users", response_model=VehicleUserOut, status_code=201)
async def assign_user(vehicle_id: int, payload: VehicleUserCreate):
    """Assign a user to a vehicle with a specific role."""
    # Verify vehicle exists
    vehicle = await get_vehicle_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # Check if user is already assigned
    existing = await get_vehicle_user(vehicle_id, payload.user_id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="User is already assigned to this vehicle",
        )

    assignment_data = {
        "vehicle_id": vehicle_id,
        "user_id": payload.user_id,
        "role": payload.role.value,
    }
    assignment = await assign_user_to_vehicle(assignment_data)
    return assignment


@router.get("/{vehicle_id}/users", response_model=list[VehicleUserOut])
async def list_vehicle_users(vehicle_id: int):
    """Get all users assigned to a vehicle."""
    vehicle = await get_vehicle_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    users = await get_users_by_vehicle(vehicle_id)
    return users


@router.get("/users/{user_id}/vehicles", response_model=list[VehicleUserOut])
async def list_user_vehicles(user_id: str):
    """Get all vehicles assigned to a user."""
    vehicles = await get_vehicles_by_user(user_id)
    return vehicles


@router.put("/{vehicle_id}/users/{user_id}", response_model=VehicleUserOut)
async def update_user_role(vehicle_id: int, user_id: str, payload: VehicleUserUpdate):
    """Update a user's role for a specific vehicle."""
    # Verify assignment exists
    assignment = await get_vehicle_user(vehicle_id, user_id)
    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="User is not assigned to this vehicle",
        )

    updated = await update_vehicle_user_role(vehicle_id, user_id, payload.role.value)
    return updated


@router.delete("/{vehicle_id}/users/{user_id}")
async def unassign_user(vehicle_id: int, user_id: str):
    """Remove a user assignment from a vehicle."""
    # Verify assignment exists
    assignment = await get_vehicle_user(vehicle_id, user_id)
    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="User is not assigned to this vehicle",
        )

    return await remove_user_from_vehicle(vehicle_id, user_id)
