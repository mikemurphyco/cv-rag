# CV-RAG: Interactive AI Resume Chat 🤖

**Chat with Mike Murphy's resume using RAG + n8n + Ollama**

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![n8n](https://img.shields.io/badge/n8n-EA4B71?style=for-the-badge&logo=n8n&logoColor=white)](https://n8n.io)
[![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.ai)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)

> An AI-powered resume you can actually talk to. Ask it anything about my experience, skills, tutorials, and projects. Built to showcase expertise in n8n workflow automation, RAG systems, vector databases, and self-hosted LLMs.

## 🎯 **What is This?**

This project is a **production-ready RAG (Retrieval-Augmented Generation) system** built entirely in **n8n using AI/LangChain nodes**. It transforms my resume and supplemental materials into an interactive chat interface where employers can ask questions and get AI-generated answers based on my actual experience.

**Why it's cool:**
- ✅ Demonstrates n8n AI workflow expertise (not just Python wrappers!)
- ✅ Shows understanding of RAG architecture and vector databases
- ✅ Self-hosted LLM on VPS (Ollama with llama3.2 + nomic-embed-text)
- ✅ Production-ready patterns (separate ingestion vs. query workflows)
- ✅ Beautiful Streamlit frontend that employers can actually use
- ✅ Perfect portfolio piece for n8n/AI engineering roles

**Live Demo:** [Coming Soon - Streamlit Cloud Deployment]

---

## 🏗️ **Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│  STREAMLIT FRONTEND                                         │
│  User asks: "What AI tutorials has Mike created?"           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  N8N WORKFLOW 2: Query Pipeline                             │
│                                                             │
│  Webhook → Embeddings Ollama → Postgres Vector Store →     │
│  Format Context → Ollama Chat Model → Response             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ├─────→ Ollama (VPS)
                         │       • nomic-embed-text
                         │       • llama3.2:latest
                         │
                         └─────→ Neon Postgres + pgvector
                                 • 25-30 resume chunks
                                 • 384-dim embeddings
```

### **Two n8n Workflows:**

**Workflow 1: Document Ingestion (One-time)**
- Read markdown files
- Split text into chunks (500 chars, 50 overlap)
- Generate embeddings (nomic-embed-text via Ollama)
- Store in Postgres with pgvector

**Workflow 2: Query Pipeline (Runtime)**
- Receive user question via webhook
- Convert to embedding vector
- Search vector database for top 3 similar chunks
- Build context-enhanced prompt
- Generate answer with Ollama llama3.2
- Return JSON to Streamlit

---

## 🚀 **Tech Stack**

| Component | Technology | Why |
|-----------|-----------|-----|
| **Workflow Engine** | n8n (self-hosted) | Visual AI workflow design with LangChain nodes |
| **Embedding Model** | Ollama nomic-embed-text | Optimized for embeddings, runs on VPS |
| **LLM** | Ollama llama3.2:latest | Fast, high-quality generation on 8GB VPS |
| **Vector Database** | Neon Postgres + pgvector | Cloud-managed, production-ready |
| **Text Processing** | n8n Text Splitter node | Recursive character splitting with overlap |
| **Frontend** | Streamlit | Beautiful chat UI with sample questions |
| **Infrastructure** | Hostinger VPS KVM2 (8GB) | Self-hosted n8n + Ollama |

---

## 📂 **Project Structure**

```
cv-rag/
├── README.md                   # This file
├── CLAUDE.md                   # Detailed project documentation
├── .env.example                # Environment variables template
├── requirements.txt            # Python dependencies (for Streamlit)
│
├── docs/                       # Source documents
│   ├── cv_mike-murphy.md       # Main resume content
│   ├── supplemental.md         # YouTube tutorials, courses, skills
│   └── setup_database.sql      # Postgres schema setup
│
├── n8n/                        # n8n workflows (import these!)
│   ├── workflow-1-document-ingestion.json  # Ingest & chunk docs
│   ├── workflow-2-query-pipeline.json      # Handle queries (production)
│   ├── README.md                           # 👈 START HERE - Complete setup guide
│   └── archive/                            # Older workflow versions
│
├── streamlit/                  # Frontend application
│   └── app.py                  # Main Streamlit app
│
├── scripts/                    # Testing & utilities
│   ├── test_workflow.py        # End-to-end workflow tests
│   ├── clean_database.py       # Database reset utility
│   └── test_ollama_models.sh   # Ollama model testing
│
└── archive/                    # Deprecated files (for reference)
    ├── scripts/                # Old Python-based approach
    └── *.md                    # Development notes
```

---

## ⚡ **Quick Start**

### **Prerequisites**

- n8n instance (self-hosted or cloud)
- Neon Postgres database
- VPS with Ollama installed
- Python 3.11+ (for Streamlit only)

### **Setup in 5 Steps**

**1. Pull required Ollama models on your VPS:**
```bash
ssh root@your-vps-ip
ollama pull nomic-embed-text
ollama pull llama3.2:latest
```

**2. Enable pgvector in Neon Postgres:**
```sql
-- Run in Neon SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;
```

**3. Import n8n workflows:**
- Open your n8n instance
- Import `n8n/workflow-1-document-ingestion.json`
- Import `n8n/workflow-2-query-pipeline.json`

**4. Configure credentials:**
- Add Neon Postgres credentials in both workflows
- Update Ollama base URL to your VPS IP
- Activate both workflows

**5. Test it:**
```bash
curl -X POST https://your-n8n.com/webhook/cv-rag-query \
  -H "Content-Type: application/json" \
  -d '{"query": "What programming languages does Mike know?"}'
```

**📖 Full setup guide:** See [n8n/README.md](n8n/README.md) for detailed step-by-step instructions.

---

## 🎨 **Streamlit Frontend**

The Streamlit app provides a clean, interactive interface for employers to chat with the resume.

**Features:**
- 6 pre-configured sample questions
- Real-time query → answer flow
- Tech stack display in sidebar
- Resume download buttons
- Mobile-responsive design

**Run locally:**
```bash
# Create .env file
echo "N8N_WEBHOOK_URL=https://your-n8n.com/webhook/cv-rag-query" > .env

# Install dependencies
pip install -r requirements.txt

# Run Streamlit
streamlit run streamlit/app.py
```

**Deploy to production:** See [Streamlit Cloud documentation](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)

---

## 🧠 **How RAG Works Here**

1. **Document Ingestion (Workflow 1):**
   - Resume markdown → Text chunks (500 chars each)
   - Each chunk → 384-dim embedding vector (nomic-embed-text)
   - Store chunks + vectors in Postgres

2. **Query Processing (Workflow 2):**
   - User question → Embedding vector
   - Vector similarity search (cosine distance)
   - Top 3 chunks retrieved
   - Context + question → Ollama llama3.2
   - Generated answer → User

**Example:**
```
Query: "What AI tutorials has Mike created?"
        ↓
Vector: [0.234, -0.567, 0.890, ...]
        ↓
Top Chunks:
  1. "YouTube tutorials on RAG systems..." (similarity: 0.92)
  2. "Created course on LangChain..." (similarity: 0.88)
  3. "Tutorial series on n8n automation..." (similarity: 0.85)
        ↓
Context → Ollama → Answer: "Mike has created several AI tutorials..."
```

---

## 📊 **n8n Nodes Used**

| Node | Type | Purpose |
|------|------|---------|
| **Webhook** | Trigger | Receives queries and ingestion requests |
| **Read Binary File** | Core | Loads markdown files |
| **Extract from File** | Core | Converts binary to text |
| **Recursive Text Splitter** | LangChain | Chunks text with overlap |
| **Embeddings Ollama** | LangChain | Generates embeddings via nomic-embed-text |
| **Postgres Vector Store** | LangChain | Insert/retrieve with pgvector |
| **Ollama Chat Model** | LangChain | Answer generation with llama3.2 |
| **Code** | Core | Context formatting, response structuring |
| **Respond to Webhook** | Core | Returns JSON to client |

---

## 🎥 **Use Cases**

### **For Job Applications**
- Add link to resume: "Interactive AI Resume: [Streamlit URL]"
- Include in cover letters
- Featured section on LinkedIn
- GitHub profile pinned repo

### **For Portfolio**
- Demonstrates n8n AI expertise
- Shows RAG implementation skills
- Proves VPS/infrastructure knowledge
- Example of production-ready code

### **For Content Creation**
- Tutorial series: "Building a RAG Resume with n8n"
- Blog post: "Why I Built an AI-Powered Resume"
- Demo video for YouTube

---

## 🔧 **Environment Variables**

Create a `.env` file (never commit this!):

```bash
# Neon Postgres connection
NEON_CONNECTION_STRING=postgresql://user:pass@host.neon.tech/db?sslmode=require

# n8n webhook URLs
N8N_WEBHOOK_URL=https://your-n8n.com/webhook/cv-rag-query

# Ollama API (if not in n8n workflow)
OLLAMA_API_URL=http://your-vps-ip:11434

# Models
OLLAMA_MODEL=llama3.2:latest
EMBEDDING_MODEL=nomic-embed-text
```

---

## 📈 **Performance**

| Metric | Value |
|--------|-------|
| **Query Response Time** | 2-5 seconds |
| **Embedding Generation** | ~100ms per chunk |
| **Vector Search** | <50ms (25-30 chunks) |
| **LLM Generation** | 2-4 seconds |
| **Chunks in Database** | 27 |
| **Top-K Retrieved** | 3 |
| **Embedding Dimension** | 384 |

---

## 🎓 **What This Demonstrates**

**For Employers:**
- ✅ n8n AI/LangChain node expertise
- ✅ Understanding of RAG architecture
- ✅ Vector database integration (pgvector)
- ✅ Self-hosted LLM orchestration
- ✅ Production workflow design
- ✅ Full-stack skills (backend + frontend)
- ✅ DevOps (VPS management, deployment)

**Interview Talking Points:**
> "I built a production RAG system entirely in n8n using LangChain nodes. I used Recursive Text Splitter for chunking, Embeddings Ollama with nomic-embed-text for vectorization, Postgres Vector Store for semantic search, and Ollama Chat Model for generation. I designed it with two workflows—ingestion and querying—following production best practices for separation of concerns."

---

## 🐛 **Troubleshooting**

See detailed troubleshooting in:
- [n8n/README.md](n8n/README.md) - Workflow setup and issues
- [QUICKSTART.md](QUICKSTART.md) - Quick setup issues
- [CLAUDE.md](Code/Projects/cv-rag/CLAUDE.md) - Complete project documentation

**Common Issues:**

| Problem | Solution |
|---------|----------|
| "Model not found" | `ollama pull nomic-embed-text` on VPS |
| "pgvector not enabled" | Run `CREATE EXTENSION vector;` in Neon |
| "Timeout error" | Check Ollama is running: `systemctl status ollama` |
| "No chunks retrieved" | Run Workflow 1 to ingest documents |

---

## 📝 **Documentation**

- **[README.md](Code/Projects/cv-rag/README.md)** - This file - Portfolio overview (START HERE)
- **[n8n/README.md](n8n/README.md)** - Complete n8n workflow setup guide
- **[QUICKSTART.md](QUICKSTART.md)** - Quick setup guide
- **[CLAUDE.md](Code/Projects/cv-rag/CLAUDE.md)** - Detailed technical documentation
- **[.env.example](.env.example)** - Environment variables template

---

## 🚀 **Roadmap**

- [x] Design n8n-native RAG workflows
- [x] Build document ingestion pipeline
- [x] Build query pipeline
- [x] Create Streamlit frontend
- [x] Write comprehensive documentation
- [ ] Deploy Streamlit to Cloud
- [ ] Record tutorial video
- [ ] Add analytics tracking
- [ ] Support multiple document types
- [ ] Add conversation history
- [ ] Multi-language support

---

## 🤝 **Contributing**

This is a personal portfolio project, but I'm open to:
- Bug reports
- Feature suggestions
- Documentation improvements

Feel free to open an issue or submit a PR!

---

## 📄 **License**

MIT License - Feel free to use this as inspiration for your own AI resume!

---

## 👤 **About Mike Murphy**

AI Educator & Technical Content Creator

- 🎥 [YouTube: AI Tutorials](https://youtube.com/@mikemurphyco)
- 💼 [LinkedIn](https://linkedin.com/in/mikemurphyco)
- 🌐 [Website](https://mikemurphy.co)
- 📧 Email: mike@mikemurphy.co

---

## 🌟 **Acknowledgments**

Built with:
- [n8n](https://n8n.io) - Workflow automation
- [Ollama](https://ollama.ai) - Self-hosted LLMs
- [Neon](https://neon.tech) - Serverless Postgres
- [Streamlit](https://streamlit.io) - Frontend framework
- [Claude Code](https://claude.ai/code) - Development assistant

---

**⭐ If this helped you, give it a star! ⭐**

**💼 Interested in hiring me? [Chat with my AI resume](https://cv-rag.streamlit.app)** _(coming soon)_
