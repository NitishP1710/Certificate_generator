import re
from typing import List

from sqlalchemy.orm import Session

from app.models.template import Template, TemplatePlaceholder
from app.repositories.template_repository import TemplateRepository
from app.validators.excel_validator import extract_placeholders


class TemplateService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = TemplateRepository(db)

    def parse_placeholders(self, content: str):
        names = extract_placeholders(content)
        return [{"placeholder_name": name, "required": True, "fallback_value": None} for name in names]

    def validate_template_configuration(self, template: Template):
        if not template.name or not template.content:
            raise ValueError("Template name and content are required")
        placeholders = extract_placeholders(template.content)
        if not placeholders:
            raise ValueError("Template content must include at least one placeholder")
        configured_names = {p.placeholder_name for p in template.placeholders}
        for placeholder_name in placeholders:
            if placeholder_name not in configured_names:
                raise ValueError(f"Missing configuration for placeholder: {placeholder_name}")
        return True

    def list_templates(self):
        return self.repository.list_templates()

    def get_template(self, template_id: int):
        template = self.repository.get_by_id(template_id)
        if not template:
            raise ValueError("Template not found")
        return template

    def create_template(self, payload):
        placeholders = payload.placeholders or self.parse_placeholders(payload.content)
        final_placeholders = []
        seen = set()
        for item in placeholders:
            if isinstance(item, dict):
                item_name = item.get("placeholder_name", "")
                item_required = item.get("required", True)
                item_fallback = item.get("fallback_value")
            else:
                item_name = getattr(item, "placeholder_name", "")
                item_required = getattr(item, "required", True)
                item_fallback = getattr(item, "fallback_value", None)
            name = str(item_name).strip()
            if not name:
                continue
            if name in seen:
                continue
            seen.add(name)
            final_placeholders.append({
                "placeholder_name": name,
                "required": item_required,
                "fallback_value": item_fallback,
            })

        template = self.repository.create(payload.name, payload.title, payload.content)
        self.repository.replace_placeholders(template, final_placeholders)
        template = self.repository.get_by_id(template.id)
        return template

    def update_template(self, template_id: int, payload):
        template = self.get_template(template_id)
        updated_template = self.repository.update(template, payload.name, payload.title, payload.content)
        if payload.placeholders is not None:
            final_placeholders = []
            seen = set()
            for item in payload.placeholders:
                if isinstance(item, dict):
                    item_name = item.get("placeholder_name", "")
                    item_required = item.get("required", True)
                    item_fallback = item.get("fallback_value")
                else:
                    item_name = getattr(item, "placeholder_name", "")
                    item_required = getattr(item, "required", True)
                    item_fallback = getattr(item, "fallback_value", None)
                item_name = str(item_name).strip()
                if item_name in seen or not item_name:
                    continue
                seen.add(item_name)
                final_placeholders.append({
                    "placeholder_name": item_name,
                    "required": item_required,
                    "fallback_value": item_fallback,
                })
            self.repository.replace_placeholders(updated_template, final_placeholders)
        return self.repository.get_by_id(updated_template.id)
