import logging
from gophish import Gophish
from typing import Optional
from app.models.instance import Instance

logger = logging.getLogger(__name__)


class GophishService:
    def __init__(self):
        self._clients = {}

    def get_client_for_instance(self, instance: Instance, verify: bool = False):
        cache_key = instance.id
        
        if cache_key not in self._clients:
            try:
                logger.info(f"Creating Gophish client for instance '{instance.name}' at {instance.base_url}")
                self._clients[cache_key] = Gophish(
                    instance.api_key,
                    host=instance.base_url,
                    verify=verify
                )
            except Exception as e:
                logger.error(f"Failed to create Gophish client for instance {instance.id}: {e}", exc_info=True)
                raise
        
        return self._clients[cache_key]
    
    def clear_client_cache(self, instance_id: Optional[int] = None):
        if instance_id:
            self._clients.pop(instance_id, None)
            logger.info(f"Cleared cached client for instance {instance_id}")
        else:
            self._clients.clear()
            logger.info("Cleared all cached Gophish clients")
