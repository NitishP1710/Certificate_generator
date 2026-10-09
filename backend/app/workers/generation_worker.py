import io

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.services.generation_service import GenerationService
from app.storage import storage


async def process_generation_job(job_id: int, file_key: str):
    db: Session = SessionLocal()
    try:
        service = GenerationService(db)
        from fastapi import UploadFile

        upload = UploadFile(filename=file_key.rsplit("/", 1)[-1], file=io.BytesIO(storage.download_bytes(file_key)))
        service.process_generation(job_id, upload)
    finally:
        db.close()
