# src/models.py — Define your data schemas with Pydantic

from pydantic import BaseModel
from datetime import datetime

class ParsedPage(BaseModel):
    page_number: int
    text: str
    word_count: int

class ParsedDocument(BaseModel):
    filename: str
    total_pages: int
    pages: list[ParsedPage]
    raw_text: str               # full document text concatenated
    pdf_metadata: dict          # title, author, creation date from PDF metadata
    parsed_at: datetime

class DocumentMetadata(BaseModel):
    """LLM-generated metadata — this is what Accredea builds."""
    filename: str
    document_type: str          # e.g., "annual_report", "regulation", "policy", "form"
    title: str                  # extracted or inferred title
    summary: str                # 2-3 sentence summary
    language: str               # "en", "es", etc.
    key_entities: list[str]     # organizations, people, regulatory bodies mentioned
    key_topics: list[str]       # main subjects covered
    regulatory_references: list[str]  # any specific laws, standards, or regulations cited
    confidence_score: float     # LLM's self-assessed confidence (0-1)

class BenchmarkResult(BaseModel):
    model_name: str
    document: str
    latency_seconds: float
    metadata: DocumentMetadata | None
    json_valid: bool           # did the LLM return valid JSON?
    raw_response: str          # for debugging