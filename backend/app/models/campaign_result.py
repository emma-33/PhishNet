from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey

from app.models.base import Base


class CampaignResult(Base):
    """Local storage for individual target results in a campaign"""
    __tablename__ = "campaign_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)

    email: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[str] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False) # e.g., "Sent", "Opened", "Clicked", "Submitted Data"

    modified_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationship back to campaign
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="results")

    def __repr__(self) -> str:
        return f"CampaignResult(campaign_id={self.campaign_id!r}, email={self.email!r}, status={self.status!r})"
