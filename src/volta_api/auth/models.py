from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from volta_api.core.database import Base
from volta_api.utils import generate_base64_id


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(11), ForeignKey("users.id"), nullable=False)
    token = Column(String(255), nullable=False)
    is_used = Column(Boolean, default=False)
    token_type = Column(
        String(50), nullable=False
    )  # access, refresh, password_reset, email_verification
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(255), nullable=False, unique=True)
    revoked_at = Column(DateTime(timezone=True), server_default=func.now())
