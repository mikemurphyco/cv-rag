"""
CV-RAG Embedder & Database Storage
===================================
This script generates vector embeddings for document chunks and stores them
in Neon Postgres with pgvector extension.

Author: Mike Murphy
Project: CV-RAG
"""

import os
import json
from pathlib import Path
from typing import List, Dict
import psycopg2
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv


def load_chunks(chunks_file: str) -> List[Dict]:
    """
    Load chunks from JSON file created by chunker.py

    Args:
        chunks_file: Path to chunks.json

    Returns:
        List of chunk dictionaries
    """
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    return chunks


def generate_embeddings(chunks: List[Dict], model_name: str = "all-MiniLM-L6-v2") -> List[Dict]:
    """
    Generate vector embeddings for each chunk using sentence-transformers.

    Args:
        chunks: List of chunk dictionaries with 'content' field
        model_name: Name of the sentence-transformers model to use

    Returns:
        Chunks with added 'embedding' field (list of floats)
    """
    print(f"\nLoading embedding model: {model_name}")
    model = SentenceTransformer(model_name)

    print(f"Generating embeddings for {len(chunks)} chunks...")

    # Extract just the content for embedding
    texts = [chunk['content'] for chunk in chunks]

    # Generate embeddings in batch (more efficient)
    embeddings = model.encode(texts, show_progress_bar=True)

    # Add embeddings to chunks
    for i, chunk in enumerate(chunks):
        chunk['embedding'] = embeddings[i].tolist()

    print(f"Generated {len(embeddings)} embeddings")
    print(f"Embedding dimension: {len(embeddings[0])}")

    return chunks


def create_database_schema(conn):
    """
    Create the cv_chunks table with pgvector extension.

    Args:
        conn: psycopg2 connection object
    """
    cursor = conn.cursor()

    print("\nSetting up database schema...")

    # Enable pgvector extension
    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    print("  Enabled pgvector extension")

    # Drop table if exists (for development - remove in production!)
    cursor.execute("DROP TABLE IF EXISTS cv_chunks;")

    # Create table
    # Note: VECTOR(384) matches all-MiniLM-L6-v2 embedding dimension
    cursor.execute("""
        CREATE TABLE cv_chunks (
            id SERIAL PRIMARY KEY,
            chunk_id VARCHAR(100) UNIQUE NOT NULL,
            content TEXT NOT NULL,
            source VARCHAR(50) NOT NULL,
            chunk_index INTEGER,
            total_chunks INTEGER,
            embedding VECTOR(384),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("  Created cv_chunks table")

    # Create index for vector similarity search
    cursor.execute("""
        CREATE INDEX ON cv_chunks USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 10);
    """)
    print("  Created vector similarity index")

    conn.commit()
    cursor.close()


def store_embeddings(chunks: List[Dict], connection_string: str):
    """
    Store chunks and their embeddings in Neon Postgres.

    Args:
        chunks: List of chunks with embeddings
        connection_string: PostgreSQL connection string
    """
    print(f"\nConnecting to database...")

    # Connect to database
    conn = psycopg2.connect(connection_string)
    print("  Connected to Neon Postgres")

    # Create schema
    create_database_schema(conn)

    # Insert chunks
    cursor = conn.cursor()
    print(f"\nInserting {len(chunks)} chunks into database...")

    for i, chunk in enumerate(chunks):
        cursor.execute("""
            INSERT INTO cv_chunks (chunk_id, content, source, chunk_index, total_chunks, embedding)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            chunk['chunk_id'],
            chunk['content'],
            chunk['source'],
            chunk['chunk_index'],
            chunk['total_chunks'],
            chunk['embedding']
        ))

        if (i + 1) % 10 == 0:
            print(f"  Inserted {i + 1}/{len(chunks)} chunks")

    conn.commit()
    print(f"  All chunks inserted successfully!")

    # Verify data
    cursor.execute("SELECT COUNT(*) FROM cv_chunks;")
    count = cursor.fetchone()[0]
    print(f"\nDatabase contains {count} chunks")

    cursor.close()
    conn.close()
    print("  Database connection closed")


def main():
    """
    Main function to generate embeddings and store in database.
    """
    # Load environment variables
    load_dotenv()

    print("=" * 60)
    print("CV-RAG Embedder & Database Storage")
    print("=" * 60)

    # Get configuration from environment
    connection_string = os.getenv("NEON_CONNECTION_STRING")
    if not connection_string:
        print("\nError: NEON_CONNECTION_STRING not found in .env file")
        print("Please copy .env.example to .env and add your connection string")
        return

    embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # Set up paths
    project_root = Path(__file__).parent.parent
    chunks_file = project_root / "data" / "chunks.json"

    if not chunks_file.exists():
        print(f"\nError: chunks.json not found at {chunks_file}")
        print("Please run chunker.py first to create chunks")
        return

    # Load chunks
    print(f"\nLoading chunks from {chunks_file}")
    chunks = load_chunks(chunks_file)
    print(f"  Loaded {len(chunks)} chunks")

    # Generate embeddings
    chunks_with_embeddings = generate_embeddings(chunks, embedding_model)

    # Store in database
    store_embeddings(chunks_with_embeddings, connection_string)

    print("\n" + "=" * 60)
    print("Embedding pipeline complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Set up n8n workflow for queries")
    print("  2. Build Streamlit frontend")
    print("  3. Test the full RAG pipeline")
    print()


if __name__ == "__main__":
    main()
