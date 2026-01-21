from app.models.campaign_stats import CampaignStats
from app.repository.base_repository import BaseRepository


class CampaignStatsRepository(BaseRepository[CampaignStats]):
    def __init__(self):
        super().__init__(CampaignStats)

    def get_by_campaign_id(self, campaign_id: int):
        return self.session.query(CampaignStats).filter(
            CampaignStats.campaign_id == campaign_id
        ).first()

    def update_or_create(self, campaign_id: int, **stats_data):
        """Update existing stats or create new ones for a campaign."""
        stats = self.get_by_campaign_id(campaign_id)
        if stats:
            for key, value in stats_data.items():
                setattr(stats, key, value)
        else:
            stats = CampaignStats(campaign_id=campaign_id, **stats_data)
            self.session.add(stats)

        self.session.commit()
        return stats
