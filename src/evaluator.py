# src/evaluator.py

import json
from pathlib import Path
from datetime import datetime, timezone
from .parser import parse_pdf
from .enricher import enrich_document
from .models import BenchmarkResult

MODELS_TO_TEST = ["llama3.2:3b", "phi3:mini"]


def run_benchmark(
    pdf_dir: Path,
    models: list[str] = MODELS_TO_TEST,
    output_dir: Path = Path("results")
) -> list[BenchmarkResult]:
    """Run all PDFs through all models and collect results."""
    output_dir.mkdir(exist_ok=True)
    results = []

    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDFs to process")
    print(f"Testing models: {models}")
    print("-" * 60)

    for pdf_path in pdf_files:
        print(f"\nProcessing: {pdf_path.name}")
        parsed = parse_pdf(pdf_path)

        for model in models:
            print(f"  Model: {model}...", end=" ", flush=True)
            metadata, debug = enrich_document(parsed, model=model)

            result = BenchmarkResult(
                model_name=model,
                document=pdf_path.name,
                latency_seconds=debug.get("latency_seconds", 0),
                metadata=metadata,
                json_valid=debug.get("json_valid", False),
                raw_response=debug.get("raw_response", ""),
            )
            results.append(result)

            status = "OK" if metadata else "FAILED"
            print(f"{status} ({debug.get('latency_seconds', 0):.1f}s)")

    # Save results
    _save_results(results, output_dir)
    _print_summary(results)

    return results


def _save_results(results: list[BenchmarkResult], output_dir: Path):
    """Save benchmark results to JSON."""
    data = []
    for r in results:
        entry = {
            "model": r.model_name,
            "document": r.document,
            "latency_seconds": r.latency_seconds,
            "json_valid": r.json_valid,
            "metadata": r.metadata.model_dump() if r.metadata else None,
        }
        data.append(entry)

    output_path = output_dir / f"benchmark_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"\nResults saved to: {output_path}")


def _print_summary(results: list[BenchmarkResult]):
    """Print a comparison summary table."""
    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)

    models = set(r.model_name for r in results)
    for model in sorted(models):
        model_results = [r for r in results if r.model_name == model]
        total = len(model_results)
        valid = sum(1 for r in model_results if r.json_valid)
        avg_latency = sum(r.latency_seconds for r in model_results) / total if total else 0

        print(f"\n{model}:")
        print(f"  JSON compliance: {valid}/{total} ({100*valid/total:.0f}%)")
        print(f"  Avg latency:     {avg_latency:.1f}s")
        print(f"  Documents:       {total}")