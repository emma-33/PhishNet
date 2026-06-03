"""Tenant-related helper functions"""
from app.repository.tenant_repository import TenantRepository


def verify_tenant_ownership(resource_tenant_id: int, user_tenant_id: int):
    """Verify tenant ownership"""
    return resource_tenant_id == user_tenant_id


def is_tenant_operator(user_id, tenant_id):
    """Check if user is the operator (owner) of the tenant."""
    tenant_repo = TenantRepository()
    tenant = tenant_repo.get_by_id(tenant_id)
    # Ensure ID comparison handles string identities from JWT
    return tenant and str(tenant.operator_id) == str(user_id)
