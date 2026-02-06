import math

from fastapi import APIRouter, Depends, HTTPException, Query
from pymysql.err import IntegrityError as PyMySQLIntegrityError
from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError

from volta_api.auth.dependencies import get_current_active_user
from volta_api.core.api_response import ApiResponse, PaginationMeta, success_response
from .schemas import (
    RouteCreate,
    RouteNodeCreate,
    RouteNodeUpdate,
    RouteNodesDelete,
    RouteUpdate,
)
from .service import (
    create_route,
    create_route_node,
    delete_route,
    delete_route_node,
    delete_route_nodes,
    delete_route_nodes_by_ids,
    get_existing_node_ids,
    get_route_by_id,
    get_routes,
    get_routes_count,
    get_route_node_by_id,
    get_route_nodes_by_ids,
    get_route_nodes,
    replace_route_nodes,
    update_route,
    update_route_node,
)

router = APIRouter(
    prefix="/volta/api/routes",
    tags=["routes"],
    dependencies=[Depends(get_current_active_user)],
)


@router.get("", response_model=ApiResponse, response_model_exclude_none=True)
async def list_routes(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    is_active: bool | None = Query(None, description="Filter by active status"),
):
    skip = (page - 1) * page_size
    routes = await get_routes(skip=skip, limit=page_size, is_active=is_active)
    total = await get_routes_count(is_active=is_active)
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    meta = PaginationMeta(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
    return success_response(data=routes, meta=meta)


@router.post("", response_model=ApiResponse, response_model_exclude_none=True, status_code=201)
async def register_route(
    payload: RouteCreate,
    current_user=Depends(get_current_active_user),
):
    data = payload.model_dump()
    data["created_by"] = current_user.id
    try:
        route = await create_route(data)
    except (SQLAlchemyIntegrityError, PyMySQLIntegrityError) as exc:
        if "uq_routes_code" in str(exc):
            raise HTTPException(status_code=400, detail="Route code already exists") from exc
        raise
    return success_response(message="Route created", data=route)


@router.put("/{route_id}", response_model=ApiResponse, response_model_exclude_none=True)
async def edit_route(route_id: int, payload: RouteUpdate):
    route = await get_route_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    update_data = payload.model_dump(exclude_unset=True)
    updated = await update_route(route_id, update_data)
    return success_response(message="Route updated", data=updated)


@router.get("/{route_id}", response_model=ApiResponse, response_model_exclude_none=True)
async def read_route(route_id: int):
    route = await get_route_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return success_response(data=route)


@router.delete("/{route_id}", response_model=ApiResponse, response_model_exclude_none=True)
async def remove_route(route_id: int):
    route = await get_route_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    await delete_route(route_id)
    return success_response(message="Route deleted")


@router.get("/{route_id}/nodes", response_model=ApiResponse, response_model_exclude_none=True)
async def list_route_nodes(route_id: int):
    route = await get_route_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    nodes = await get_route_nodes(route_id)
    total = len(nodes)
    meta = PaginationMeta(
        total=total,
        page=1,
        page_size=total,
        total_pages=1,
    )
    return success_response(data=nodes, meta=meta)


@router.post(
    "/{route_id}/nodes",
    response_model=ApiResponse,
    response_model_exclude_none=True,
    status_code=201,
)
async def add_route_node(route_id: int, payload: RouteNodeCreate):
    route = await get_route_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    existing_nodes = await get_existing_node_ids([payload.node_id])
    if payload.node_id not in existing_nodes:
        raise HTTPException(status_code=400, detail="Node does not exist")

    route_node = await create_route_node(route_id, payload.model_dump())
    return success_response(message="Route node created", data=route_node)


@router.put("/{route_id}/nodes", response_model=ApiResponse, response_model_exclude_none=True)
async def replace_route_nodes_endpoint(route_id: int, payload: list[RouteNodeCreate]):
    route = await get_route_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    node_ids = [item.node_id for item in payload]
    existing_nodes = await get_existing_node_ids(node_ids)
    missing = [node_id for node_id in node_ids if node_id not in existing_nodes]
    if missing:
        raise HTTPException(
            status_code=400, detail={"message": "Nodes not found", "missing": missing}
        )

    nodes = await replace_route_nodes(
        route_id, [item.model_dump() for item in payload]
    )
    meta = PaginationMeta(
        total=len(nodes),
        page=1,
        page_size=len(nodes),
        total_pages=1,
    )
    return success_response(message="Route nodes updated", data=nodes, meta=meta)


@router.put(
    "/{route_id}/nodes/{route_node_id}",
    response_model=ApiResponse,
    response_model_exclude_none=True,
)
async def edit_route_node(
    route_id: int, route_node_id: int, payload: RouteNodeUpdate
):
    route = await get_route_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    route_node = await get_route_node_by_id(route_node_id)
    if not route_node or route_node["route_id"] != route_id:
        raise HTTPException(status_code=404, detail="Route node not found")

    updated = await update_route_node(
        route_node_id, payload.model_dump(exclude_unset=True)
    )
    return success_response(message="Route node updated", data=updated)


@router.delete(
    "/{route_id}/nodes/{route_node_id}",
    response_model=ApiResponse,
    response_model_exclude_none=True,
)
async def remove_route_node(route_id: int, route_node_id: int):
    route = await get_route_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    route_node = await get_route_node_by_id(route_node_id)
    if not route_node or route_node["route_id"] != route_id:
        raise HTTPException(status_code=404, detail="Route node not found")

    await delete_route_node(route_node_id)
    return success_response(message="Route node deleted")


@router.delete("/{route_id}/nodes", response_model=ApiResponse, response_model_exclude_none=True)
async def remove_route_nodes(route_id: int, payload: RouteNodesDelete):
    route = await get_route_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail={"message": "Route not found"})

    existing_nodes = await get_route_nodes_by_ids(payload.route_node_ids)
    existing_ids = {node["id"] for node in existing_nodes}
    missing = [node_id for node_id in payload.route_node_ids if node_id not in existing_ids]
    if missing:
        raise HTTPException(
            status_code=404,
            detail={"message": "Route nodes not found", "missing": missing},
        )

    mismatched = [
        node["id"] for node in existing_nodes if node["route_id"] != route_id
    ]
    if mismatched:
        raise HTTPException(
            status_code=400,
            detail={"message": "Route nodes do not belong to route", "mismatched": mismatched},
        )

    await delete_route_nodes_by_ids(route_id, payload.route_node_ids)
    return success_response(message="Route nodes deleted")
