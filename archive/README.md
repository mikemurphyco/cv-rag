# Archive

This directory contains deprecated files kept for reference and project history.

## Contents

### Python Scripts (archive/scripts/)

These scripts were part of the original Python-based approach before migrating to n8n-native workflows:

- **`chunker.py`** - Text chunking script (replaced by n8n Recursive Text Splitter node)
- **`embedder.py`** - Embedding generation script (replaced by n8n Embeddings Ollama node)
- **`embedding_service.py`** - Flask embedding service (replaced by direct n8n → Ollama calls)
- **`query.py`** - Query testing script (replaced by direct curl tests to n8n webhooks)

**Why deprecated:** The project now uses n8n's built-in AI/LangChain nodes, which better demonstrates n8n expertise for portfolio purposes.

### Development Documentation

These markdown files document various development experiments and deployment attempts:

- **`BUILD_SUMMARY.md`** - Early development notes
- **`DEPLOY-NOW.md`** - Deployment attempt notes
- **`DEPLOYMENT.md`** - Old deployment guide
- **`DOCKER-DEPLOYMENT-SUMMARY.md`** - Docker deployment experiments
- **`NEXT-STEPS.md`** - Old project planning notes
- **`TRAEFIK-SETUP.md`** - Traefik reverse proxy setup notes
- **`TRANSFER.md`** - Project transfer notes

**Why kept:** Useful for understanding the project's evolution and can inform future similar projects.

### Infrastructure Scripts

- **`docker-compose.yml`** - Docker Compose configuration (not currently used in production)
- **`setup-vps.sh`** - VPS setup script (superseded by manual setup)

**Why kept:** May be useful for future Docker-based deployments or as reference for setting up new VPS instances.

## Current Production Setup

The production version of CV-RAG uses:

1. **n8n workflows** (see `/n8n/` directory):
   - `workflow-1-document-ingestion.json` - Document ingestion
   - `workflow-2-query-pipeline.json` - Query handling (v2.2 production version)

2. **Testing scripts** (see `/scripts/` directory):
   - `test_workflow.py` - End-to-end workflow testing
   - `clean_database.py` - Database management
   - `test_ollama_models.sh` - Ollama model testing
   - `check_ollama_status.sh` - Service status checks

3. **Streamlit frontend** (see `/streamlit/` directory):
   - `app.py` - Chat interface

## Need Help?

- **Quick setup:** See [QUICKSTART.md](../QUICKSTART.md)
- **Complete docs:** See [CLAUDE.md](../CLAUDE.md)
- **Portfolio overview:** See [README.md](../README.md)
- **n8n setup:** See [n8n/README.md](../n8n/README.md)

---

**Note:** Files in this archive are not maintained and may contain outdated information. Always refer to the main project documentation for current setup instructions.
