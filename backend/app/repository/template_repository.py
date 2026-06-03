from app.models.template import Template
from app.repository.base_repository import BaseRepository


class TemplateMapRepository(BaseRepository[Template]):
    def __init__(self):
        super().__init__(Template)

    def get_by_instance_id(self, instance_id: int):
        return self.session.query(Template).filter(
            Template.gophish_instance_id == instance_id
        ).all()

    def get_by_name(self, name: str):
        return self.session.query(Template).filter(
            Template.name == name
        ).all()

    def get_by_name_and_instance(self, name: str, instance_id: int):
        return self.session.query(Template).filter(
            Template.name == name,
            Template.gophish_instance_id == instance_id
        ).first()

    def get_by_instance_and_template_ids(self, instance_id: int, email_template_id: int, landing_page_id: int):
        return self.session.query(Template).filter(
            Template.gophish_instance_id == instance_id,
            Template.gophish_email_template_id == email_template_id,
            Template.gophish_landing_page_id == landing_page_id
        ).first()
