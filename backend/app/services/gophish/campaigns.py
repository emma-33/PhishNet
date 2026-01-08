import logging
from gophish.models import Campaign as GophishCampaign, Template as GophishTemplate, Page, Group, SMTP
from app.models.campaign import CampaignStatus, Campaign
from app.api.helpers import format_date
from .client import GophishService
from app.repository.campaign_repository import CampaignRepository
from app.repository.instance_repository import InstanceRepository
from app.repository.template_repository import TemplateMapRepository
from app.repository.tenant_repository import TenantRepository

logger = logging.getLogger(__name__)


class CampaignService:
    """Campaign service for managing Gophish campaigns."""

    def __init__(self):
        self._gophish_service = None
        self._repository = None
        self._instance_repository = None

    @property
    def gophish_service(self):
        """Get or create GophishService instance."""
        if self._gophish_service is None:
            self._gophish_service = GophishService()
        return self._gophish_service
    
    @property
    def instance_repository(self):
        """Get or create InstanceRepository instance."""
        if self._instance_repository is None:
            self._instance_repository = InstanceRepository()
        return self._instance_repository

    @property
    def repository(self):
        """Get or create CampaignRepository instance."""
        if self._repository is None:
            self._repository = CampaignRepository()
        return self._repository
    
    @property
    def template_repository(self):
        """Get or create TemplateMapRepository instance."""
        if not hasattr(self, '_template_repository') or self._template_repository is None:
            self._template_repository = TemplateMapRepository()
        return self._template_repository
    
    @property
    def tenant_repository(self):
        """Get or create TenantRepository instance."""
        if not hasattr(self, '_tenant_repository') or self._tenant_repository is None:
            self._tenant_repository = TenantRepository()
        return self._tenant_repository

    def get_all_campaigns(self, tenant_id=None):
        """Return all campaigns, optionally filtered by tenant_id."""
        if tenant_id is not None:
            return self.repository.get_all(tenant_id=tenant_id)
        return self.repository.get_all()

    def get_campaign_by_id(self, campaign_id, tenant_id=None):
        """Return a specific campaign by ID, optionally filtered by tenant_id."""
        if tenant_id is not None:
            campaign = self.repository.get_by_id(campaign_id, tenant_id=tenant_id)
        else:
            campaign = self.repository.get_by_id(campaign_id)
        return campaign

    def create_campaign(self, campaign):
        """Create a new campaign"""

        # Get instance for this campaign
        instance = self.instance_repository.get_by_id(campaign.gophish_instance_id)
        if not instance:
            raise ValueError(f"Instance {campaign.gophish_instance_id} not found")
        
        # Get template by ID to get its name (templates are replicated across instances)
        template_reference = self.template_repository.get_by_id(campaign.template_id)
        if not template_reference:
            raise ValueError(f"Template {campaign.template_id} not found")
        
        # Find the template on the campaign's instance
        template_map = self.template_repository.get_by_name_and_instance(
            template_reference.name, 
            campaign.gophish_instance_id
        )
        if not template_map:
            raise ValueError(
                f"Template '{template_reference.name}' not found on instance {campaign.gophish_instance_id}"
            )
        
        # Get tenant to get gophish_group_id
        tenant = self.tenant_repository.get_by_id(campaign.tenant_id)
        if not tenant:
            raise ValueError(f"Tenant {campaign.tenant_id} not found")
        
        if not tenant.gophish_group_id:
            raise ValueError(f"Tenant {campaign.tenant_id} does not have a Gophish group assigned")
        
        # Create gophish Campaign object
        client = self.gophish_service.get_client_for_instance(instance)
        
        # Fetch full template and page objects from gophish
        try:
            gophish_template = client.templates.get(template_id=template_map.gophish_email_template_id)
            if not gophish_template:
                raise ValueError(f"Gophish template {template_map.gophish_email_template_id} not found")
        except Exception as e:
            logger.error(f"Failed to fetch template {template_map.gophish_email_template_id}: {e}")
            raise ValueError(f"Failed to fetch template: {str(e)}")
        
        try:
            gophish_page = client.pages.get(template_map.gophish_landing_page_id)
            if not gophish_page:
                raise ValueError(f"Gophish page {template_map.gophish_landing_page_id} not found")
        except Exception as e:
            logger.error(f"Failed to fetch page {template_map.gophish_landing_page_id}: {e}")
            raise ValueError(f"Failed to fetch page: {str(e)}")
        
        # Fetch group from gophish (tenant's group)
        try:
            gophish_group = client.groups.get(group_id=tenant.gophish_group_id)
            if not gophish_group:
                raise ValueError(f"Gophish group {tenant.gophish_group_id} not found")
        except Exception as e:
            logger.error(f"Failed to fetch group {tenant.gophish_group_id}: {e}")
            raise ValueError(f"Failed to fetch group: {str(e)}")
        
        smtp_profile_id = 1
        
        # Fetch SMTP profile from gophish
        try:
            gophish_smtp = client.smtp.get(smtp_id=smtp_profile_id)
            if not gophish_smtp:
                raise ValueError(f"Gophish SMTP profile {smtp_profile_id} not found")
        except Exception as e:
            logger.error(f"Failed to fetch SMTP profile {smtp_profile_id}: {e}")
            raise ValueError(f"Failed to fetch SMTP profile: {str(e)}")
        
        gophish_campaign = GophishCampaign(
            name=campaign.name,
            template=gophish_template,
            page=gophish_page,
            groups=[gophish_group],
            smtp=gophish_smtp
        )
        
        # Add optional fields from meta if present
        if hasattr(campaign, 'meta') and campaign.meta:
            if 'url' in campaign.meta:
                gophish_campaign.url = campaign.meta['url']
        
        try:
            result = client.campaigns.post(gophish_campaign)
            
            if result:
                # Create platform campaign record
                platform_campaign = Campaign(
                    gophish_instance_id=campaign.gophish_instance_id,
                    gophish_campaign_id=result.id,
                    tenant_id=campaign.tenant_id,
                    name=campaign.name,
                    created_by_user_id=campaign.created_by_user_id,
                    template_id=campaign.template_id,
                    status=CampaignStatus.DRAFT,
                    meta=getattr(campaign, 'meta', {})
                )
                platform_campaign = self.repository.create(platform_campaign)
                logger.info(f"Created campaign '{campaign.name}' (ID: {result.id}) for tenant {campaign.tenant_id}")
                
                # Convert gophish campaign to dict for JSON serialization
                gophish_campaign_dict = {
                    'id': result.id,
                    'name': result.name,
                    'status': getattr(result, 'status', 'Draft'),
                    'created_date': format_date(getattr(result, 'created_date', None)),
                    'launch_date': format_date(getattr(result, 'launch_date', None)),
                    'completed_date': format_date(getattr(result, 'completed_date', None)),
                }
                
                return {
                    "status": "success",
                    "message": "Campaign created successfully",
                    "campaign": {
                        'id': platform_campaign.id,
                        'name': platform_campaign.name,
                        'status': platform_campaign.status.value,
                        'tenant_id': platform_campaign.tenant_id,
                        'gophish_campaign_id': platform_campaign.gophish_campaign_id,
                        'template_id': platform_campaign.template_id,
                        'created_at': platform_campaign.created_at.isoformat() if platform_campaign.created_at else None,
                    },
                    "gophish_campaign": gophish_campaign_dict
                }
            
            return {"status": "error", "message": "Failed to create campaign"}
        except Exception as e:
            logger.error(f"Failed to create campaign '{campaign.name}': {e}", exc_info=True)
            raise ValueError(f"Failed to create campaign: {str(e)}")

    def delete_campaign(self, campaign_id, tenant_id=None):
        """Delete the campaign"""
        if campaign_id is None:
            raise ValueError("campaign_id is required and cannot be None")
        if not isinstance(campaign_id, (int, str)):
            raise TypeError(f"campaign_id must be an int or str, got {type(campaign_id).__name__}")
        if isinstance(campaign_id, str) and not campaign_id.strip():
            raise ValueError("campaign_id cannot be an empty string")
        
        if tenant_id is not None:
            campaign = self.repository.get_by_id(campaign_id, tenant_id=tenant_id)
        else:
            campaign = self.repository.get_by_id(campaign_id)
        
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        if tenant_id is not None and campaign.tenant_id != tenant_id:
            raise PermissionError(f"Campaign {campaign_id} does not belong to tenant {tenant_id}")
        
        instance = self.instance_repository.get_by_id(campaign.gophish_instance_id)
        if not instance:
            raise ValueError(f"Instance {campaign.gophish_instance_id} not found")
        
        client = self.gophish_service.get_client_for_instance(instance)
        result = client.campaigns.delete(campaign.gophish_campaign_id)
        if result:
            self.repository.delete(campaign_id)
            return {"status": "success", "message": "Campaign deleted successfully"}
            
        return {"status": "error", "message": "Failed to delete campaign"}

    def complete_campaign(self, campaign_id, tenant_id=None):
        """Complete the campaign"""
        if campaign_id is None:
            raise ValueError("campaign_id is required and cannot be None")
        if not isinstance(campaign_id, (int, str)):
            raise TypeError(f"campaign_id must be an int or str, got {type(campaign_id).__name__}")
        if isinstance(campaign_id, str) and not campaign_id.strip():
            raise ValueError("campaign_id cannot be an empty string")
        
        # Get campaign to find its instance and verify tenant ownership
        if tenant_id is not None:
            campaign = self.repository.get_by_id(campaign_id, tenant_id=tenant_id)
        else:
            campaign = self.repository.get_by_id(campaign_id)
        
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        # Verify tenant ownership if tenant_id was provided
        if tenant_id is not None and campaign.tenant_id != tenant_id:
            raise PermissionError(f"Campaign {campaign_id} does not belong to tenant {tenant_id}")
        
        # Get instance for this campaign
        instance = self.instance_repository.get_by_id(campaign.gophish_instance_id)
        if not instance:
            raise ValueError(f"Instance {campaign.gophish_instance_id} not found")
        
        client = self.gophish_service.get_client_for_instance(instance)
        result = client.campaigns.complete(campaign.gophish_campaign_id)
        if result:
            self.repository.update_status_by_id(campaign_id, CampaignStatus.STOPPED)
            return {"status": "success", "message": "Campaign completed successfully"}

        return {"status": "error", "message": "Failed to complete campaign"}
