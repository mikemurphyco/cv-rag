#!/usr/bin/env python3
"""
Clean the cv_chunks table in Neon database.
This will DELETE ALL chunks so we can re-ingest cleanly.
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def clean_database():
    """Delete all records from cv_chunks table."""

    # Get connection string
    conn_string = os.getenv('NEON_CONNECTION_STRING')

    if not conn_string:
        print("❌ Error: NEON_CONNECTION_STRING not found in .env")
        return False

    try:
        # Connect to database
        print("🔌 Connecting to Neon database...")
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        # Count existing chunks
        cursor.execute("SELECT COUNT(*) FROM cv_chunks")
        count_before = cursor.fetchone()[0]
        print(f"📊 Current chunks in database: {count_before}")

        # Delete all chunks
        print("🗑️  Deleting all chunks...")
        cursor.execute("DELETE FROM cv_chunks")
        conn.commit()

        # Verify deletion
        cursor.execute("SELECT COUNT(*) FROM cv_chunks")
        count_after = cursor.fetchone()[0]
        print(f"✅ Chunks remaining: {count_after}")

        # Close connection
        cursor.close()
        conn.close()

        print(f"\n✨ Successfully deleted {count_before} chunks!")
        print("👉 Now run Workflow 1 in n8n to re-ingest your resume.")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("  CV-RAG Database Cleanup")
    print("=" * 50)
    print()

    clean_database()
