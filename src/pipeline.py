# src/pipeline.py: Join everything together

from pathlib import Path
from .parser import parse_pdf
from .enricher import enrich_document
from .evaluator import run_benchmark


def process_single(pdf_path: str, model: str = "llama3.2:3b"):
    """Process a single PDF end-to-end."""
    path = Path(pdf_path)
    print(f"Parsing: {path.name}")
    parsed = parse_pdf(path)
    print(f"  Pages: {parsed.total_pages} | Words: {len(parsed.raw_text.split())}")

    print(f"Enriching with {model}...")
    metadata, debug = enrich_document(parsed, model=model)

    if metadata:
        print(f"\n--- Generated Metadata ---")
        print(f"  Type:       {metadata.document_type}")
        print(f"  Title:      {metadata.title}")
        print(f"  Language:   {metadata.language}")
        print(f"  Summary:    {metadata.summary[:150]}...")
        print(f"  Entities:   {', '.join(metadata.key_entities[:5])}")
        print(f"  Topics:     {', '.join(metadata.key_topics[:5])}")
        print(f"  References: {', '.join(metadata.regulatory_references[:3])}")
        print(f"  Confidence: {metadata.confidence_score}")
        print(f"  Latency:    {debug['latency_seconds']:.1f}s")
    else:
        print(f"  FAILED: {debug}")


def benchmark(pdf_dir: str = "data/samples"):
    """Run full benchmark across all PDFs and models."""
    run_benchmark(Path(pdf_dir))


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "benchmark":
        benchmark()
    elif len(sys.argv) > 1:
        process_single(sys.argv[1])
    else:
        print("Usage:")
        print("  uv run python -m src.pipeline <path_to_pdf>")
        print("  uv run python -m src.pipeline benchmark")