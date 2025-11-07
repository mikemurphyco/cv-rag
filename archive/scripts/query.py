"""
CV-RAG Query Tester
===================
This script tests the RAG pipeline by querying the database directly
or through the n8n webhook.

Author: Mike Murphy
Project: CV-RAG
"""

import os
from typing import List, Dict
import psycopg2
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import requests


def query_database_direct(query_text: str, connection_string: str, top_k: int = 3) -> List[Dict]:
    """
    Query the database directly without n8n (for testing).

    Args:
        query_text: The question to ask
        connection_string: PostgreSQL connection string
        top_k: Number of similar chunks to retrieve

    Returns:
        List of relevant chunks with similarity scores
    """
    print(f"\n= Query: '{query_text}'")
    print(f"{'=' * 60}")

    # Load embedding model
    print("=å Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Generate embedding for query
    print("= Generating query embedding...")
    query_embedding = model.encode(query_text).tolist()

    # Connect to database
    print("=¾ Connecting to database...")
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()

    # Perform vector similarity search
    print(f"= Searching for top {top_k} similar chunks...")
    cursor.execute("""
        SELECT
            chunk_id,
            content,
            source,
            1 - (embedding <=> %s::vector) AS similarity
        FROM cv_chunks
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
    """, (query_embedding, query_embedding, top_k))

    results = cursor.fetchall()

    # Format results
    chunks = []
    for row in results:
        chunks.append({
            'chunk_id': row[0],
            'content': row[1],
            'source': row[2],
            'similarity': float(row[3])
        })

    cursor.close()
    conn.close()

    return chunks


def query_via_n8n(query_text: str, webhook_url: str) -> Dict:
    """
    Query through the n8n workflow (full RAG pipeline).

    Args:
        query_text: The question to ask
        webhook_url: n8n webhook endpoint

    Returns:
        Response from n8n workflow including LLM-generated answer
    """
    print(f"\n= Query: '{query_text}'")
    print(f"{'=' * 60}")

    print("=á Sending request to n8n webhook...")
    response = requests.post(
        webhook_url,
        json={'query': query_text},
        timeout=30
    )

    if response.status_code == 200:
        return response.json()
    else:
        print(f"L Error: {response.status_code}")
        print(response.text)
        return None


def test_direct_query():
    """
    Test direct database queries (without LLM).
    """
    load_dotenv()

    connection_string = os.getenv("NEON_CONNECTION_STRING")
    if not connection_string:
        print("L Error: NEON_CONNECTION_STRING not found in .env file")
        return

    print("=" * 60)
    print("CV-RAG Direct Query Test (No LLM)")
    print("=" * 60)

    # Sample queries
    test_queries = [
        "What AI tutorials has Mike created?",
        "What is Mike's experience with tech support?",
        "Tell me about Mike's RAG system projects",
        "What skills does Mike have?"
    ]

    for query in test_queries:
        results = query_database_direct(query, connection_string, top_k=3)

        print(f"\n=Ê Found {len(results)} relevant chunks:\n")

        for i, chunk in enumerate(results, 1):
            print(f"{i}. Source: {chunk['source']} | Similarity: {chunk['similarity']:.3f}")
            print(f"   {'-' * 56}")
            print(f"   {chunk['content'][:200]}...")
            print(f"   {'-' * 56}\n")

        print("=" * 60)
        input("\nPress Enter to continue to next query...")


def test_n8n_query():
    """
    Test n8n webhook queries (full RAG with LLM).
    """
    load_dotenv()

    webhook_url = os.getenv("N8N_WEBHOOK_URL")
    if not webhook_url:
        print("L Error: N8N_WEBHOOK_URL not found in .env file")
        print("   Please set up your n8n workflow first")
        return

    print("=" * 60)
    print("CV-RAG n8n Query Test (Full RAG Pipeline)")
    print("=" * 60)

    # Sample queries
    test_queries = [
        "What AI tutorials has Mike created?",
        "Why is Mike great for tech support roles?",
        "Tell me about Mike's RAG system experience"
    ]

    for query in test_queries:
        response = query_via_n8n(query, webhook_url)

        if response:
            print(f"\n=Ý LLM Response:")
            print(f"   {'-' * 56}")
            print(f"   {response.get('answer', 'No answer found')}")
            print(f"   {'-' * 56}\n")

            if 'sources' in response:
                print(f"=Ú Sources used: {response['sources']}")

        print("=" * 60)
        input("\nPress Enter to continue to next query...")


def interactive_mode():
    """
    Interactive query mode.
    """
    load_dotenv()

    connection_string = os.getenv("NEON_CONNECTION_STRING")
    webhook_url = os.getenv("N8N_WEBHOOK_URL")

    print("=" * 60)
    print("CV-RAG Interactive Query Mode")
    print("=" * 60)

    mode = input("\nChoose mode:\n  1. Direct database query (no LLM)\n  2. Full n8n pipeline (with LLM)\n\nEnter 1 or 2: ")

    if mode == "1" and connection_string:
        print("\n=¡ Direct query mode - Returns similar chunks without LLM generation\n")
        while True:
            query = input("\nEnter your question (or 'quit' to exit): ")
            if query.lower() in ['quit', 'exit', 'q']:
                break

            results = query_database_direct(query, connection_string, top_k=3)
            print(f"\n=Ê Found {len(results)} relevant chunks:\n")

            for i, chunk in enumerate(results, 1):
                print(f"{i}. Similarity: {chunk['similarity']:.3f}")
                print(f"   {chunk['content']}\n")

    elif mode == "2" and webhook_url:
        print("\n=¡ Full RAG mode - Returns LLM-generated answers\n")
        while True:
            query = input("\nEnter your question (or 'quit' to exit): ")
            if query.lower() in ['quit', 'exit', 'q']:
                break

            response = query_via_n8n(query, webhook_url)
            if response:
                print(f"\n=Ý Answer: {response.get('answer', 'No answer found')}\n")
    else:
        print("L Configuration missing for selected mode")


def main():
    """
    Main function with menu for different test modes.
    """
    print("=" * 60)
    print("CV-RAG Query Tester")
    print("=" * 60)
    print("\nTest Options:")
    print("  1. Run automated direct query tests")
    print("  2. Run automated n8n query tests")
    print("  3. Interactive query mode")
    print("  4. Exit")

    choice = input("\nEnter your choice (1-4): ")

    if choice == "1":
        test_direct_query()
    elif choice == "2":
        test_n8n_query()
    elif choice == "3":
        interactive_mode()
    else:
        print("Exiting...")


if __name__ == "__main__":
    main()
