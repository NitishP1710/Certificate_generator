from datetime import datetime

from sqlalchemy.orm import Session

from app.models.generation import GenerationJob, GeneratedCertificate


class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_job(self, template_id: int, source_file_path: str | None = None, source_file_name: str | None = None):
        job = GenerationJob(
            template_id=template_id,
            status="PENDING",
            total_count=0,
            success_count=0,
            failed_count=0,
            pending_count=0,
            processing_count=0,
            source_file_path=source_file_path,
            source_file_name=source_file_name,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_job_by_id(self, job_id: int):
        return self.db.query(GenerationJob).filter(GenerationJob.id == job_id).first()

    def list_jobs(self):
        return self.db.query(GenerationJob).order_by(GenerationJob.created_at.desc()).all()

    def add_certificate(self, job_id: int, row_number: int, recipient_data: dict | None):
        certificate = GeneratedCertificate(
            job_id=job_id,
            row_number=row_number,
            recipient_data=recipient_data,
            status="PENDING",
        )
        self.db.add(certificate)
        self.db.commit()
        self.db.refresh(certificate)
        return certificate

    def update_job_status(self, job: GenerationJob, status: str, error_message: str | None = None):
        job.status = status
        if error_message:
            job.error_message = error_message
        if status in {"COMPLETED", "COMPLETED_WITH_ERRORS", "FAILED"}:
            job.completed_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(job)
        return job

    def update_certificate(self, certificate: GeneratedCertificate, status: str, file_path: str | None = None,
                           error_message: str | None = None, certificate_name: str | None = None):
        certificate.status = status
        if file_path is not None:
            certificate.file_path = file_path
        if error_message is not None:
            certificate.error_message = error_message
        if certificate_name is not None:
            certificate.certificate_name = certificate_name
        if status in {"SUCCESS", "FAILED"}:
            certificate.completed_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(certificate)
        return certificate

    def get_certificates_by_job(self, job_id: int):
        return (
            self.db.query(GeneratedCertificate)
            .filter(GeneratedCertificate.job_id == job_id)
            .order_by(GeneratedCertificate.row_number.asc())
            .all()
        )
