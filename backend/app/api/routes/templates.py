from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.template import TemplateCreate, TemplateRead, TemplateUpdate
from app.services.template_service import TemplateService

router = APIRouter(prefix="/templates", tags=["templates"])


@router.post("", response_model=TemplateRead, status_code=status.HTTP_201_CREATED)
def create_template(payload: TemplateCreate, db: Session = Depends(get_db)):
    service = TemplateService(db)
    try:
        template = service.create_template(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return template


@router.get("", response_model=List[TemplateRead])
def list_templates(db: Session = Depends(get_db)):
    return TemplateService(db).list_templates()


@router.get("/{template_id}", response_model=TemplateRead)
def get_template(template_id: int, db: Session = Depends(get_db)):
    try:
        return TemplateService(db).get_template(template_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put("/{template_id}", response_model=TemplateRead)
def update_template(template_id: int, payload: TemplateUpdate, db: Session = Depends(get_db)):
    try:
        return TemplateService(db).update_template(template_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
