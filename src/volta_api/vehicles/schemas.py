from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class VehicleStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class VehicleUserRole(str, Enum):
    DRIVER = "driver"
    OWNER = "owner"
    CONDUCTOR = "conductor"


# ===== Vehicle Schemas =====


class VehicleCreate(BaseModel):
    plate_number: str = Field(..., pattern=r"^T-\d{3}-[A-Za-z]{3}$")
    capacity: int = Field(..., gt=0)
    type: str = Field(..., min_length=1, max_length=50)
    status: VehicleStatus = VehicleStatus.ACTIVE
    route_id: Optional[int] = None
    is_sharing_location: bool = False


class VehicleUpdate(BaseModel):
    plate_number: str = Field(..., pattern=r"^T-\d{3}-[A-Za-z]{3}$")
    capacity: int = Field(..., gt=0)
    type: str = Field(..., min_length=1, max_length=50)
    status: Optional[VehicleStatus] = None
    route_id: Optional[int] = None
    is_sharing_location: Optional[bool] = None


class VehicleOut(BaseModel):
    plate_number: str
    capacity: int
    type: str
    status: str
    route_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class VehicleListOut(BaseModel):
    """Response model for paginated vehicle list."""

    items: list[VehicleOut]
    total: int
    page: int
    page_size: int
    total_pages: int


class VehicleDeleteConfirm(BaseModel):
    confirm: Literal["DELETE"]


# ===== Vehicle Route Schemas =====


class VehicleRouteAssign(BaseModel):
    route_id: Optional[int] = None


# ===== VehicleUser Schemas =====


class VehicleUserCreate(BaseModel):
    vehicle_id: int
    user_id: str = Field(..., min_length=11, max_length=11)
    role: VehicleUserRole


class VehicleUserUpdate(BaseModel):
    role: VehicleUserRole


class VehicleUserOut(BaseModel):
    vehicle_id: int
    user_id: str
    role: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
