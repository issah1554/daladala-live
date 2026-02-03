from typing import Optional

from sqlalchemy import and_, delete, func, select, update

from volta_api.core.database import database
from .models import Node


async def create_node(data: dict):
    query = Node.__table__.insert().values(**data)
    node_id = await database.execute(query)
    return await get_node_by_id(node_id)


async def get_nodes(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    node_type: Optional[str] = None,
):
    query = Node.__table__.select()

    filters = []
    if status:
        filters.append(Node.status == status)
    if node_type:
        filters.append(Node.type == node_type)

    if filters:
        query = query.where(and_(*filters))

    query = query.offset(skip).limit(limit)
    return await database.fetch_all(query)


async def get_nodes_count(
    status: Optional[str] = None,
    node_type: Optional[str] = None,
) -> int:
    query = select(func.count()).select_from(Node.__table__)

    filters = []
    if status:
        filters.append(Node.status == status)
    if node_type:
        filters.append(Node.type == node_type)

    if filters:
        query = query.where(and_(*filters))

    result = await database.fetch_one(query)
    return result[0] if result else 0


async def get_node_by_id(node_id: int):
    query = Node.__table__.select().where(Node.id == node_id)
    return await database.fetch_one(query)


async def search_nodes(search_term: str, skip: int = 0, limit: int = 100):
    search_pattern = f"%{search_term}%"
    query = (
        Node.__table__.select()
        .where(Node.name.ilike(search_pattern))
        .offset(skip)
        .limit(limit)
    )
    return await database.fetch_all(query)


async def update_node(node_id: int, data: dict):
    if not data:
        return await get_node_by_id(node_id)

    query = update(Node.__table__).where(Node.id == node_id).values(**data)
    await database.execute(query)
    return await get_node_by_id(node_id)


async def delete_node(node_id: int):
    query = delete(Node.__table__).where(Node.id == node_id)
    await database.execute(query)
    return {"deleted": node_id}


async def delete_nodes(node_ids: list[int]):
    query = select(Node.id).where(Node.id.in_(node_ids))
    rows = await database.fetch_all(query)
    existing_ids = {row["id"] for row in rows}

    if existing_ids:
        delete_query = delete(Node.__table__).where(Node.id.in_(existing_ids))
        await database.execute(delete_query)

    deleted = [node_id for node_id in node_ids if node_id in existing_ids]
    missing = [node_id for node_id in node_ids if node_id not in existing_ids]

    return {"deleted": deleted, "missing": missing, "count": len(deleted)}
