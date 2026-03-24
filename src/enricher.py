# src/enricher.py

import json
import time
import ollama
from .models import DocumentMetadata, ParsedDocument

SYSTEM_PROMPT = """You are a document analysis assistant for a regulatory technology platform.
Your job is to analyze documents and extract structured metadata.

You MUST respond with ONLY valid JSON matching this exact schema:
{
  "document_type": "one of: annual_report, regulation, policy, form, legal, financial, technical, other",
  "title": "the document title, inferred from content if not explicit",
  "summary": "2-3 sentence summary of the document's purpose and content",
  "language": "two-letter language code (en, es, etc.)",
  "key_entities": ["list of organizations, people, or regulatory bodies mentioned"],
  "key_topics": ["list of main subjects covered"],
  "regulatory_references": ["any specific laws, standards, articles, or regulations cited"],
  "confidence_score": 0.85
}

Respond with ONLY the JSON object. No markdown, no explanation, no preamble."""


def enrich_document(
    parsed: ParsedDocument,
    model: str = "llama3.2:3b",
    max_context_chars: int = 4000
) -> tuple[DocumentMetadata | None, dict]:
    """
    Send parsed document text to a local LLM and get structured metadata.
    Returns (metadata, debug_info) tuple.
    """
    # Truncate to fit context window — real systems use chunking
    text_sample = parsed.raw_text[:max_context_chars]

    user_prompt = f"""Analyze the following document and extract metadata.

Document filename: {parsed.filename}
Total pages: {parsed.total_pages}
PDF metadata: {json.dumps(parsed.pdf_metadata)}

--- DOCUMENT TEXT ---
{text_sample}
--- END ---

Respond with ONLY the JSON metadata object."""

    start_time = time.time()

    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            options={"temperature": 0.1}  # Low temp for structured output
        )
        raw_response = response["message"]["content"]
        latency = time.time() - start_time

        # Attempt to parse JSON from LLM response
        metadata = _parse_llm_json(raw_response, parsed.filename)

        debug_info = {
            "model": model,
            "latency_seconds": round(latency, 2),
            "json_valid": metadata is not None,
            "raw_response": raw_response,
            "input_chars": len(text_sample),
        }

        return metadata, debug_info

    except Exception as e:
        return None, {
            "model": model,
            "error": str(e),
            "json_valid": False,
            "latency_seconds": time.time() - start_time,
        }


def _parse_llm_json(raw: str, filename: str) -> DocumentMetadata | None:
    """Attempt to extract valid JSON from LLM response."""
    # Try direct parsing first
    try:
        data = json.loads(raw)
        data["filename"] = filename
        return DocumentMetadata(**data)
    except (json.JSONDecodeError, Exception):
        pass

    # Try extracting JSON from markdown code blocks
    if "```" in raw:
        try:
            json_str = raw.split("```")[1]
            if json_str.startswith("json"):
                json_str = json_str[4:]
            data = json.loads(json_str.strip())
            data["filename"] = filename
            return DocumentMetadata(**data)
        except (json.JSONDecodeError, IndexError, Exception):
            pass


# Try fixing truncated JSON (missing closing brace)
    cleaned = raw.strip()
    if not cleaned.endswith("}"):
        cleaned += "}"
    try:
        data = json.loads(cleaned)
        data["filename"] = filename
        return DocumentMetadata(**data)
    except (json.JSONDecodeError, Exception):
        pass

    return None
