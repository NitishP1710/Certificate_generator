import io
import textwrap

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def render_certificate_pdf(template, row_data: dict) -> bytes:
    content = template.content
    for key, value in row_data.items():
        placeholder = "{{" + key + "}}"
        content = content.replace(placeholder, str(value) if value not in (None, "") else "")

    output = io.BytesIO()
    pdf = canvas.Canvas(output, pagesize=letter)
    pdf.setTitle(f"Certificate for {row_data.get('name', 'Recipient')}")
    pdf.setFillColorRGB(0.12, 0.12, 0.12)
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawCentredString(306, 760, template.title or "Certificate of Completion")

    pdf.setFont("Helvetica", 16)
    y = 680
    for line in content.splitlines():
        wrapped_lines = textwrap.wrap(line, width=70)
        if not wrapped_lines:
            wrapped_lines = [""]
        for wrapped in wrapped_lines:
            pdf.drawCentredString(306, y, wrapped)
            y -= 22
        if y < 80:
            pdf.showPage()
            y = 760
            pdf.setFont("Helvetica", 16)

    pdf.save()
    return output.getvalue()


def generate_certificate_pdf_for_job(template, row_data: dict, job_id: int, row_number: int):
    return render_certificate_pdf(template, row_data)
