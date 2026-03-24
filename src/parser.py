# src/parser.py: PDF extraction using PyMuPDF

import fitz  # PyMuPDF
from pathlib import Path
from datetime import datetime, timezone
from .models import ParsedDocument, ParsedPage

def parse_pdf(filepath: Path) -> ParsedDocument:
    """Extract text and metadata from a PDF file."""
    doc = fitz.open(filepath)

    pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        pages.append(ParsedPage(
            page_number=i + 1,
            text=text,
            word_count=len(text.split())
        ))

    raw_text = "\n\n".join(p.text for p in pages)

    # Extract PDF-level metadata
    meta = doc.metadata or {}

    parsed = ParsedDocument(
        filename=filepath.name,
        total_pages=len(doc),
        pages=pages,
        raw_text=raw_text,
        pdf_metadata={
            "title": meta.get("title", ""),
            "author": meta.get("author", ""),
            "subject": meta.get("subject", ""),
            "creator": meta.get("creator", ""),
        },
        parsed_at=datetime.now(timezone.utc)
    )

    doc.close()
    return parsed