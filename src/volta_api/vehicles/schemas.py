from pydantic import BaseModel, Field
from typing import Optional
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
    plate_number: str = Field(..., min_length=1, max_length=20)
    capacity: int = Field(..., gt=0)
    type: str = Field(..., min_length=1, max_length=50)
    status: VehicleStatus = VehicleStatus.ACTIVE
    is_sharing_location: bool = False


class VehicleUpdate(BaseModel):
    plate_number: Optional[str] = Field(None, min_length=1, max_length=20)
    capacity: Optional[int] = Field(None, gt=0)
    type: Optional[str] = Field(None, min_length=1, max_length=50)
    status: Optional[VehicleStatus] = None
    is_sharing_location: Optional[bool] = None


class VehicleOut(BaseModel):
    id: int
    plate_number: str
    capacity: int
    type: str
    status: str
    is_sharing_location: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VehicleListOut(BaseModel):
    """Response model for paginated vehicle list."""

    items: list[VehicleOut]
    total: int
    page: int
    page_size: int
    total_pages: int


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
