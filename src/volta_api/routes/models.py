from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.sql import func

from volta_api.core.database import Base


class Route(Base):
    __tablename__ = "routes"
    __table_args__ = (
        UniqueConstraint("code", name="uq_routes_code"),
        Index("idx_routes_created_by", "created_by"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String(50), nullable=True)
    name = Column(String(150), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=text("1"), default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )


class RouteNode(Base):
    __tablename__ = "route_nodes"
    __table_args__ = (
        UniqueConstraint("route_id", "seq_no", name="uq_route_nodes_route_seq"),
        UniqueConstraint("route_id", "node_id", name="uq_route_nodes_route_node"),
        Index("idx_route_nodes_node", "node_id"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    route_id = Column(
        BigInteger, ForeignKey("routes.id", ondelete="CASCADE"), nullable=False
    )
    node_id = Column(
        BigInteger, ForeignKey("nodes.id", ondelete="RESTRICT"), nullable=False
    )
    seq_no = Column(Integer, nullable=False)
    distance_km_from_start = Column(Numeric(10, 3), nullable=True)
    travel_minutes_from_start = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
