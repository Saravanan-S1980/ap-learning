"""PDF text extraction using PyMuPDF (fitz)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import fitz  # PyMuPDF


# Minimum characters per page to be considered "text-based"
_TEXT_THRESHOLD = 50


@dataclass
class PageResult:
    page_number: int  # 1-based
    text: str
    image_based: bool  # True when extracted text < threshold


@dataclass
class ExtractionResult:
    text: str
    pages: int
    page_results: list[PageResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def extract_text(file_path: str | Path) -> ExtractionResult:
    """Extract plain text from a PDF file.

    Returns an ExtractionResult with:
    - text: concatenated text from all pages
    - pages: total page count
    - page_results: per-page details (text, image_based flag)
    - warnings: non-fatal issues (e.g., image-based pages, encrypted doc)

    Raises:
        ValueError: if the file is password-protected or cannot be opened
        RuntimeError: if PyMuPDF reports a corrupt or unsupported file
    """
    path = Path(file_path)

    try:
        doc = fitz.open(str(path))
    except fitz.FileDataError as exc:
        raise RuntimeError(f"Corrupt or unsupported file: {exc}") from exc
    except Exception as exc:
        raise RuntimeError(f"Could not open file: {exc}") from exc

    if doc.is_encrypted:
        doc.close()
        raise ValueError("PDF is password-protected. Please provide an unlocked file.")

    warnings: list[str] = []
    page_results: list[PageResult] = []
    all_text_parts: list[str] = []

    for i, page in enumerate(doc, start=1):
        try:
            page_text = page.get_text()
        except Exception:
            page_text = ""

        is_image_based = len(page_text.strip()) < _TEXT_THRESHOLD
        if is_image_based:
            warnings.append(
                f"Page {i} appears to be image-based (less than {_TEXT_THRESHOLD} "
                "characters extracted). OCR not yet supported — marker data may be missing."
            )

        page_results.append(PageResult(
            page_number=i,
            text=page_text,
            image_based=is_image_based,
        ))
        all_text_parts.append(page_text)

    doc.close()

    full_text = "\n".join(all_text_parts).strip()

    if not full_text:
        warnings.append(
            "No text could be extracted from this file. "
            "All pages appear to be image-based."
        )

    return ExtractionResult(
        text=full_text,
        pages=len(page_results),
        page_results=page_results,
        warnings=warnings,
    )
