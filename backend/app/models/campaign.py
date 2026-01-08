from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, String, Integer, ForeignKey, DateTime, JSON, UniqueConstraint, Index, Enum as SQLEnum

from app.models.base import Base


class CampaignStatus(str, Enum):
    """Campaign status"""
    DRAFT = "draft"
    RUNNING = "running"
    STOPPED = "stopped"
    ARCHIVED = "archived"


class Campaign(Base):
    """Platform campaign model"""
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    gophish_instance_id: Mapped[int] = mapped_column(ForeignKey("instances.id", ondelete="RESTRICT"), nullable=False)
    gophish_campaign_id: Mapped[int] = mapped_column(Integer, nullable=False)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[CampaignStatus] = mapped_column(SQLEnum(CampaignStatus), default=CampaignStatus.DRAFT, nullable=False)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    template_id: Mapped[Optional[int]] = mapped_column(ForeignKey("templates.id", ondelete="RESTRICT"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    launched_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    stopped_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    meta: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (
        UniqueConstraint("tenant_id", "gophish_instance_id", "gophish_campaign_id", name="uq_campaign_gophish_map"),
        Index("ix_campaigns_tenant_id", "tenant_id"),
        Index("ix_campaigns_instance_id", "gophish_instance_id"),
    )

    def __repr__(self) -> str:
        return f"Campaign(id={self.id!r}, name={self.name!r}, gophish_campaign_id={self.gophish_campaign_id!r})"
