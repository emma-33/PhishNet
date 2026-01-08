#!/usr/bin/env python3
"""
Script to assign tenants to available Gophish instances.

This script finds all tenants without an assigned instance and distributes them
across available active instances using a load-balancing algorithm.

Usage:
    python assign_instances_to_tenants.py [--dry-run] [--force]

Options:
    --dry-run    Show what would be assigned without making changes
    --force      Force reassignment of all tenants (including those already assigned)
"""

import argparse
import sys
import logging
from collections import defaultdict
from app import create_app
from app.repository.tenant_repository import TenantRepository
from app.repository.instance_repository import InstanceRepository

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_unassigned_tenants(tenant_repo: TenantRepository, force: bool = False):
    """Get tenants that don't have an instance assigned."""
    if force:
        # Get all tenants if force is enabled
        return tenant_repo.get_all()
    else:
        # Get only tenants without instance_id
        return tenant_repo.session.query(tenant_repo.model).filter(
            tenant_repo.model.instance_id.is_(None)
        ).all()


def get_tenant_counts_by_instance(tenant_repo: TenantRepository):
    """Get count of tenants per instance."""
    tenants = tenant_repo.get_all()
    counts = defaultdict(int)
    for tenant in tenants:
        if tenant.instance_id:
            counts[tenant.instance_id] += 1
    return counts


def assign_instances_to_tenants(dry_run: bool = False, force: bool = False):
    """Assign tenants to available instances using load balancing."""
    tenant_repo = TenantRepository()
    instance_repo = InstanceRepository()
    
    # Get active instances
    active_instances = instance_repo.get_active()
    
    if not active_instances:
        logger.error("No active instances found. Cannot assign tenants.")
        return False
    
    logger.info(f"Found {len(active_instances)} active instance(s)")
    for instance in active_instances:
        logger.info(f"  - {instance.name} (ID: {instance.id})")
    
    # Get tenants to assign
    tenants_to_assign = get_unassigned_tenants(tenant_repo, force)
    
    if not tenants_to_assign:
        logger.info("No tenants need assignment.")
        return True
    
    logger.info(f"\nFound {len(tenants_to_assign)} tenant(s) to assign:")
    for tenant in tenants_to_assign:
        current_instance = f" (currently: instance {tenant.instance_id})" if tenant.instance_id else ""
        logger.info(f"  - {tenant.name} (ID: {tenant.id}){current_instance}")
    
    # Get current tenant counts per instance for load balancing
    initial_tenant_counts = get_tenant_counts_by_instance(tenant_repo)
    tenant_counts = initial_tenant_counts.copy()
    
    # If forcing reassignment, remove tenants being reassigned from their current instance counts
    # This ensures load balancing considers the reassignment
    if force:
        for tenant in tenants_to_assign:
            if tenant.instance_id and tenant.instance_id in tenant_counts:
                tenant_counts[tenant.instance_id] = max(0, tenant_counts[tenant.instance_id] - 1)
    
    # Assign tenants using round-robin with load balancing
    assignments = []
    instance_index = 0
    
    for tenant in tenants_to_assign:
        # Find instance with least tenants
        selected_instance = None
        min_tenant_count = float('inf')
        
        for instance in active_instances:
            count = tenant_counts.get(instance.id, 0)
            if count < min_tenant_count:
                min_tenant_count = count
                selected_instance = instance
        
        if not selected_instance:
            selected_instance = active_instances[0]
        
        assignments.append({
            'tenant': tenant,
            'instance': selected_instance,
            'current_instance_id': tenant.instance_id
        })
        
        # Update count for next iteration
        tenant_counts[selected_instance.id] = tenant_counts.get(selected_instance.id, 0) + 1
    
    # Display assignments
    logger.info("\n" + "=" * 70)
    logger.info("ASSIGNMENT PLAN")
    logger.info("=" * 70)
    
    for assignment in assignments:
        tenant = assignment['tenant']
        instance = assignment['instance']
        current = assignment['current_instance_id']
        
        if current:
            logger.info(
                f"Tenant '{tenant.name}' (ID: {tenant.id}) -> "
                f"Instance '{instance.name}' (ID: {instance.id}) "
                f"[REASSIGN from instance {current}]"
            )
        else:
            logger.info(
                f"Tenant '{tenant.name}' (ID: {tenant.id}) -> "
                f"Instance '{instance.name}' (ID: {instance.id})"
            )
    
    logger.info("=" * 70)
    
    # Show final distribution
    logger.info("\nFinal tenant distribution:")
    for instance in active_instances:
        initial_count = initial_tenant_counts.get(instance.id, 0)
        final_count = tenant_counts.get(instance.id, 0)
        logger.info(
            f"  {instance.name} (ID: {instance.id}): "
            f"{initial_count} -> {final_count} tenants"
        )
    
    if dry_run:
        logger.info("\n[DRY RUN] No changes were made. Use without --dry-run to apply changes.")
        return True
    
    # Apply assignments
    logger.info("\nApplying assignments...")
    success_count = 0
    error_count = 0
    
    for assignment in assignments:
        tenant = assignment['tenant']
        instance = assignment['instance']
        
        try:
            tenant_repo.update_by_id(tenant.id, instance_id=instance.id)
            logger.info(
                f"✓ Assigned tenant '{tenant.name}' (ID: {tenant.id}) "
                f"to instance '{instance.name}' (ID: {instance.id})"
            )
            success_count += 1
        except Exception as e:
            logger.error(
                f"✗ Failed to assign tenant '{tenant.name}' (ID: {tenant.id}): {e}"
            )
            error_count += 1
    
    logger.info("\n" + "=" * 70)
    logger.info(f"Assignment complete: {success_count} successful, {error_count} failed")
    logger.info("=" * 70)
    
    return error_count == 0


def main():
    parser = argparse.ArgumentParser(
        description='Assign tenants to available Gophish instances',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be assigned without making changes'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force reassignment of all tenants (including those already assigned)'
    )
    
    args = parser.parse_args()
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        try:
            success = assign_instances_to_tenants(
                dry_run=args.dry_run,
                force=args.force
            )
            sys.exit(0 if success else 1)
        except Exception as e:
            logger.exception("Error assigning instances to tenants")
            sys.exit(1)


if __name__ == '__main__':
    main()
