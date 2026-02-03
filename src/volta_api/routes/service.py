from typing import Optional

from sqlalchemy import delete, func, select, update

from volta_api.core.database import database
from .models import Route, RouteNode
from volta_api.nodes.models import Node


async def create_route(data: dict):
    query = Route.__table__.insert().values(**data)
    route_id = await database.execute(query)
    return await get_route_by_id(route_id)


async def get_route_by_id(route_id: int):
    query = Route.__table__.select().where(Route.id == route_id)
    return await database.fetch_one(query)


async def get_routes(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
):
    query = Route.__table__.select()

    if is_active is not None:
        query = query.where(Route.is_active == is_active)

    query = query.offset(skip).limit(limit)
    return await database.fetch_all(query)


async def get_routes_count(is_active: Optional[bool] = None) -> int:
    query = select(func.count()).select_from(Route.__table__)

    if is_active is not None:
        query = query.where(Route.is_active == is_active)

    result = await database.fetch_one(query)
    return result[0] if result else 0


async def get_route_nodes(route_id: int):
    query = (
        RouteNode.__table__
        .select()
        .where(RouteNode.route_id == route_id)
        .order_by(RouteNode.seq_no)
    )
    return await database.fetch_all(query)


async def update_route(route_id: int, data: dict):
    if not data:
        return await get_route_by_id(route_id)

    query = update(Route.__table__).where(Route.id == route_id).values(**data)
    await database.execute(query)
    return await get_route_by_id(route_id)


async def delete_route(route_id: int):
    async with database.transaction():
        delete_nodes_query = delete(RouteNode.__table__).where(
            RouteNode.route_id == route_id
        )
        await database.execute(delete_nodes_query)

        delete_route_query = delete(Route.__table__).where(Route.id == route_id)
        await database.execute(delete_route_query)

    return {"deleted": route_id}


async def create_route_node(route_id: int, data: dict):
    query = RouteNode.__table__.insert().values(route_id=route_id, **data)
    route_node_id = await database.execute(query)
    return await get_route_node_by_id(route_node_id)


async def get_route_node_by_id(route_node_id: int):
    query = RouteNode.__table__.select().where(RouteNode.id == route_node_id)
    return await database.fetch_one(query)


async def update_route_node(route_node_id: int, data: dict):
    if not data:
        return await get_route_node_by_id(route_node_id)

    query = (
        update(RouteNode.__table__)
        .where(RouteNode.id == route_node_id)
        .values(**data)
    )
    await database.execute(query)
    return await get_route_node_by_id(route_node_id)


async def delete_route_node(route_node_id: int):
    query = delete(RouteNode.__table__).where(RouteNode.id == route_node_id)
    await database.execute(query)
    return {"deleted": route_node_id}


async def replace_route_nodes(route_id: int, nodes: list[dict]):
    async with database.transaction():
        delete_query = delete(RouteNode.__table__).where(RouteNode.route_id == route_id)
        await database.execute(delete_query)

        if nodes:
            nodes_payload = [{"route_id": route_id, **node} for node in nodes]
            await database.execute_many(RouteNode.__table__.insert(), nodes_payload)

    return await get_route_nodes(route_id)


async def get_existing_node_ids(node_ids: list[int]) -> set[int]:
    if not node_ids:
        return set()

    query = select(Node.id).where(Node.id.in_(node_ids))
    rows = await database.fetch_all(query)
    return {row["id"] for row in rows}
