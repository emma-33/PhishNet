import logging
from typing import Optional
from gophish.models import Group, User as GophishUser
from app.services.gophish.client import GophishService
from app.services.load_balancer import LoadBalancerService
from app.models.instance import Instance
from app.models.tenant import Tenant
from app.repository.target_repository import TargetRepository

logger = logging.getLogger(__name__)


class GroupsService:
    def __init__(self, gophish_service: Optional[GophishService] = None):
        self.gophish_service = gophish_service or GophishService()
        self.load_balancer = LoadBalancerService()

    def create_group(
        self,
        tenant: Tenant,
        instance: Optional[Instance] = None
    ) -> Group:
        """Create a Gophish group"""
        if not instance:
            instance = self.load_balancer.select_instance_for_load_balancing()

        if not instance:
            raise ValueError("No active Gophish instance found")

        target_repo = TargetRepository()
        targets_db = target_repo.get_all_by_tenant_id(tenant.id)

        gophish_targets = [
            GophishUser(
                first_name=t.first_name,
                last_name=t.last_name,
                email=t.email,
                position=t.position or ""
            )
            for t in targets_db
        ]

        client = self.gophish_service.get_client_for_instance(instance)
        group = Group(name=tenant.name, targets=gophish_targets)

        try:
            created_group = client.groups.post(group)
            if gophish_targets:
                logger.info(f"Created Gophish group '{tenant.name}' with ID {created_group.id} and {len(gophish_targets)} targets in instance {instance.name}")
            else:
                logger.warning(f"Created Gophish group '{tenant.name}' with ID {created_group.id} but no targets in instance {instance.name}")
            return created_group
        except Exception as e:
            logger.error(f"Failed to create Gophish group '{tenant.name}' in instance {instance.name}: {e}")
            raise ValueError(f"Failed to create Gophish group: {str(e)}")

    def add_target_to_group(
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

            new_target = GophishUser(
                first_name=first_name,
                last_name=last_name,
                email=email,
                position=position or ""
            )

            existing_emails = {user.email for user in group.targets if hasattr(user, 'email')}
            if email not in existing_emails:
                group.targets.append(new_target)
                updated_group = client.groups.put(group)
                logger.info(f"Added target {email} to group {group_id} in instance {instance.name}")
                return updated_group
            else:
                logger.info(f"Target {email} already exists in group {group_id}")
                return group

        except Exception as e:
            logger.error(f"Failed to add target to group {group_id} in instance {instance.name}: {e}")
            raise ValueError(f"Failed to add target to group: {str(e)}")

    def remove_target_from_group(
        self,
        group_id: int,
        email: str,
        instance: Optional[Instance] = None
    ) -> Group:
        """Remove a target from a Gophish group by email."""
        if not instance:
            instance = self.load_balancer.select_instance_for_load_balancing()

        if not instance:
            raise ValueError("No active Gophish instance found")

        client = self.gophish_service.get_client_for_instance(instance)

        try:
            group = client.groups.get(group_id=group_id)
            if not group:
                raise ValueError(f"Group with ID {group_id} not found")

            # Filter out the target with the given email
            new_targets = [t for t in group.targets if hasattr(t, 'email') and t.email != email]

            if len(new_targets) < len(group.targets):
                group.targets = new_targets
                updated_group = client.groups.put(group)
                logger.info(f"Removed target {email} from group {group_id} in instance {instance.name}")
                return updated_group
            else:
                logger.info(f"Target {email} not found in group {group_id}")
                return group

        except Exception as e:
            logger.error(f"Failed to remove target from group {group_id} in instance {instance.name}: {e}")
            raise ValueError(f"Failed to remove target from group: {str(e)}")

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
