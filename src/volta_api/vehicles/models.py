from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from volta_api.core.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    plate_number = Column(String(20), unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)  # active, inactive, maintenance
    is_sharing_location = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )


class VehicleUser(Base):
    __tablename__ = "vehicles_users"

    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), primary_key=True)
    user_id = Column(String(11), ForeignKey("users.public_id"), primary_key=True)
    role = Column(String(20), nullable=False)  # driver, owner, conductor
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )
