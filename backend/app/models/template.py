from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Template(Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    placeholders: Mapped[list["TemplatePlaceholder"]] = relationship(
        back_populates="template", cascade="all, delete-orphan"
    )
    jobs: Mapped[list["GenerationJob"]] = relationship(back_populates="template")


class TemplatePlaceholder(Base):
    __tablename__ = "template_placeholders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("templates.id"), nullable=False, index=True)
    placeholder_name: Mapped[str] = mapped_column(String(128), nullable=False)
    required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fallback_value: Mapped[str | None] = mapped_column(String(255), nullable=True)

    template: Mapped[Template] = relationship(back_populates="placeholders")
