from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RouteNodeCreate(BaseModel):
    node_id: int
    seq_no: int = Field(..., gt=0)
    distance_km_from_start: Optional[float] = None
    travel_minutes_from_start: Optional[int] = Field(None, ge=0)


class RouteNodeOut(BaseModel):
    id: int
    route_id: int
    node_id: int
    seq_no: int
    distance_km_from_start: Optional[float] = None
    travel_minutes_from_start: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RouteNodeUpdate(BaseModel):
    seq_no: Optional[int] = Field(None, gt=0)
    distance_km_from_start: Optional[float] = None
    travel_minutes_from_start: Optional[int] = Field(None, ge=0)


class RouteCreate(BaseModel):
    code: Optional[str] = Field(None, max_length=50)
    name: str = Field(..., min_length=1, max_length=150)
    created_by: Optional[int] = None
    is_active: bool = True


class RouteUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    created_by: Optional[int] = None
    is_active: Optional[bool] = None


class RouteOut(BaseModel):
    id: int
    code: Optional[str] = None
    name: str
    created_by: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RouteListOut(BaseModel):
    items: list[RouteOut]
    total: int
    page: int
    page_size: int
    total_pages: int


class RouteNodeListOut(BaseModel):
    items: list[RouteNodeOut]
    total: int
