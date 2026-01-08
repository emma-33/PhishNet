#!/usr/bin/env python3
"""
Script to generate invitation codes for user registration.

Usage:
    python generate_invitation.py [--tenant-id TENANT_ID] [--tenant-name TENANT_NAME] [--expires-days DAYS]

Examples:
    python generate_invitation.py --tenant-id 1
    python generate_invitation.py --tenant-name "My Company"
    python generate_invitation.py --tenant-id 1 --expires-days 30
    
Note: When using --tenant-name, the tenant will be created automatically if it doesn't exist.
"""

import argparse
import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.services.tenant_invitation_service import create_invitation
from app.repository.tenant_repository import TenantRepository


def list_tenants():
    """List all available tenants."""
    repo = TenantRepository()
    tenants = repo.get_all()
    
    if not tenants:
        print("No tenants found in the database.")
        return []
    
    print("\nAvailable tenants:")
    print("-" * 50)
    for tenant in tenants:
        print(f"  ID: {tenant.id:3d} | Name: {tenant.name}")
    print("-" * 50)
    
    return tenants


def get_tenant_by_id(tenant_id: int):
    """Get a tenant by ID."""
    repo = TenantRepository()
    tenant = repo.get_by_id(tenant_id)
    return tenant


def get_or_create_tenant_by_name(tenant_name: str):
    """Get a tenant by name, or create it if it doesn't exist."""
    repo = TenantRepository()
    tenant = repo.get_or_create_by_name(tenant_name)
    return tenant


def main():
    parser = argparse.ArgumentParser(
        description='Generate an invitation code for user registration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--tenant-id',
        type=int,
        help='Tenant ID to generate invitation for'
    )
    
    parser.add_argument(
        '--tenant-name',
        type=str,
        help='Tenant name to generate invitation for (will create tenant if it doesn\'t exist)'
    )
    
    parser.add_argument(
        '--expires-days',
        type=int,
        default=None,
        help='Number of days until invitation expires (default: never expires)'
    )
    
    parser.add_argument(
        '--list-tenants',
        action='store_true',
        help='List all available tenants and exit'
    )
    
    args = parser.parse_args()
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        # List tenants if requested
        if args.list_tenants:
            list_tenants()
            return
        
        # Determine tenant
        tenant = None
        
        if args.tenant_id:
            tenant = get_tenant_by_id(args.tenant_id)
            if not tenant:
                print(f"Error: Tenant with ID {args.tenant_id} not found.", file=sys.stderr)
                sys.exit(1)
        elif args.tenant_name:
            # Get or create tenant by name
            repo = TenantRepository()
            existing_tenant = repo.get_by_name(args.tenant_name)
            tenant = get_or_create_tenant_by_name(args.tenant_name)
            if not existing_tenant:
                print(f"Created new tenant: '{args.tenant_name}' (ID: {tenant.id})")
        else:
            # Interactive mode: list tenants and prompt for selection
            tenants = list_tenants()
            if not tenants:
                print("Error: No tenants available. Please create a tenant first.", file=sys.stderr)
                sys.exit(1)
            
            try:
                tenant_id_input = input("\nEnter tenant ID: ").strip()
                tenant_id = int(tenant_id_input)
                tenant = get_tenant_by_id(tenant_id)
                if not tenant:
                    print(f"Error: Tenant with ID {tenant_id} not found.", file=sys.stderr)
                    sys.exit(1)
            except ValueError:
                print("Error: Invalid tenant ID. Must be a number.", file=sys.stderr)
                sys.exit(1)
            except KeyboardInterrupt:
                print("\nCancelled by user.")
                sys.exit(0)
        
        # Generate invitation
        try:
            result = create_invitation(tenant.id, args.expires_days)
            
            if result['status'] == 'success':
                invitation = result['invitation']
                print("\n" + "=" * 60)
                print("Invitation Code Generated Successfully!")
                print("=" * 60)
                print(f"Invitation Code: {invitation.invitation_code}")
                print(f"Tenant: {tenant.name} (ID: {tenant.id})")
                print(f"Created At: {invitation.created_at}")
                if invitation.expires_at:
                    print(f"Expires At: {invitation.expires_at}")
                else:
                    print("Expires At: Never")
                print(f"Status: {'Used' if invitation.is_used else 'Available'}")
                print("=" * 60)
                print("\nShare this invitation code with the user for registration.")
            else:
                print(f"Error: {result['message']}", file=sys.stderr)
                sys.exit(1)
                
        except Exception as e:
            print(f"Error generating invitation: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    main()
