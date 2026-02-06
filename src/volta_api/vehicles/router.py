import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from volta_api.auth.dependencies import get_current_active_user, get_current_admin_user
from volta_api.core.api_response import ApiResponse, PaginationMeta, success_response
from .schemas import (
    VehicleCreate,
    VehicleUpdate,
    VehicleStatus,
    VehicleUserCreate,
    VehicleUserUpdate,
    VehicleDeleteConfirm,
    VehicleUserRole,
)
from .service import (
    create_vehicle,
    get_vehicles_for_user,
    get_vehicles_count_for_user,
    get_vehicle_by_id_for_user,
    get_vehicle_by_plate_number,
    get_vehicle_by_plate_number_for_user,
    search_vehicles_for_user,
    get_vehicles_with_owners,
    get_vehicles_count,
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

def _strip_vehicle_fields(vehicle: dict) -> dict:
    vehicle_payload = dict(vehicle)
    vehicle_payload.pop("id", None)
    vehicle_payload.pop("updated_at", None)
    vehicle_payload.pop("is_sharing_location", None)
    return vehicle_payload

    
# ===== Vehicle Endpoints =====


@router.post("", response_model=ApiResponse, response_model_exclude_none=True, status_code=201)
async def register_vehicle(
    payload: VehicleCreate,
    current_user=Depends(get_current_active_user),
):
    """Create a new vehicle."""
    # Check for duplicate plate number
    existing = await get_vehicle_by_plate_number(payload.plate_number)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Vehicle with plate number '{payload.plate_number}' already exists",
        )

    vehicle = await create_vehicle(payload.model_dump())
    await assign_user_to_vehicle(
        {
            "vehicle_id": vehicle.id,
            "user_id": current_user.public_id,
            "role": VehicleUserRole.OWNER.value,
        }
    )
    return success_response(message="Vehicle created", data=vehicle)


@router.get("", response_model=ApiResponse, response_model_exclude_none=True)
async def list_vehicles(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[VehicleStatus] = Query(None, description="Filter by status"),
    vehicle_type: Optional[str] = Query(None, description="Filter by vehicle type"),
    is_sharing_location: Optional[bool] = Query(
        None, description="Filter by location sharing status"
    ),
    current_user=Depends(get_current_active_user),
):
    """List all vehicles with pagination and filtering."""
    skip = (page - 1) * page_size
    status_value = status.value if status else None

    vehicles = await get_vehicles_for_user(
        user_id=current_user.public_id,
        skip=skip,
        limit=page_size,
        status=status_value,
        vehicle_type=vehicle_type,
        is_sharing_location=is_sharing_location,
    )

    total = await get_vehicles_count_for_user(
        user_id=current_user.public_id,
        status=status_value,
        vehicle_type=vehicle_type,
        is_sharing_location=is_sharing_location,
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    meta = PaginationMeta(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
    return success_response(
        data=[_strip_vehicle_fields(vehicle) for vehicle in vehicles], meta=meta
    )


@router.get(
    "/admin/with-owners",
    response_model=ApiResponse,
    response_model_exclude_none=True,
)
async def list_vehicles_with_owners(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[VehicleStatus] = Query(None, description="Filter by status"),
    vehicle_type: Optional[str] = Query(None, description="Filter by vehicle type"),
    is_sharing_location: Optional[bool] = Query(
        None, description="Filter by location sharing status"
    ),
    current_user=Depends(get_current_admin_user),
):
    """List all vehicles with owners (admin only)."""
    skip = (page - 1) * page_size
    status_value = status.value if status else None

    vehicles_with_owners = await get_vehicles_with_owners(
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

    data = []
    for item in vehicles_with_owners:
        vehicle_payload = _strip_vehicle_fields(item["vehicle"])
        vehicle_payload["owners"] = item["owners"]
        data.append(vehicle_payload)

    meta = PaginationMeta(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
    return success_response(data=data, meta=meta)


@router.get("/search", response_model=ApiResponse, response_model_exclude_none=True)
async def search_vehicles_endpoint(
    q: str = Query(..., min_length=1, description="Search term"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_active_user),
):
    """Search vehicles by plate number or type."""
    skip = (page - 1) * page_size
    vehicles = await search_vehicles_for_user(
        user_id=current_user.public_id,
        search_term=q,
        skip=skip,
        limit=page_size,
    )
    total = len(vehicles)
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    meta = PaginationMeta(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
    return success_response(
        data=[_strip_vehicle_fields(vehicle) for vehicle in vehicles], meta=meta
    )


@router.get("/plate/{plate_number}", response_model=ApiResponse, response_model_exclude_none=True)
async def read_vehicle_by_plate(
    plate_number: str,
    current_user=Depends(get_current_active_user),
):
    """Get a vehicle by its plate number."""
    vehicle = await get_vehicle_by_plate_number_for_user(
        plate_number, current_user.public_id
    )
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return success_response(data=_strip_vehicle_fields(vehicle))


@router.get("/{vehicle_id}", response_model=ApiResponse, response_model_exclude_none=True)
async def read_vehicle(
    vehicle_id: int,
    current_user=Depends(get_current_active_user),
):
    """Get a vehicle by ID."""
    vehicle = await get_vehicle_by_id_for_user(vehicle_id, current_user.public_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return success_response(data=_strip_vehicle_fields(vehicle))


@router.put("/{vehicle_id}", response_model=ApiResponse, response_model_exclude_none=True)
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
    return success_response(message="Vehicle updated", data=updated)


@router.patch(
    "/{vehicle_id}/location-sharing",
    response_model=ApiResponse,
    response_model_exclude_none=True,
)
async def toggle_location_sharing(vehicle_id: int, is_sharing: bool):
    """Toggle location sharing for a vehicle."""
    vehicle = await get_vehicle_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    updated = await update_vehicle_location_sharing(vehicle_id, is_sharing)
    return success_response(message="Vehicle updated", data=updated)


@router.delete(
    "/plate/{plate_number}",
    response_model=ApiResponse,
    response_model_exclude_none=True,
)
@router.delete(
    "/{plate_number}",
    response_model=ApiResponse,
    response_model_exclude_none=True,
)
async def remove_vehicle(
    plate_number: str,
    payload: VehicleDeleteConfirm,
    current_user=Depends(get_current_active_user),
):
    """Delete a vehicle by plate number."""
    vehicle = await get_vehicle_by_plate_number_for_user(
        plate_number, current_user.public_id
    )
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    await delete_vehicle(vehicle.id)
    return success_response(message="Vehicle deleted")


# ===== VehicleUser Endpoints =====


@router.post(
    "/{vehicle_id}/users",
    response_model=ApiResponse,
    response_model_exclude_none=True,
    status_code=201,
)
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
    return success_response(message="User assigned to vehicle", data=assignment)


@router.get("/{vehicle_id}/users", response_model=ApiResponse, response_model_exclude_none=True)
async def list_vehicle_users(vehicle_id: int):
    """Get all users assigned to a vehicle."""
    vehicle = await get_vehicle_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    users = await get_users_by_vehicle(vehicle_id)
    total = len(users)
    meta = PaginationMeta(
        total=total,
        page=1,
        page_size=total,
        total_pages=1,
    )
    return success_response(data=users, meta=meta)


@router.get("/users/{user_id}/vehicles", response_model=ApiResponse, response_model_exclude_none=True)
async def list_user_vehicles(
    user_id: str,
    current_user=Depends(get_current_active_user),
):
    """Get all vehicles assigned to a user."""
    if user_id != current_user.public_id:
        raise HTTPException(status_code=403, detail="Access denied")
    vehicles = await get_vehicles_by_user(user_id)
    total = len(vehicles)
    meta = PaginationMeta(
        total=total,
        page=1,
        page_size=total,
        total_pages=1,
    )
    return success_response(data=vehicles, meta=meta)


@router.put(
    "/{vehicle_id}/users/{user_id}",
    response_model=ApiResponse,
    response_model_exclude_none=True,
)
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
    return success_response(message="Vehicle user updated", data=updated)


@router.delete(
    "/{vehicle_id}/users/{user_id}",
    response_model=ApiResponse,
    response_model_exclude_none=True,
)
async def unassign_user(vehicle_id: int, user_id: str):
    """Remove a user assignment from a vehicle."""
    # Verify assignment exists
    assignment = await get_vehicle_user(vehicle_id, user_id)
    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="User is not assigned to this vehicle",
        )

    await remove_user_from_vehicle(vehicle_id, user_id)
    return success_response(message="User unassigned from vehicle")
