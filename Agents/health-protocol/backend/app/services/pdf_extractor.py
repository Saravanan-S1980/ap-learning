# PDF text extraction using PyMuPDF — placeholder
from pathlib import Path


def extract_text(file_path: str | Path) -> str:
    """Extract plain text from a PDF or image file."""
    import fitz  # PyMuPDF

    doc = fitz.open(str(file_path))
    pages = [page.get_text() for page in doc]
    doc.close()
    return "\n".join(pages)
