# Next Steps - CV-RAG Completion

Great progress! Streamlit is deployed and accessible at `https://chat.imurph.com` 🎉

## What's Working
- ✅ Streamlit container deployed with Docker
- ✅ Traefik routing with automatic HTTPS
- ✅ DNS configured correctly
- ✅ App loads and displays properly
- ✅ Beautiful dark theme UI

## Issues to Fix

### 1. Emoji Display Issues
Some emojis are showing as corrupted characters (e.g., line 158: `"=�"`). Need to:
- Review all emoji usage in app.py
- Ensure UTF-8 encoding throughout
- Fix corrupted emoji on line 158 (View Sources expander)

### 2. No Answer Responses Yet
The app accepts questions but doesn't return answers. This is because:

**Required Setup:**
1. **Re-import Workflow 2** with webhook support
   - File: `n8n/workflow-2-query-pipeline.json`
   - Location: `https://flow.imurph.com`
   - Action: Import → Configure credentials → Activate

2. **Configure Postgres Credential in n8n**
   - Credential name: "Postgres account"
   - **IMPORTANT**: Do NOT paste the full connection string! Parse it manually:

   From this `.env` connection string:
   ```
   postgresql://neondb_owner:npg_2r6yhKmZEPfk@ep-holy-glitter-adq7h6qu-pooler.c-2.us-east-1.aws.neon.tech/mm_content_factory?sslmode=require
   ```

   Fill in n8n Postgres credential fields:
   - **Host**: `ep-holy-glitter-adq7h6qu-pooler.c-2.us-east-1.aws.neon.tech` (only the hostname part)
   - **Database**: `mm_content_factory`
   - **User**: `neondb_owner`
   - **Password**: `npg_2r6yhKmZEPfk`
   - **Port**: `5432` (default)
   - **SSL**: `require` (enable SSL/TLS)

   - Test connection to ensure it works

3. **Configure Ollama Credential in n8n**
   - Credential name: "Ollama account"
   - Base URL: `http://ollama:11434` (Docker internal)
   - Verify Ollama container is running

4. **Verify Database Has Data**
   - Check if resume chunks were ingested via Workflow 1
   - Query count: `SELECT COUNT(*) FROM cv_chunks;` in Neon console
   - If empty, run Workflow 1 to ingest documents

### 3. Test End-to-End Pipeline

Once Workflow 2 is configured and activated:

**Test via Streamlit:**
1. Visit `https://chat.imurph.com`
2. Click a sample question (e.g., "What AI tutorials has Mike created?")
3. Should see:
   - Spinner: "> Thinking..."
   - Success message: "Here's what I found:"
   - Answer text from LLM
   - Optional: Sources expander

**Test via Direct Webhook:**
```bash
curl -X POST https://flow.imurph.com/webhook/cv-rag-query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are Mike Murphy skills?"}'
```

Expected response:
```json
{
  "answer": "Based on Mike's resume, he has extensive experience with..."
}
```

## Quick Fixes Needed

### Fix Emoji on Line 158
```python
# Current (broken):
with st.expander("=� View Sources"):

# Should be:
with st.expander("📄 View Sources"):
```

### Verify Sample Question Buttons Work
Check that clicking sample questions populates the input field correctly.

## Deployment Checklist

- [x] Streamlit container running
- [x] DNS configured (`chat.imurph.com`)
- [x] HTTPS working (Traefik + Let's Encrypt)
- [ ] Workflow 2 imported with webhook
- [ ] Postgres credential configured
- [ ] Ollama credential configured
- [ ] Workflow 2 activated
- [ ] Database populated with resume chunks
- [ ] End-to-end test successful
- [ ] Fix emoji display issues
- [ ] Record demo video

## Files to Review Tomorrow

1. `streamlit/app.py` - Fix emoji characters
2. `n8n/workflow-2-query-pipeline.json` - Import this into n8n
3. Check Neon database for existing data

## Commands Reference

```bash
# On VPS - View Streamlit logs
cd /cv-rag
docker compose logs -f streamlit

# Restart Streamlit after code changes
docker compose restart streamlit

# Full rebuild after code changes
git pull && docker compose up -d --build

# Test webhook directly
curl -X POST https://flow.imurph.com/webhook/cv-rag-query \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'

# Check running containers
docker ps | grep -E "streamlit|ollama|n8n"
```

## Next Session Goals

1. Fix emoji display issues in app.py
2. Import and activate Workflow 2 in n8n
3. Verify database has resume data
4. Test complete RAG pipeline
5. Tweak UI/UX as needed
6. Record demo video

---

**Current Status:** Deployment infrastructure complete. Need to wire up the RAG backend (n8n workflows + database).

**Time Investment:** Infrastructure done. ~30 minutes to configure n8n workflows and test.
