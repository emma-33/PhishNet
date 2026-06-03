import logging
from typing import Optional
from app.models.instance import Instance
from app.repository.instance_repository import InstanceRepository
from app.repository.campaign_repository import CampaignRepository

logger = logging.getLogger(__name__)


class LoadBalancerService:
    def __init__(self):
        self._instance_repository = None
        self._campaign_repository = None

    @property
    def instance_repository(self):
        if self._instance_repository is None:
            self._instance_repository = InstanceRepository()
        return self._instance_repository

    @property
    def campaign_repository(self):
        if self._campaign_repository is None:
            self._campaign_repository = CampaignRepository()
        return self._campaign_repository

    def select_instance_for_load_balancing(self) -> Optional[Instance]:
        active_instances = self.instance_repository.get_active()
        
        if not active_instances:
            logger.warning("No active Gophish instances found")
            return None

        if len(active_instances) == 1:
            return active_instances[0]

        campaign_counts = {
            instance_id: count 
            for instance_id, count in self.campaign_repository.get_campaign_counts_by_instance()
        }

        selected_instance = None
        min_campaigns = float('inf')

        for instance in active_instances:
            campaign_count = campaign_counts.get(instance.id, 0)
            if campaign_count < min_campaigns:
                min_campaigns = campaign_count
                selected_instance = instance

        if selected_instance is None:
            selected_instance = active_instances[0]

        logger.info(
            f"Selected instance '{selected_instance.name}' (ID: {selected_instance.id}) "
            f"with {min_campaigns} campaigns"
        )
        
        return selected_instance
