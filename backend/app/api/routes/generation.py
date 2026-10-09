import asyncio
import uuid
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.generation import ExcelValidationResult, GenerationJobRead
from app.services.generation_service import GenerationService
from app.storage import storage
from app.workers.generation_worker import process_generation_job

router = APIRouter(tags=["generation"])


@router.post("/templates/{template_id}/validate-excel", response_model=dict)
def validate_excel(template_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    service = GenerationService(db)
    try:
        result = service.validate_upload(template_id, file)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return result


@router.post("/generation", response_model=dict)
async def create_generation_job(
    template_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    service = GenerationService(db)
    try:
        validation = service.validate_upload(template_id, file)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if not validation["valid"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": "Excel validation failed", "validation": validation})

    file_bytes = await file.read()
    stored_name = f"{uuid.uuid4()}_{file.filename or 'upload.xlsx'}"
    stored_key = storage.upload_bytes(
        f"uploads/{stored_name}",
        file_bytes,
        file.content_type or "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    job = service.create_job(template_id)
    job.source_file_path = stored_key
    job.source_file_name = file.filename or stored_name
    db.commit()
    db.refresh(job)

    asyncio.create_task(process_generation_job(job.id, stored_key))
    return {"job_id": job.id, "status": job.status, "message": "Generation started"}


@router.get("/generation/{job_id}", response_model=GenerationJobRead)
def get_generation_job(job_id: int, db: Session = Depends(get_db)):
    try:
        job = GenerationService(db).get_job_details(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return job


@router.get("/generation/{job_id}/certificates", response_model=List[dict])
def list_generation_certificates(job_id: int, db: Session = Depends(get_db)):
    try:
        certificates = GenerationService(db).get_certificates(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return [{
        "id": cert.id,
        "job_id": cert.job_id,
        "row_number": cert.row_number,
        "status": cert.status,
        "file_path": cert.file_path,
        "certificate_name": cert.certificate_name,
        "error_message": cert.error_message,
        "recipient_data": cert.recipient_data,
        "created_at": cert.created_at,
        "completed_at": cert.completed_at,
    } for cert in certificates]
