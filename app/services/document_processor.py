import io
import tempfile
from pathlib import Path

from docx import Document
from pypdf import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return text.strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        doc = Document(tmp_path)
        text = "\n".join(p.text for p in doc.paragraphs)
    finally:
        Path(tmp_path).unlink(missing_ok=True)
    return text.strip()


def extract_text(file_bytes: bytes, filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext == ".docx":
        return extract_text_from_docx(file_bytes)
    else:
        return file_bytes.decode("utf-8", errors="replace").strip()
