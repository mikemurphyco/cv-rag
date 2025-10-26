-- CV-RAG Database Schema for Neon Postgres
-- Author: Mike Murphy
-- Project: CV-RAG
--
-- Instructions:
-- 1. Log into your Neon console: https://console.neon.tech/
-- 2. Select your project and database
-- 3. Open the SQL Editor
-- 4. Copy and paste this entire file
-- 5. Execute the commands

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop existing table if you're resetting (CAUTION: This deletes all data!)
-- Uncomment the line below only if you want to start fresh
-- DROP TABLE IF EXISTS cv_chunks;

-- Create the main table for storing resume chunks and embeddings
CREATE TABLE IF NOT EXISTS cv_chunks (
    id SERIAL PRIMARY KEY,
    chunk_id VARCHAR(100) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    source VARCHAR(50) NOT NULL,
    chunk_index INTEGER,
    total_chunks INTEGER,
    embedding VECTOR(384),  -- Matches all-MiniLM-L6-v2 embedding dimension
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for fast vector similarity search using cosine distance
-- ivfflat is an approximate nearest neighbor (ANN) algorithm
-- lists = 10 is good for small datasets (< 100k rows)
CREATE INDEX IF NOT EXISTS cv_chunks_embedding_idx
ON cv_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 10);

-- Optional: Create index on source for faster filtering
CREATE INDEX IF NOT EXISTS cv_chunks_source_idx
ON cv_chunks(source);

-- Verify the setup
SELECT
    'pgvector extension enabled' AS status
WHERE EXISTS (
    SELECT 1 FROM pg_extension WHERE extname = 'vector'
);

SELECT
    'cv_chunks table created' AS status,
    COUNT(*) AS row_count
FROM cv_chunks;

-- Example query for vector similarity search
-- (This won't work until you have data, but shows the pattern)
/*
SELECT
    chunk_id,
    content,
    source,
    1 - (embedding <=> '[0.1, 0.2, ...]'::vector) AS similarity
FROM cv_chunks
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 3;
*/
