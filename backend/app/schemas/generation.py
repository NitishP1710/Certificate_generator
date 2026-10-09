from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class ValidationErrorItem(BaseModel):
    row: Optional[int] = None
    field: Optional[str] = None
    message: str


class ExcelValidationResult(BaseModel):
    valid: bool
    total_rows: int
    valid_rows: int
    invalid_rows: int
    errors: List[ValidationErrorItem] = []
    missing_columns: List[str] = []
    unexpected_columns: List[str] = []
    file_name: Optional[str] = None


class GenerationJobCreate(BaseModel):
    template_id: int
    file_name: Optional[str] = None


class GenerationJobSummary(BaseModel):
    id: int
    template_id: int
    status: str
    total_count: int
    success_count: int
    failed_count: int
    pending_count: int
    processing_count: int
    source_file_name: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]

    class Config:
        from_attributes = True


class CertificateRead(BaseModel):
    id: int
    job_id: int
    row_number: int
    status: str
    file_path: Optional[str]
    certificate_name: Optional[str]
    error_message: Optional[str]
    recipient_data: Optional[dict[str, Any]]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class GenerationJobRead(BaseModel):
    id: int
    template_id: int
    status: str
    total_count: int
    success_count: int
    failed_count: int
    pending_count: int
    processing_count: int
    created_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
    certificates: List[CertificateRead] = []

    class Config:
        from_attributes = True
