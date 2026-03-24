RegDoc Pipeline
A regulatory document processing pipeline that extracts content from PDF filings and generates structured metadata using local LLMs. Built as a proof of concept for AI powered document management in RegTech.
What It Does

Parses PDFs — Extracts text, page structure, and file metadata using PyMuPDF
Generates metadata with local LLMs: Classifies document type, extracts entities, topics, regulatory references, and generates summaries via Ollama
Benchmarks model configurations: Compares Llama 3.2 3B vs Phi-3 Mini on JSON compliance, latency, and output quality

Architecture
PDF File → PyMuPDF Parser → Extracted Text → Local LLM (Ollama) → Structured Metadata (JSON)
Tech Stack

Python 3.13 managed with uv
PyMuPDF for PDF text extraction
Ollama for local LLM inference
Pydantic for data validation and structured schemas
Llama 3.2 3B / Phi-3 Mini as evaluation targets

Setup
Prerequisites

macOS with Apple Silicon (M1+) or Linux/Windows with NVIDIA GPU (6GB+ VRAM)
uv package manager
Ollama installed and running

Installation
bashgit clone https://github.com/Hub3rt-M4D/RegDoc_Pipeline.git
cd RegDoc_Pipeline
uv sync
ollama pull llama3.2:3b
ollama pull phi3:mini
Environment
Copy .env.example and configure as needed:
bashcp .env.example .env
Usage
Process a single document
bashuv run python -m src.pipeline data/samples/tesla.pdf
Run benchmark across all documents
bashuv run python -m src.pipeline benchmark
Results are saved to the results/ directory as timestamped JSON files.
Benchmark Results
Tested on 4 SEC filings (10-K and 10-Q reports) on Apple Silicon M-series:
ModelJSON ComplianceAvg LatencyDocumentsLlama 3.2 3B4/4 (100%)4.0s4Phi-3 Mini3/4 (75%)7.0s4
Key finding: Llama 3.2 3B produced valid structured JSON on every document at nearly half the latency of Phi-3 Mini. Phi-3 failed JSON validation on one document (Dell 10-K), likely due to output truncation.
Design Decisions

Low temperature (0.1) for LLM calls to maximize JSON compliance over creative output
Text truncated to 4,000 characters to fit within small model context windows, production systems would use chunking strategies
Fallback JSON parsing handles truncated output (missing closing braces), a common issue with small local models
Encrypted PDF detection at parse time with clear error messages instead of silent failures
Pydantic validation ensures all metadata conforms to a strict schema before downstream use

Limitations and Future Work

Small test set (4 English-language SEC filings). Would expand to include Spanish-language regulations, policy documents, and varied formats
Metadata quality is not scored beyond JSON validity. A production system would need precision/recall metrics against labeled ground truth
No chunking strategy for long documents. Currently truncates to first 4,000 characters
No embedding generation or vector storage. Could extend with pgvector for semantic retrieval

Project Structure
├── src/
│   ├── models.py       # Pydantic schemas for documents and metadata
│   ├── parser.py       # PDF text extraction with PyMuPDF
│   ├── enricher.py     # LLM-based metadata generation via Ollama
│   ├── evaluator.py    # Multi-model benchmarking
│   └── pipeline.py     # CLI entry point
├── data/samples/       # Sample PDF documents
├── results/            # Benchmark output (JSON)
├── CLAUDE.md           # AI assistant context file
├── pyproject.toml      # Project config and dependencies
└── .env.example        # Environment variable template