from sqlalchemy import BigInteger, Column, DateTime, Index, Numeric, String, text
from sqlalchemy.sql import func
from volta_api.core.database import Base


class Node(Base):
    __tablename__ = "nodes"
    __table_args__ = (
        Index("idx_nodes_lat_lng", "latitude", "longitude"),
        Index("idx_nodes_name", "name"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    latitude = Column(Numeric(10, 7), nullable=False)
    longitude = Column(Numeric(10, 7), nullable=False)
    type = Column(
        String(20),
        nullable=False,
        default="station",
        server_default=text("'station'"),
    )
    status = Column(
        String(20),
        nullable=False,
        default="active",
        server_default=text("'active'"),
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
