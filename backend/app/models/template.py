from __future__ import annotations

from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, DateTime, UniqueConstraint, Index

from app.models.base import Base


class Template(Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    gophish_instance_id: Mapped[int] = mapped_column(ForeignKey("instances.id", ondelete="RESTRICT"), nullable=False)
    gophish_email_template_id: Mapped[int] = mapped_column(Integer, nullable=False)
    gophish_landing_page_id: Mapped[int] = mapped_column(Integer, nullable=False)
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("gophish_instance_id", "gophish_email_template_id", "gophish_landing_page_id", name="uq_template_map"),
        Index("ix_template_maps_instance_id", "gophish_instance_id"),
        Index("ix_template_maps_name", "name"),
    )

    def __repr__(self) -> str:
        return f"Template(id={self.id!r}, name={self.name!r}, email_template_id={self.gophish_email_template_id!r}, landing_page_id={self.gophish_landing_page_id!r})"
