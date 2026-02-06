from datetime import datetime
from typing import Optional

import re

from pydantic import BaseModel, Field, field_validator

_LINESTRING_RE = re.compile(
    r"^LINESTRING\(\s*-?\d+(\.\d+)?\s+-?\d+(\.\d+)?"
    r"(\s*,\s*-?\d+(\.\d+)?\s+-?\d+(\.\d+)?)*\s*\)$",
    re.IGNORECASE,
)


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
    geometry: Optional[str] = None
    is_active: bool = True

    @field_validator("geometry")
    @classmethod
    def validate_geometry(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not _LINESTRING_RE.match(value.strip()):
            raise ValueError("geometry must be a WKT LINESTRING")
        return value.strip()


class RouteUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    geometry: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("geometry")
    @classmethod
    def validate_geometry(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not _LINESTRING_RE.match(value.strip()):
            raise ValueError("geometry must be a WKT LINESTRING")
        return value.strip()


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


class RouteNodesDelete(BaseModel):
    route_node_ids: list[int] = Field(..., min_length=1)
