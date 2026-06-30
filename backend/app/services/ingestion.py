import io
from pypdf import PdfReader
from docx import Document
from PIL import Image
import pytesseract

from app.config import settings


def extract_text(file_bytes: bytes, file_type: str) -> str:
    """Extrage text brut dintr-un fisier PDF, DOCX sau imagine (OCR)."""
    file_type = file_type.lower()

    if file_type == "pdf":
        reader = PdfReader(io.BytesIO(file_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if file_type in ("docx", "doc"):
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs)

    if file_type in ("png", "jpg", "jpeg"):
        image = Image.open(io.BytesIO(file_bytes))
        return pytesseract.image_to_string(image, lang="ron+eng")

    raise ValueError(f"Tip de fisier nesuportat: {file_type}")


def chunk_text(
    text: str,
    chunk_size: int = settings.CHUNK_SIZE,
    overlap: int = settings.CHUNK_OVERLAP,
) -> list[str]:
    """Imparte textul in bucati cu overlap, pentru a pastra contextul la margini."""
    words = text.split()
    if not words:
        return []

    chunks = []
    step = max(chunk_size - overlap, 1)
    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
        i += step

    return chunks
