#!/usr/bin/env python3
"""
Script to set the first created user as admin.

This script finds the user with the earliest created_at timestamp
and sets their is_admin flag to True.

Usage:
    python set_first_user_admin.py
"""

import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import asc
from app import create_app
from app.repository.user_repository import UserRepository


def get_first_user():
    """Get the first user created (by created_at timestamp)."""
    repo = UserRepository()
    first_user = repo.session.query(repo.model).order_by(asc(repo.model.created_at)).first()
    return first_user


def set_user_as_admin(user_id: int):
    """Set a user as admin by their ID."""
    repo = UserRepository()
    try:
        updated_user = repo.update_by_id(user_id, is_admin=True)
        return updated_user
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return None


def main():
    """Main function to set first user as admin."""
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        # Get the first user created
        first_user = get_first_user()
        
        if not first_user:
            print("Error: No users found in the database.", file=sys.stderr)
            sys.exit(1)
        
        # Check if user is already admin
        if first_user.is_admin:
            print(f"User ID {first_user.id} ({first_user.email}) is already an admin.")
            print(f"  Name: {first_user.first_name} {first_user.last_name}")
            print(f"  Created At: {first_user.created_at}")
            return
        
        # Set user as admin
        try:
            updated_user = set_user_as_admin(first_user.id)
            
            if updated_user:
                print("\n" + "=" * 60)
                print("Successfully Set First User as Admin!")
                print("=" * 60)
                print(f"User ID: {updated_user.id}")
                print(f"Email: {updated_user.email}")
                print(f"Name: {updated_user.first_name} {updated_user.last_name}")
                print(f"Tenant ID: {updated_user.tenant_id}")
                print(f"Created At: {updated_user.created_at}")
                print(f"Admin Status: {updated_user.is_admin}")
                print("=" * 60)
            else:
                print("Error: Failed to update user.", file=sys.stderr)
                sys.exit(1)
                
        except Exception as e:
            print(f"Error setting user as admin: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    main()
