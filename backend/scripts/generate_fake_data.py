import argparse
import random
import sys
import os
from faker import Faker
from datetime import datetime, timedelta

# Add the parent directory to sys.path to allow imports from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.tenant import Tenant
from app.models.user import User
from app.models.target import Target
from app.models.template import Template
from app.models.campaign import Campaign, CampaignStatus
from app.models.campaign_stats import CampaignStats
from app.models.campaign_result import CampaignResult
from app.models.audit_log import AuditLog

fake = Faker()

def generate_data(tenant_id, user_id, num_targets, num_campaigns):
    app = create_app()
    with app.app_context():
        # 1. Validate tenant and user
        tenant = db.session.get(Tenant, tenant_id)
        if not tenant:
            print(f"Error: Tenant with ID {tenant_id} not found.")
            return

        user = db.session.get(User, user_id)
        if not user:
            print(f"Error: User with ID {user_id} not found.")
            return

        if user.tenant_id != tenant_id:
            print(f"Error: User {user_id} does not belong to tenant {tenant_id}.")
            return

        # 2. Fetch existing templates for the tenant's instance
        if not tenant.instance_id:
            print(f"Error: Tenant {tenant_id} does not have an instance assigned.")
            return

        templates = db.session.query(Template).filter(
            Template.gophish_instance_id == tenant.instance_id
        ).all()

        if not templates:
            print(f"Error: No templates found for instance {tenant.instance_id}. Please create at least one template first.")
            return

        print(f"Starting generation for Tenant: {tenant.name} (ID: {tenant_id})")

        # 3. Generate fake targets
        print(f"Generating {num_targets} fake targets...")
        new_targets = []
        for _ in range(num_targets):
            target = Target(
                email=fake.unique.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                position=fake.job(),
                tenant_id=tenant_id
            )
            new_targets.append(target)
            db.session.add(target)

        db.session.flush() # Get IDs

        # Add audit log for target generation (matching CREATE_TARGET pattern)
        for target in new_targets:
            target_log = AuditLog(
                user_id=user_id,
                tenant_id=tenant_id,
                action="CREATE_TARGET",
                resource_type="Target",
                resource_id=str(target.id),
                details={
                    "email": target.email,
                    "first_name": target.first_name,
                    "last_name": target.last_name,
                    "note": "Generated via fake data script"
                },
                ip_address="127.0.0.1"
            )
            db.session.add(target_log)

        # 4. Generate fake campaigns
        print(f"Generating {num_campaigns} fake campaigns...")
        for i in range(num_campaigns):
            template = random.choice(templates)

            # Use random status
            status = random.choice([CampaignStatus.RUNNING, CampaignStatus.STOPPED, CampaignStatus.ARCHIVED])

            # Generate a "gophish" ID that doesn't exist (fake)
            fake_gophish_id = random.randint(10000, 99999)

            launched_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))
            stopped_at = launched_at + timedelta(days=7) if status != CampaignStatus.RUNNING else None

            campaign = Campaign(
                name=f"Fake Campaign {fake.word().capitalize()} {i+1}",
                gophish_instance_id=tenant.instance_id,
                gophish_campaign_id=fake_gophish_id,
                tenant_id=tenant_id,
                created_by_user_id=user_id,
                template_id=template.id,
                status=status,
                launched_at=launched_at,
                stopped_at=stopped_at
            )
            db.session.add(campaign)
            db.session.flush()

            # 5. Generate random statistics with realistic percentages (25-75% for each step)
            sent = num_targets

            # Opened: 25-75% of sent
            opened = random.randint(max(1, int(sent * 0.25)), max(1, int(sent * 0.75)))

            # Clicked: 25-75% of opened
            clicked = random.randint(max(1, int(opened * 0.25)), max(1, int(opened * 0.75)))

            # Submitted: 25-75% of clicked
            submitted = random.randint(max(0, int(clicked * 0.25)), max(1, int(clicked * 0.75)))

            # Reported: 0-10% of sent
            reported = random.randint(0, max(1, int(sent * 0.10)))

            stats = CampaignStats(
                campaign_id=campaign.id,
                total_targets=num_targets,
                sent_count=sent,
                opened_count=opened,
                clicked_count=clicked,
                submitted_count=submitted,
                reported_count=reported
            )
            db.session.add(stats)

            # 6. Generate individual results to populate the table
            print(f"  Populating results for campaign {campaign.id}...")

            # We shuffle the targets to assign statuses randomly
            random.shuffle(new_targets)

            for idx, target in enumerate(new_targets):
                # Determine status based on the counts generated above
                if idx < submitted:
                    status = "Submitted Data"
                elif idx < clicked:
                    status = "Clicked Link"
                elif idx < opened:
                    status = "Email Opened"
                else:
                    status = "Sent"

                # Overwrite some with "Email Reported" if needed (separate funnel)
                if status == "Sent" and idx < (sent - opened) and idx < reported:
                    status = "Email Reported"

                result = CampaignResult(
                    campaign_id=campaign.id,
                    email=target.email,
                    first_name=target.first_name,
                    last_name=target.last_name,
                    position=target.position,
                    status=status,
                    modified_date=launched_at + timedelta(hours=random.randint(1, 48))
                )
                db.session.add(result)

            # Add audit log for campaign generation (matching CREATE_CAMPAIGN pattern)
            campaign_log = AuditLog(
                user_id=user_id,
                tenant_id=tenant_id,
                action="CREATE_CAMPAIGN",
                resource_type="Campaign",
                resource_id=str(campaign.id),
                details={
                    "name": campaign.name,
                    "template_id": template.id,
                    "note": "Generated via fake data script"
                },
                ip_address="127.0.0.1"
            )
            db.session.add(campaign_log)

        db.session.commit()
        print(f"Successfully generated data for tenant {tenant_id}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate fake target and campaign data.")
    parser.add_argument("--tenant-id", type=int, required=True, help="ID of the tenant")
    parser.add_argument("--user-id", type=int, required=True, help="ID of the user creating the data")
    parser.add_argument("--targets", type=int, default=10, help="Number of targets to generate")
    parser.add_argument("--campaigns", type=int, default=2, help="Number of campaigns to generate")

    args = parser.parse_args()
    generate_data(args.tenant_id, args.user_id, args.targets, args.campaigns)
