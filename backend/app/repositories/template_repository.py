from sqlalchemy.orm import Session

from app.models.template import Template, TemplatePlaceholder


class TemplateRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_templates(self):
        return self.db.query(Template).order_by(Template.created_at.desc()).all()

    def get_by_id(self, template_id: int):
        return self.db.query(Template).filter(Template.id == template_id).first()

    def create(self, name: str, title: str | None, content: str):
        template = Template(name=name, title=title, content=content)
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

    def update(self, template: Template, name: str | None, title: str | None, content: str | None):
        if name is not None:
            template.name = name
        if title is not None:
            template.title = title
        if content is not None:
            template.content = content
        template.updated_at = template.updated_at
        self.db.commit()
        self.db.refresh(template)
        return template

    def replace_placeholders(self, template: Template, placeholder_entries):
        self.db.query(TemplatePlaceholder).filter(TemplatePlaceholder.template_id == template.id).delete()
        for entry in placeholder_entries:
            placeholder = TemplatePlaceholder(
                template_id=template.id,
                placeholder_name=entry["placeholder_name"],
                required=entry.get("required", True),
                fallback_value=entry.get("fallback_value"),
            )
            self.db.add(placeholder)
        self.db.commit()
        self.db.refresh(template)
        return template
