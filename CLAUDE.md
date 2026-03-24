# CLAUDE.md

## Project Overview
RegDoc Pipeline processes regulatory PDF documents, extracts content using PyMuPDF,
and generates structured metadata using local LLMs via Ollama.

## Tech Stack
- Python 3.13+ managed with uv
- PyMuPDF for PDF parsing
- Ollama for local LLM inference (Llama 3.2 3B, Phi-3 Mini)
- Pydantic for data validation

## Project Structure
- src/parser.py — PDF text extraction
- src/enricher.py — LLM-based metadata generation
- src/evaluator.py — Model benchmarking
- src/models.py — Pydantic schemas
- src/pipeline.py — CLI entry point

## Running
- Single doc: uv run python -m src.pipeline data/samples/example.pdf
- Benchmark: uv run python -m src.pipeline benchmark

## Code Style
- Type hints on all functions
- Pydantic models for all data structures
- Error handling around LLM responses (JSON parsing can fail)

## Key Design Decisions
- Low temperature (0.1) for LLM calls to improve JSON compliance
- Text truncated to 4000 chars to fit small model context windows
- Benchmark tracks JSON validity rate as a key metric