from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    STATION = "station"
    TERMINAL = "terminal"
    LANDMARK = "landmark"
    JUNCTION = "junction"


class NodeStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class NodeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    latitude: float
    longitude: float
    type: NodeType = NodeType.STATION
    status: NodeStatus = NodeStatus.ACTIVE


class NodeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    type: Optional[NodeType] = None
    status: Optional[NodeStatus] = None


class NodeOut(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    type: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class NodeListOut(BaseModel):
    items: list[NodeOut]
    total: int
    page: int
    page_size: int
    total_pages: int


class NodeBulkDeleteRequest(BaseModel):
    ids: list[int] = Field(..., min_length=1)


class NodeBulkDeleteOut(BaseModel):
    deleted: list[int]
    missing: list[int]
    count: int
