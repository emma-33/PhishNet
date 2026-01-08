import secrets
import logging
from datetime import datetime, timedelta
from app.repository.tenant_repository import TenantRepository
from app.repository.tenant_invitation_repository import TenantInvitationRepository
from app.models.tenant import Tenant
from app.models.tenant_invitation import TenantInvitation
from app.services.gophish.groups import GroupsService

logger = logging.getLogger(__name__)


def create_tenant(name: str, invitation_expires_days: int = None):
    tenant_repo = TenantRepository()
    invitation_repo = TenantInvitationRepository()
    
    existing_tenant = tenant_repo.get_by_name(name)
    if existing_tenant:
        return {
            'status': 'error',
            'message': f'Tenant with name "{name}" already exists',
            'tenant': None,
            'invitation': None
        }
    
    tenant = Tenant(name=name)
    tenant = tenant_repo.create(tenant)
    
    try:
        groups_service = GroupsService()
        gophish_group = groups_service.create_group(tenant)
        tenant_repo.update_by_id(tenant.id, gophish_group_id=gophish_group.id)
        tenant = tenant_repo.get_by_id(tenant.id)
        logger.info(f"Created Gophish group {gophish_group.id} for tenant {tenant.id}")
    except Exception as e:
        logger.warning(f"Failed to create Gophish group for tenant {tenant.id}: {e}")
    
    invitation_code = secrets.token_urlsafe(32)
    
    expires_at = None
    if invitation_expires_days is not None:
        expires_at = datetime.utcnow() + timedelta(days=invitation_expires_days)
    
    invitation = TenantInvitation(
        invitation_code=invitation_code,
        tenant_id=tenant.id,
        is_used=False,
        expires_at=expires_at
    )
    invitation = invitation_repo.create(invitation)
    
    return {
        'status': 'success',
        'message': 'Tenant created successfully',
        'tenant': tenant,
        'invitation': invitation
    }


def get_tenant_by_id(tenant_id: int):
    tenant_repo = TenantRepository()
    return tenant_repo.get_by_id(tenant_id)


def get_all_tenants():
    tenant_repo = TenantRepository()
    return tenant_repo.get_all()
