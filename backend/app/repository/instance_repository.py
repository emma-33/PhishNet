from typing import List
from app.models.instance import Instance
from app.repository.base_repository import BaseRepository

class InstanceRepository(BaseRepository[Instance]):
    """Repository for Gophish instances."""

    def __init__(self):
        super().__init__(Instance)

    def get_active(self) -> List[Instance]:
        """Get all active instances"""
        return self.session.query(self.model).filter(
            self.model.is_active == True
        ).all()
    
    def deactivate(self, instance_id: int):
        """Deactivate a instance"""
        return self.update_by_id(instance_id, is_active=False)

    def activate(self, instance_id: int):
        """Activate a instance"""
        return self.update_by_id(instance_id, is_active=True)