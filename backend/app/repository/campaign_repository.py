import datetime
from sqlalchemy import func
from app.models.campaign import CampaignStatus, Campaign
from app.repository.base_repository import BaseRepository


class CampaignRepository(BaseRepository[Campaign]):
    def __init__(self):
        super().__init__(Campaign)

    def get_by_instance_id(self, instance_id: int):
        return self.session.query(Campaign).filter(
            Campaign.gophish_instance_id == instance_id
            ).all()

    def count_by_instance_id(self, instance_id: int) -> int:
        return self.session.query(Campaign).filter(
            Campaign.gophish_instance_id == instance_id
        ).count()

    def get_campaign_counts_by_instance(self):
        return self.session.query(
            Campaign.gophish_instance_id,
            func.count(Campaign.id).label('campaign_count')
        ).group_by(Campaign.gophish_instance_id).all()

    def update_status_by_id(self, campaign_id: int, status: CampaignStatus):
        """Update campaign status by platform campaign ID."""
        campaign = self.get_by_id(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")

        update_data = {"status": status}
        if status == CampaignStatus.RUNNING:
            update_data["launched_at"] = datetime.datetime.utcnow()
        elif status == CampaignStatus.STOPPED:
            update_data["stopped_at"] = datetime.datetime.utcnow()
            
        return self.update_by_id(campaign_id, **update_data)
