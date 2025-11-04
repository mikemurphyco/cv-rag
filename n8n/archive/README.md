# Archive: Python-Based Approach

This folder contains documentation for the **original Python-heavy implementation** of the CV-RAG system.

## Why Archived?

The original approach required multiple Python services:
- Flask embedding service
- sentence-transformers library
- Python scripts for chunking and embedding
- n8n used primarily as an orchestrator

**This approach was replaced** with a cleaner **n8n-native implementation** that:
- Uses n8n's built-in AI/LangChain nodes
- Connects directly to Ollama (no Flask service needed)
- Better showcases n8n expertise for portfolio/interviews
- Simpler to maintain and deploy

## Archived Files

- `README-python-approach.md` - Original setup guide
- `QUICKSTART-python-approach.md` - Original quick start
- `ARCHITECTURE-python-approach.md` - Original architecture docs
- `cv-rag-workflow-python.json` - Original n8n workflow (single file)

## Current Implementation

See the main n8n README for the current n8n-native approach:
- `/n8n/README.md` - n8n-native setup guide
- `/n8n/workflow-1-document-ingestion.json` - Document ingestion workflow
- `/n8n/workflow-2-query-pipeline.json` - Query pipeline workflow

## If You Need the Old Approach

The Python scripts are still in the repository but marked as deprecated:
- `scripts/embedding_service.py` - DEPRECATED
- `scripts/embedder.py` - DEPRECATED
- `scripts/chunker.py` - DEPRECATED

These files are kept for reference but are not used in the current implementation.

---

**Last Updated:** 2025-11-03
**Reason:** Migrated to n8n-native approach for better portfolio value
