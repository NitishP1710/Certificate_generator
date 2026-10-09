import os
import sys
import time
from io import BytesIO

from openpyxl import Workbook
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///./test_certificate_app.db"

from app.database import Base, engine
from app.main import app

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
client = TestClient(app)


def _build_excel(rows):
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(rows[0])
    for row in rows[1:]:
        sheet.append(row)
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def test_template_creation_and_placeholder_detection():
    payload = {
        "name": "Course Template",
        "title": "Certificate of Completion",
        "content": "This certificate is proudly presented to\n\n{{name}}\n\nfor successfully completing\n\n{{course}}\n\non\n\n{{date}}",
    }
    response = client.post("/api/templates", json=payload)
    assert response.status_code == 201, response.text
    template = response.json()
    assert template["name"] == "Course Template"
    placeholder_names = {item["placeholder_name"] for item in template["placeholders"]}
    assert {"name", "course", "date"}.issubset(placeholder_names)


def test_excel_validation_missing_column_and_empty_required_values():
    template_response = client.post(
        "/api/templates",
        json={
            "name": "Validation Template",
            "title": "Certification",
            "content": "{{name}}\n{{course}}\n{{date}}",
        },
    )
    template_id = template_response.json()["id"]

    file_bytes = _build_excel([
        ["name", "course", "date"],
        ["Rahul", "", "2026-01-10"],
        ["Priya", "Java", "2026-01-11"],
    ])

    response = client.post(
        f"/api/templates/{template_id}/validate-excel",
        files={"file": ("bad.xlsx", file_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["valid"] is False
    assert body["invalid_rows"] >= 1
    assert any(error["field"] == "course" for error in body["errors"])


def test_generation_job_processes_success_and_failure_independently(monkeypatch):
    import app.services.generation_service as generation_service_module

    template_response = client.post(
        "/api/templates",
        json={
            "name": "Bulk Template",
            "title": "Course Completion",
            "content": "This is to certify {{name}} for {{course}} on {{date}}",
        },
    )
    template_id = template_response.json()["id"]

    real_generator = generation_service_module.generate_certificate_pdf_for_job

    def fake_generator(template, row_data, job_id, row_number):
        if row_number == 2:
            raise RuntimeError("Simulated PDF failure")
        return real_generator(template, row_data, job_id, row_number)

    monkeypatch.setattr(generation_service_module, "generate_certificate_pdf_for_job", fake_generator)

    file_bytes = _build_excel([
        ["name", "course", "date"],
        ["Rahul", "Python", "2026-01-10"],
        ["Priya", "Java", "2026-01-11"],
        ["Amit", "React", "2026-01-12"],
    ])

    response = client.post(
        "/api/generation",
        data={"template_id": template_id},
        files={"file": ("valid.xlsx", file_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert response.status_code == 200, response.text
    job_id = response.json()["job_id"]

    deadline = time.time() + 12
    while time.time() < deadline:
        job_response = client.get(f"/api/generation/{job_id}")
        status = job_response.json()["status"]
        if status in {"COMPLETED", "COMPLETED_WITH_ERRORS", "FAILED"}:
            break
        time.sleep(0.5)

    final_job = client.get(f"/api/generation/{job_id}").json()
    assert final_job["status"] in {"COMPLETED", "COMPLETED_WITH_ERRORS"}
    assert final_job["total_count"] == 3
    assert final_job["success_count"] == 2
    assert final_job["failed_count"] == 1

    cert_response = client.get(f"/api/generation/{job_id}/certificates")
    assert cert_response.status_code == 200, cert_response.text
    certs = cert_response.json()
    assert len(certs) == 3
    successful = [cert for cert in certs if cert["status"] == "SUCCESS"]
    failed = [cert for cert in certs if cert["status"] == "FAILED"]
    assert len(successful) == 2
    assert len(failed) == 1

    if successful:
        pdf = client.get(f"/api/certificates/{successful[0]['id']}")
        assert pdf.status_code == 200
        assert pdf.headers["content-type"].startswith("application/pdf")
