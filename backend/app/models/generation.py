from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("templates.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False)
    total_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pending_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    processing_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    source_file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    template: Mapped["Template"] = relationship("Template", back_populates="jobs")
    certificates: Mapped[list["GeneratedCertificate"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class GeneratedCertificate(Base):
    __tablename__ = "generated_certificates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("generation_jobs.id"), nullable=False, index=True)
    row_number: Mapped[int] = mapped_column(Integer, nullable=False)
    recipient_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    certificate_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    job: Mapped[GenerationJob] = relationship(back_populates="certificates")
