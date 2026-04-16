import io
from textwrap import wrap

import pdfplumber
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text_parts: list[str] = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_parts.append(page_text.strip())
    return "\n\n".join(text_parts)


def build_pdf_from_text(text: str) -> bytes:
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)
    width, height = A4

    x_margin = 40
    y = height - 40
    line_height = 15
    max_chars_per_line = 95

    for paragraph in text.splitlines():
        lines = wrap(paragraph, max_chars_per_line) if paragraph else [""]
        for line in lines:
            c.drawString(x_margin, y, line)
            y -= line_height
            if y <= 50:
                c.showPage()
                y = height - 40
        y -= 5

    c.save()
    packet.seek(0)
    return packet.read()
