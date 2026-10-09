# Bulk Certificate Generator

A full-stack certificate generation system for creating bulk PDF certificates from Excel data and reusable templates. The app supports template management, row-level validation, asynchronous generation, per-certificate failure isolation, progress tracking, and PDF retrieval.

## Features

- Create and manage certificate templates
- Extract and validate placeholders from template content
- Upload Excel files and validate required columns and row values
- Generate certificates in bulk with background processing
- Track generation jobs and per-row success/failure results
- Download individual generated certificate PDFs
- Hosted PostgreSQL database configuration
- Neon Object Storage bucket for Excel uploads and generated PDFs
- React dashboard frontend with Vite
- FastAPI backend with SQLAlchemy and Pydantic validation

## Tech Stack

- Backend: FastAPI, SQLAlchemy, Pydantic, Python 3.12
- Database: Hosted PostgreSQL via `DATABASE_URL`
- Excel processing: openpyxl
- PDF generation: reportlab
- Frontend: React + Vite
- Testing: pytest

## Repository Structure

- [backend](backend): FastAPI app, SQLAlchemy models, services, validators, routes, and tests
- [frontend](frontend): React dashboard and Vite app
- [.env.example](.env.example): environment template for backend configuration

## Requirements

- Python 3.12+
- Node.js 18+
- npm

## Local Setup

1. Create the backend environment:

   ```bash
   cd backend
   python3 -m venv .venv
   . .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy the environment template and set the hosted PostgreSQL connection string:

   ```bash
   cd ..
   cp .env.example .env
   ```

3. Start the backend:

   ```bash
   cd backend
   . .venv/bin/activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. Start the frontend:

   ```bash
   cd frontend
   npm install
   npm run dev -- --host 0.0.0.0
   ```

5. Open the app in a browser:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API docs: http://localhost:8000/docs

## Environment Configuration

The backend reads configuration from environment variables. A hosted PostgreSQL database is required; the application does not create or use a local SQLite database.

Example values:

```env
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:5432/certificate_app?sslmode=require
APP_ENV=production
SECRET_KEY=replace-with-a-long-random-value
AWS_ACCESS_KEY_ID=your_neon_storage_access_key
AWS_SECRET_ACCESS_KEY=your_neon_storage_secret_key
AWS_ENDPOINT_URL_S3=https://your-neon-storage-endpoint
AWS_REGION=us-east-2
```

Use the connection string supplied by your hosted PostgreSQL provider. Both standard PostgreSQL URLs and provider URLs beginning with `postgres://` are accepted:

```env
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:5432/certificate_app
```

Neon provisions the `certificate` bucket from [neon.ts](neon.ts). Uploaded Excel files are stored under `uploads/`, and generated PDFs are stored under `certificates/{job_id}/`. Only the object key is saved in PostgreSQL.

## Template and Excel Format

A template uses placeholders like `{{name}}`, `{{course}}`, and `{{date}}`.

Example content:

```text
This certificate is proudly presented to

{{name}}

for successfully completing

{{course}}

on

{{date}}
```

Excel requirements:

- The first row must contain headers.
- Header names must match the placeholders used in the template.
- Required columns cannot be empty for any valid row.
- Invalid rows are reported without stopping successful ones from being generated.

Example workbook:

| name  | course | date       |
| ----- | ------ | ---------- |
| Rahul | Python | 2026-01-10 |
| Priya | Java   | 2026-01-11 |
| Amit  | React  | 2026-01-12 |

## Application Flow

1. Create a template in the dashboard or via the API.
2. Upload an Excel file that matches the template placeholders.
3. Validate the workbook to detect missing/extra/empty required data.
4. Start a bulk generation job.
5. Monitor the job status and certificate result list.
6. Download generated PDF certificates individually.

## API Overview

### Templates

- `POST /api/templates`
- `GET /api/templates`
- `GET /api/templates/{template_id}`
- `PUT /api/templates/{template_id}`

### Validation

- `POST /api/templates/{template_id}/validate-excel`

### Generation

- `POST /api/generation`
- `GET /api/generation/{job_id}`
- `GET /api/generation/{job_id}/certificates`

### Certificates

- `GET /api/certificates/{certificate_id}`

## Testing

Run backend tests with:

```bash
cd backend
. .venv/bin/activate
pytest -q
```

The project includes validation and generation tests covering template creation, Excel validation, and generation behavior.

## Verification

The app was verified locally against the live backend. The final validation used an HTTP client to:

- create a template,
- validate a valid Excel file,
- start a generation job,
- confirm the job reached `COMPLETED`,
- fetch the generated certificate list,
- download a real PDF with HTTP 200 and content type `application/pdf`.

This confirms the end-to-end flow is working in practice.

## Notes

- The project is intentionally structured without unnecessary microservices.
- Background generation is handled within the app process to keep the solution simple and deployment-friendly.
- The deployed application requires hosted PostgreSQL and Neon Object Storage credentials. Test runs explicitly use isolated SQLite and local test storage and do not affect Neon.
