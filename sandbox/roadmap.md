## Roadmap / To-Do List

Follow this phased approach to build incrementally. Aim for small wins—test each step before moving on. Estimated time: 1-2 days if building on your existing VPS and Python setup.

### Phase 1: Project Setup (30-60 minutes)

1. Create the folder structure above in your CV-RAG directory.
2. Initialize Git: Run git init in the root, add a .gitignore (exclude venv/, .env, etc.), commit initial files.
3. Set up a virtual environment: python -m venv venv, activate it, and create requirements.txt with basics like pip install langchain sentence-transformers psycopg2-binary requests streamlit.
4. Create a .env file for secrets (e.g., Neon Postgres connection string, Ollama API URL). Don't commit it!
5. Push to GitHub: Create a new repo called mike-murphy-cv-rag, add remote, and push.

### Phase 2: Data Preparation (1-2 hours)

1. Flesh out Supplemental.md: Add sections like:
    - **About Mike**: A short bio highlighting your hospitality background, tech support role, and AI journey.
    - **YouTube Tutorials**: List titles, links, and brief descriptions (e.g., "Setting up Postgres with pgvector: [link] - Covers database setup for RAG systems").
    - **Courses & Projects**: Bullet points of recent work, like your 12-week Python plan, RAG experiments, VPS hosting tips.
    - **Skills Highlights**: Extra stories, e.g., "Solved 99% of podcast host tickets under 10 minutes using patient problem-solving." Keep it concise—aim for 1-2 pages of text. Use Markdown for formatting.
2. Write a simple Python script (scripts/chunker.py) to read docs and split into chunks:
    - Use langchain.text_splitter or manual splitting (e.g., by paragraphs, 200-500 words per chunk).
    - Output: Save chunks as a JSON file or list for embedding.
3. Test chunking: Run the script on Resume.md and Supplemental.md, print a few chunks to verify.

### Phase 3: RAG Implementation (2-4 hours)

1. Set up Neon Postgres: If not already, create a free database, enable pgvector extension via SQL: CREATE EXTENSION vector;. Create a table like CREATE TABLE documents (id SERIAL PRIMARY KEY, content TEXT, embedding VECTOR(384)); (adjust dimension for your embedder).
2. Embed chunks: In scripts/embedder.py, use sentence-transformers to generate embeddings, then insert into Postgres via psycopg2.
    - Example flow: Load chunks → Embed → Connect to Neon → Insert.
3. Install and run Ollama on VPS: Pull a model like llama3:8b via Docker: docker run -d -p 11434:11434 --name ollama ollama/ollama. Test API: curl http://your-vps-ip:11434/api/generate -d '{"model": "llama3", "prompt": "Hello"}'.
4. Build n8n workflow: Create a flow in n8n on your VPS.
    - Trigger: Webhook for queries.
    - Steps: Receive query → Vector search in Postgres (use n8n's Postgres node or HTTP to query embeddings via cosine similarity) → Retrieve top chunks → Send to Ollama for generation (prompt: "Answer based on this context: [chunks] Question: [query]") → Return response.
5. Test query script: In scripts/query.py, simulate a query via n8n webhook, print response.

### Phase 4: Frontend & Interaction (1-2 hours)

1. Build Streamlit app (streamlit/app.py):
    - Simple chat interface: Use st.text_input for queries, POST to n8n webhook, display response.
    - Add meta touches: Buttons for sample questions like "What are Mike's AI skills?" or "Tell me about his tech support experience."
    - Include links: Footer with "Download PDF Resume" and GitHub repo.
2. Run locally: streamlit run app.py and test queries.
3. Deploy: Push to Streamlit Cloud (free tier), or host on VPS with a reverse proxy.

### Phase 5: Polish & Deployment (1 hour)

1. Update README: Add screenshots of the app, n8n flow, and a live demo link.
2. Add error handling: In scripts and n8n, handle empty results or failed embeddings.
3. Test end-to-end: Query something like "Why is Mike great for AI education?"—ensure it pulls from both docs.
4. Share: Link the GitHub repo in job apps, with a note: "Chat with my resume here: [Streamlit URL]".