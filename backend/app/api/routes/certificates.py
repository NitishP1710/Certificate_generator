from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO

from app.database import get_db
from app.repositories.job_repository import JobRepository
from app.storage import storage

router = APIRouter(tags=["certificates"])


@router.get("/certificates/{certificate_id}")
def download_certificate(certificate_id: int, db: Session = Depends(get_db)):
    certificate = db.query(JobRepository(db).get_certificates_by_job.__annotations__.get("return", None)) if False else None
    # Use a direct SQLAlchemy query instead of the repository helper for a single certificate lookup.
    from app.models.generation import GeneratedCertificate

    cert = db.query(GeneratedCertificate).filter(GeneratedCertificate.id == certificate_id).first()
    if cert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found")
    if not cert.file_path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Certificate file is not available")
    try:
        contents = storage.download_bytes(cert.file_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate file is not available") from exc
    return StreamingResponse(
        BytesIO(contents),
        headers={"Content-Disposition": f'attachment; filename="{cert.certificate_name or f"certificate_{cert.id}.pdf"}"'},
        media_type="application/pdf",
    )
