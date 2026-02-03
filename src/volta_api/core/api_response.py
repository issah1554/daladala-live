from datetime import datetime, timezone
from typing import Any, Mapping, Optional

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from pydantic.config import ConfigDict


class ApiResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    success: bool
    timestamp: int
    message: Optional[str] = None
    data: Optional[Any] = None
    meta: Optional[Any] = None


class PaginationMeta(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int


def x() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def _normalize_data(value: Any) -> Any:
    if isinstance(value, Mapping):
        return dict(value)
    if isinstance(value, (list, tuple, set)):
        return [_normalize_data(item) for item in value]
    return value


def success_response(*, message: str | None = None, data: Any = None, meta: Any = None):
    payload: dict[str, Any] = {
        "success": True,
        "timestamp": _unix_ms_timestamp(),
    }
    if message is not None:
        payload["message"] = message
    if data is not None:
        payload["data"] = _normalize_data(data)
    if meta is not None:
        payload["meta"] = meta
    return jsonable_encoder(payload)


def error_response(message: str):
    return jsonable_encoder({
        "success": False,
        "timestamp": _unix_ms_timestamp(),
        "message": message,
    })
