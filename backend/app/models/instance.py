from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Boolean, DateTime, UniqueConstraint, Index

from app.models.base import Base


class Instance(Base):
    """Gophish instance model"""
    __tablename__ = "instances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)

    api_key: Mapped[str] = mapped_column(Text, nullable=False)
    redirect_url: Mapped[str] = mapped_column(String(500), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        UniqueConstraint("name", name="uq_gophish_instance_name"),
        Index("ix_gophish_instances_name", "name"),
    )

    def __repr__(self) -> str:
        return f"Instance(id={self.id!r}, name={self.name!r}, base_url={self.base_url!r})"
