import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from volta_api.auth.dependencies import get_current_active_user
from .schemas import (
    NodeCreate,
    NodeBulkDeleteOut,
    NodeBulkDeleteRequest,
    NodeListOut,
    NodeOut,
    NodeStatus,
    NodeType,
    NodeUpdate,
)
from .service import (
    create_node,
    delete_node,
    delete_nodes,
    get_node_by_id,
    get_nodes,
    get_nodes_count,
    search_nodes,
    update_node,
)

router = APIRouter(
    prefix="/volta/api/nodes",
    tags=["nodes"],
    dependencies=[Depends(get_current_active_user)],
)


@router.post("", response_model=NodeOut, status_code=201)
async def register_node(payload: NodeCreate):
    node = await create_node(payload.model_dump())
    return node


@router.get("", response_model=NodeListOut)
async def list_nodes(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[NodeStatus] = Query(None, description="Filter by status"),
    node_type: Optional[NodeType] = Query(None, description="Filter by node type"),
):
    skip = (page - 1) * page_size
    status_value = status.value if status else None
    node_type_value = node_type.value if node_type else None

    nodes = await get_nodes(
        skip=skip,
        limit=page_size,
        status=status_value,
        node_type=node_type_value,
    )

    total = await get_nodes_count(
        status=status_value,
        node_type=node_type_value,
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return NodeListOut(
        items=nodes,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/search", response_model=list[NodeOut])
async def search_nodes_endpoint(
    q: str = Query(..., min_length=1, description="Search term"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    skip = (page - 1) * page_size
    nodes = await search_nodes(search_term=q, skip=skip, limit=page_size)
    return nodes


@router.get("/{node_id}", response_model=NodeOut)
async def read_node(node_id: int):
    node = await get_node_by_id(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


@router.put("/{node_id}", response_model=NodeOut)
async def edit_node(node_id: int, payload: NodeUpdate):
    node = await get_node_by_id(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "status" in update_data and update_data["status"]:
        update_data["status"] = update_data["status"].value
    if "type" in update_data and update_data["type"]:
        update_data["type"] = update_data["type"].value

    updated = await update_node(node_id, update_data)
    return updated


@router.delete("/{node_id}")
async def remove_node(node_id: int):
    node = await get_node_by_id(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return await delete_node(node_id)


@router.delete("", response_model=NodeBulkDeleteOut)
async def remove_nodes(payload: NodeBulkDeleteRequest):
    result = await delete_nodes(payload.ids)
    return result
