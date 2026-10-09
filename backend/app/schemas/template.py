from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TemplatePlaceholderInput(BaseModel):
    placeholder_name: str = Field(..., min_length=1)
    required: bool = True
    fallback_value: Optional[str] = None


class TemplateCreate(BaseModel):
    name: str = Field(..., min_length=1)
    title: Optional[str] = None
    content: str = Field(..., min_length=1)
    placeholders: List[TemplatePlaceholderInput] = []


class TemplatePlaceholderRead(BaseModel):
    id: int
    placeholder_name: str
    required: bool
    fallback_value: Optional[str] = None

    class Config:
        from_attributes = True


class TemplateRead(BaseModel):
    id: int
    name: str
    title: Optional[str]
    content: str
    created_at: datetime
    updated_at: datetime
    placeholders: List[TemplatePlaceholderRead]

    class Config:
        from_attributes = True


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    placeholders: Optional[List[TemplatePlaceholderInput]] = None
