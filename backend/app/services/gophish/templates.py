import logging
from typing import Optional, Dict, Any
from gophish.models import Template as GophishTemplate, Page

from .client import GophishService
from app.repository.template_repository import TemplateMapRepository
from app.repository.instance_repository import InstanceRepository
from app.models.template import Template

logger = logging.getLogger(__name__)


class TemplatesService:
    def __init__(self):
        self._gophish_service = None
        self._repository = None
        self._instance_repository = None

    @property
    def gophish_service(self):
        if self._gophish_service is None:
            self._gophish_service = GophishService()
        return self._gophish_service
    
    @property
    def instance_repository(self):
        if self._instance_repository is None:
            self._instance_repository = InstanceRepository()
        return self._instance_repository

    @property
    def repository(self):
        if self._repository is None:
            self._repository = TemplateMapRepository()
        return self._repository

    def get_all_templates(self, instance_id: Optional[int] = None):
        if instance_id:
            return self.repository.get_by_instance_id(instance_id)
        else:
            return self.repository.get_all()

    def get_template_by_id(self, template_id: int):
        return self.repository.get_by_id(template_id)

    def get_template_details(self, template_id: int):
        template_map = self.get_template_by_id(template_id)
        if not template_map:
            return None

        instance = self.instance_repository.get_by_id(template_map.gophish_instance_id)
        if not instance:
            raise ValueError(f"Instance {template_map.gophish_instance_id} not found")
        
        client = self.gophish_service.get_client_for_instance(instance)
        
        try:
            email_template = client.templates.get(template_id=template_map.gophish_email_template_id)
            landing_page = client.pages.get(template_map.gophish_landing_page_id)
            
            return {
                "template_map": template_map,
                "email_template": email_template,
                "landing_page": landing_page
            }
        except Exception as e:
            logger.error(f"Failed to fetch template details: {e}", exc_info=True)
            raise

    def create_template(
        self,
        name: str,
        email_template_data: Dict[str, Any],
        landing_page_data: Dict[str, Any],
        created_by_user_id: int
    ):
        active_instances = self.instance_repository.get_active()
        if not active_instances:
            raise ValueError("No active Gophish instances found")

        created_template_maps = []
        created_resources = []

        try:
            email_template_name = f"{name} Email Template"
            email_template = GophishTemplate(
                name=email_template_name,
                subject=email_template_data.get("subject", ""),
                html=email_template_data.get("html", ""),
            )
            
            if email_template_data.get("attachments"):
                from gophish.models import Attachment
                email_template.attachments = [
                    Attachment(**att) for att in email_template_data["attachments"]
                ]

            landing_page_name = f"{name} Landing Page"
            landing_page = Page(
                name=landing_page_name,
                html=landing_page_data.get("html", ""),
                capture_credentials=landing_page_data.get("capture_credentials", False),
                capture_passwords=landing_page_data.get("capture_passwords", False),
            )
            
            if landing_page_data.get("redirect_url"):
                landing_page.redirect_url = landing_page_data["redirect_url"]

            for instance in active_instances:
                client = self.gophish_service.get_client_for_instance(instance)
                email_template_id = None
                landing_page_id = None
                template_map_id = None

                try:
                    try:
                        created_email_template = client.templates.post(email_template)
                        email_template_id = created_email_template.id
                        logger.info(f"Created email template with ID: {email_template_id} in instance {instance.name}")
                    except Exception as gophish_error:
                        logger.error(f"Gophish API error creating email template in instance {instance.name}: {gophish_error}")
                        raise ValueError(f"Failed to create email template in instance {instance.name}: {str(gophish_error)}")

                    try:
                        created_landing_page = client.pages.post(landing_page)
                        landing_page_id = created_landing_page.id
                        logger.info(f"Created landing page with ID: {landing_page_id} in instance {instance.name}")
                    except Exception as gophish_error:
                        logger.error(f"Gophish API error creating landing page in instance {instance.name}: {gophish_error}")
                        if email_template_id:
                            try:
                                client.templates.delete(email_template_id)
                            except:
                                pass
                        raise ValueError(f"Failed to create landing page in instance {instance.name}: {str(gophish_error)}")

                    template_map = Template(
                        name=name,
                        gophish_instance_id=instance.id,
                        gophish_email_template_id=email_template_id,
                        gophish_landing_page_id=landing_page_id,
                        created_by_user_id=created_by_user_id
                    )

                    created_template_map = self.repository.create(template_map)
                    template_map_id = created_template_map.id
                    created_template_maps.append(created_template_map)
                    created_resources.append((instance.id, email_template_id, landing_page_id, template_map_id))
                    logger.info(f"Created template map with ID: {template_map_id} for instance {instance.name}")

                except Exception as instance_error:
                    logger.error(f"Failed to create template in instance {instance.name}: {instance_error}")
                    raise

            return {
                "status": "success",
                "message": f"Template created successfully in {len(created_template_maps)} instance(s)",
                "templates": [{
                    "id": tm.id,
                    "name": tm.name,
                    "instance_id": tm.gophish_instance_id,
                    "email_template_id": tm.gophish_email_template_id,
                    "landing_page_id": tm.gophish_landing_page_id,
                } for tm in created_template_maps]
            }

        except Exception as e:
            logger.error(f"Failed to create template: {e}", exc_info=True)
            
            for instance_id, email_template_id, landing_page_id, template_map_id in reversed(created_resources):
                try:
                    instance = self.instance_repository.get_by_id(instance_id)
                    if instance:
                        client = self.gophish_service.get_client_for_instance(instance)
                        
                        if template_map_id:
                            try:
                                self.repository.delete(template_map_id)
                                logger.info(f"Cleaned up template map with ID: {template_map_id}")
                            except Exception as cleanup_error:
                                logger.warning(f"Failed to cleanup template map {template_map_id}: {cleanup_error}")
                        
                        if landing_page_id:
                            try:
                                client.pages.delete(landing_page_id)
                                logger.info(f"Cleaned up landing page with ID: {landing_page_id}")
                            except Exception as cleanup_error:
                                logger.warning(f"Failed to cleanup landing page {landing_page_id}: {cleanup_error}")
                        
                        if email_template_id:
                            try:
                                client.templates.delete(email_template_id)
                                logger.info(f"Cleaned up email template with ID: {email_template_id}")
                            except Exception as cleanup_error:
                                logger.warning(f"Failed to cleanup email template {email_template_id}: {cleanup_error}")
                except Exception as cleanup_error:
                    logger.error(f"Error during cleanup for instance {instance_id}: {cleanup_error}", exc_info=True)
            
            raise

    def update_template(
        self,
        template_id: int,
        name: Optional[str] = None,
        email_template_data: Optional[Dict[str, Any]] = None,
        landing_page_data: Optional[Dict[str, Any]] = None
    ):
        template_map = self.get_template_by_id(template_id)
        if not template_map:
            raise ValueError(f"Template with ID {template_id} not found")

        old_template_name = template_map.name
        new_template_name = name if name else old_template_name
        
        all_template_maps = self.repository.get_by_name(old_template_name)
        if not all_template_maps:
            raise ValueError(f"No template maps found with name '{old_template_name}'")

        active_instances = self.instance_repository.get_active()
        existing_maps_by_instance = {tm.gophish_instance_id: tm for tm in all_template_maps}
        updated_count = 0
        created_count = 0
        errors = []

        try:
            for template_map in all_template_maps:
                instance = self.instance_repository.get_by_id(template_map.gophish_instance_id)
                if not instance:
                    logger.warning(f"Instance {template_map.gophish_instance_id} not found for template map {template_map.id}")
                    continue
                
                if not instance.is_active:
                    logger.info(f"Skipping inactive instance {instance.name} for template update")
                    continue

                client = self.gophish_service.get_client_for_instance(instance)

                try:
                    if name or email_template_data:
                        email_template = client.templates.get(template_id=template_map.gophish_email_template_id)
                        
                        if name:
                            email_template.name = f"{new_template_name} Email Template"
                        
                        if email_template_data:
                            if email_template_data.get("subject") is not None:
                                email_template.subject = email_template_data["subject"]
                            if email_template_data.get("html") is not None:
                                email_template.html = email_template_data["html"]
                            if email_template_data.get("attachments") is not None:
                                from gophish.models import Attachment
                                email_template.attachments = [
                                    Attachment(**att) for att in email_template_data["attachments"]
                                ]
                        
                        client.templates.put(email_template)
                        logger.info(f"Updated email template with ID: {email_template.id} in instance {instance.name}")

                    if name or landing_page_data:
                        landing_page = client.pages.get(template_map.gophish_landing_page_id)
                        
                        if name:
                            landing_page.name = f"{new_template_name} Landing Page"
                        
                        if landing_page_data:
                            if landing_page_data.get("html") is not None:
                                landing_page.html = landing_page_data["html"]
                            if landing_page_data.get("capture_credentials") is not None:
                                landing_page.capture_credentials = landing_page_data["capture_credentials"]
                            if landing_page_data.get("capture_passwords") is not None:
                                landing_page.capture_passwords = landing_page_data["capture_passwords"]
                            if landing_page_data.get("redirect_url") is not None:
                                landing_page.redirect_url = landing_page_data["redirect_url"]
                        
                        client.pages.put(landing_page)
                        logger.info(f"Updated landing page with ID: {landing_page.id} in instance {instance.name}")

                    if name and name != old_template_name:
                        self.repository.update_by_id(template_map.id, name=name)

                    updated_count += 1

                except Exception as instance_error:
                    error_msg = f"Failed to update template in instance {instance.name}: {str(instance_error)}"
                    logger.error(error_msg, exc_info=True)
                    errors.append(error_msg)

            if email_template_data and landing_page_data:
                for instance in active_instances:
                    if instance.id not in existing_maps_by_instance:
                        try:
                            email_template_name = f"{new_template_name} Email Template"
                            email_template = GophishTemplate(
                                name=email_template_name,
                                subject=email_template_data.get("subject", ""),
                                html=email_template_data.get("html", ""),
                            )
                            
                            if email_template_data.get("attachments"):
                                from gophish.models import Attachment
                                email_template.attachments = [
                                    Attachment(**att) for att in email_template_data["attachments"]
                                ]

                            landing_page_name = f"{new_template_name} Landing Page"
                            landing_page = Page(
                                name=landing_page_name,
                                html=landing_page_data.get("html", ""),
                                capture_credentials=landing_page_data.get("capture_credentials", False),
                                capture_passwords=landing_page_data.get("capture_passwords", False),
                            )
                            
                            if landing_page_data.get("redirect_url"):
                                landing_page.redirect_url = landing_page_data["redirect_url"]

                            client = self.gophish_service.get_client_for_instance(instance)
                            created_email_template = client.templates.post(email_template)
                            created_landing_page = client.pages.post(landing_page)

                            new_template_map = Template(
                                name=new_template_name,
                                gophish_instance_id=instance.id,
                                gophish_email_template_id=created_email_template.id,
                                gophish_landing_page_id=created_landing_page.id,
                                created_by_user_id=template_map.created_by_user_id
                            )

                            self.repository.create(new_template_map)
                            created_count += 1
                            logger.info(f"Created template in instance {instance.name} during update")

                        except Exception as create_error:
                            error_msg = f"Failed to create template in instance {instance.name}: {str(create_error)}"
                            logger.error(error_msg, exc_info=True)
                            errors.append(error_msg)

            message = f"Template updated successfully in {updated_count} instance(s)"
            if created_count > 0:
                message += f", created in {created_count} new instance(s)"
            if errors:
                message += f", {len(errors)} error(s) occurred"

            return {
                "status": "success" if not errors else "partial",
                "message": message,
                "updated_count": updated_count,
                "created_count": created_count,
                "errors": errors if errors else None
            }

        except Exception as e:
            logger.error(f"Failed to update template: {e}", exc_info=True)
            raise

    def delete_template(self, template_id: int):
        template_map = self.get_template_by_id(template_id)
        if not template_map:
            raise ValueError(f"Template with ID {template_id} not found")

        instance = self.instance_repository.get_by_id(template_map.gophish_instance_id)
        if not instance:
            raise ValueError(f"Instance {template_map.gophish_instance_id} not found")
        
        client = self.gophish_service.get_client_for_instance(instance)

        try:
            client.templates.delete(template_map.gophish_email_template_id)
            logger.info(f"Deleted email template with ID: {template_map.gophish_email_template_id}")

            client.pages.delete(template_map.gophish_landing_page_id)
            logger.info(f"Deleted landing page with ID: {template_map.gophish_landing_page_id}")

            self.repository.delete(template_id)
            logger.info(f"Deleted template map with ID: {template_id}")

            return {
                "status": "success",
                "message": "Template deleted successfully"
            }

        except Exception as e:
            logger.error(f"Failed to delete template: {e}", exc_info=True)
            raise
