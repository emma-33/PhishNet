import logging
from typing import Optional
from gophish.models import Group, User as GophishUser
from app.services.gophish.client import GophishService
from app.services.load_balancer import LoadBalancerService
from app.models.instance import Instance
from app.models.tenant import Tenant
from app.repository.user_repository import UserRepository

logger = logging.getLogger(__name__)


class GroupsService:
    def __init__(self, gophish_service: Optional[GophishService] = None):
        self.gophish_service = gophish_service or GophishService()
        self.load_balancer = LoadBalancerService()

    def create_group(
        self, 
        tenant: Tenant, 
        instance: Optional[Instance] = None,
        active_users_only: bool = True
    ) -> Group:
        """Create a Gophish group"""
        if not instance:
            instance = self.load_balancer.select_instance_for_load_balancing()
        
        if not instance:
            raise ValueError("No active Gophish instance found")
        
        user_repo = UserRepository()
        users = user_repo.get_all_by_tenant_id(tenant.id, active_only=active_users_only)
        
        targets = [
            GophishUser(
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                position=""
            )
            for user in users
        ]
        
        client = self.gophish_service.get_client_for_instance(instance)
        group = Group(name=tenant.name, targets=targets)
        
        try:
            created_group = client.groups.post(group)
            if targets:
                logger.info(f"Created Gophish group '{tenant.name}' with ID {created_group.id} and {len(targets)} users in instance {instance.name}")
            else:
                logger.warning(f"Created Gophish group '{tenant.name}' with ID {created_group.id} but no users in instance {instance.name}")
            return created_group
        except Exception as e:
            logger.error(f"Failed to create Gophish group '{tenant.name}' in instance {instance.name}: {e}")
            raise ValueError(f"Failed to create Gophish group: {str(e)}")

    def add_user_to_group(
        self, 
        group_id: int, 
        first_name: str, 
        last_name: str, 
        email: str,
        position: Optional[str] = None,
        instance: Optional[Instance] = None
    ) -> Group:
        if not instance:
            instance = self.load_balancer.select_instance_for_load_balancing()
        
        if not instance:
            raise ValueError("No active Gophish instance found")
        
        client = self.gophish_service.get_client_for_instance(instance)
        
        try:
            group = client.groups.get(group_id=group_id)
            if not group:
                raise ValueError(f"Group with ID {group_id} not found")
            
            new_user = GophishUser(
                first_name=first_name,
                last_name=last_name,
                email=email,
                position=position or ""
            )
            
            existing_emails = {user.email for user in group.targets if hasattr(user, 'email')}
            if email not in existing_emails:
                group.targets.append(new_user)
                updated_group = client.groups.put(group)
                logger.info(f"Added user {email} to group {group_id} in instance {instance.name}")
                return updated_group
            else:
                logger.info(f"User {email} already exists in group {group_id}")
                return group
                
        except Exception as e:
            logger.error(f"Failed to add user to group {group_id} in instance {instance.name}: {e}")
            raise ValueError(f"Failed to add user to group: {str(e)}")

    def get_group(self, group_id: int, instance: Optional[Instance] = None) -> Optional[Group]:
        if not instance:
            instance = self.load_balancer.select_instance_for_load_balancing()
        
        if not instance:
            logger.warning("No active Gophish instance found")
            return None
        
        try:
            client = self.gophish_service.get_client_for_instance(instance)
            return client.groups.get(group_id=group_id)
        except Exception as e:
            logger.error(f"Failed to get group {group_id} from instance {instance.name}: {e}")
            return None
