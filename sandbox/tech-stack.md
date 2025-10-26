## Tech Stack

- **Data Storage**: Neon Postgres with pgvector for vector embeddings (scalable and managed).
- **Embedding Model**: Use a lightweight model like nomic-embed-text or Hugging Face's sentence-transformers for chunk embeddings.
- **LLM**: Ollama running on your VPS (e.g., Llama 3 for generation).
- **Workflow Automation**: n8n for orchestrating ingestion, querying, and responses.
- **Chunking & Processing**: Python scripts (using libraries like langchain or custom code for simplicity).
- **Frontend**: Streamlit for the interactive chat interface.
- **Deployment**: GitHub repo for version control; host Streamlit on Streamlit Cloud or your VPS; n8n and Ollama on VPS.
- **Other Tools**: Docker for containerizing Ollama if needed; requests for API calls.
- 
CV-RAG/
├── README.md          # This file
├── docs/              # Source documents
│   ├── Resume.md      # Your main resume content (already created)
│   └── Supplemental.md # Extra info: YouTube links, courses, bios, etc.
├── scripts/           # Python scripts for processing
│   ├── chunker.py     # Script to chunk docs
│   ├── embedder.py    # Script to generate and store embeddings
│   └── query.py       # Script to test queries
├── n8n/               # n8n workflow exports (JSON files)
├── streamlit/         # Streamlit app files
│   └── app.py         # Main Streamlit script
├── .gitignore         # Ignore venv, secrets, etc.
└── requirements.txt   # Python dependencies