from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel


class ApiResponse(BaseModel):
    success: bool
    timestamp: str
    message: Optional[str] = None
    data: Optional[Any] = None
    meta: Optional[Any] = None


class PaginationMeta(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int


def _iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def success_response(*, message: str | None = None, data: Any = None, meta: Any = None):
    payload: dict[str, Any] = {
        "success": True,
        "timestamp": _iso_timestamp(),
    }
    if message is not None:
        payload["message"] = message
    if data is not None:
        payload["data"] = data
    if meta is not None:
        payload["meta"] = meta
    return payload


def error_response(message: str):
    return {
        "success": False,
        "timestamp": _iso_timestamp(),
        "message": message,
    }
