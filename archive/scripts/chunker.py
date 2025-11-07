"""
⚠️ DEPRECATED - This script is no longer used in the n8n-native approach.

CV-RAG Document Chunker
========================
This script reads resume and supplemental documents, splits them into
semantically meaningful chunks, and saves them for embedding.

DEPRECATION NOTICE:
-------------------
This functionality is now handled by the n8n "Recursive Text Splitter" node
in workflow-1-document-ingestion.json.

This file is kept for reference only.

For the current implementation, see: n8n/README.md

Author: Mike Murphy
Project: CV-RAG
"""

import os
import json
from pathlib import Path
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_document(file_path: str) -> str:
    """
    Load a markdown document from the docs/ folder.

    Args:
        file_path: Path to the markdown file

    Returns:
        Document content as string
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content


def chunk_document(content: str, source: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[Dict]:
    """
    Split document into chunks using recursive character splitting.

    This approach splits on paragraph breaks first, then sentences, then words.
    It preserves semantic meaning better than arbitrary splitting.

    Args:
        content: The document text to chunk
        source: Document identifier (e.g., 'resume', 'supplemental')
        chunk_size: Target size for each chunk in characters
        chunk_overlap: Number of characters to overlap between chunks

    Returns:
        List of dictionaries with chunk content and metadata
    """
    # Initialize the text splitter
    # Separators: Try paragraphs first, then newlines, then sentences, then words
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    # Split the text
    chunks = text_splitter.split_text(content)

    # Add metadata to each chunk
    chunk_data = []
    for i, chunk in enumerate(chunks):
        chunk_data.append({
            "chunk_id": f"{source}_{i}",
            "content": chunk.strip(),
            "source": source,
            "chunk_index": i,
            "total_chunks": len(chunks)
        })

    return chunk_data


def main():
    """
    Main function to chunk CV documents.
    """
    # Set up paths
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / "docs"
    output_dir = project_root / "data"

    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)

    # Documents to process
    documents = {
        "resume": docs_dir / "cv_mike-murphy.md",
        "supplemental": docs_dir / "supplemental.md"
    }

    all_chunks = []

    print("=" * 60)
    print("CV-RAG Document Chunker")
    print("=" * 60)

    # Process each document
    for source, file_path in documents.items():
        print(f"\nProcessing: {source}")
        print(f"File: {file_path}")

        if not file_path.exists():
            print(f"  �  File not found: {file_path}")
            continue

        # Load document
        content = load_document(file_path)
        print(f"   Loaded {len(content)} characters")

        # Chunk document
        chunks = chunk_document(content, source)
        print(f"   Created {len(chunks)} chunks")

        # Add to all chunks
        all_chunks.extend(chunks)

        # Print first chunk as example
        if chunks:
            print(f"\n  Example chunk:")
            print(f"  {'-' * 56}")
            print(f"  {chunks[0]['content'][:200]}...")
            print(f"  {'-' * 56}")

    # Save chunks to JSON
    output_file = output_dir / "chunks.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f" Success! Created {len(all_chunks)} total chunks")
    print(f"=� Saved to: {output_file}")
    print(f"{'=' * 60}\n")

    # Print statistics
    print("Chunk Statistics:")
    print(f"  Resume chunks: {sum(1 for c in all_chunks if c['source'] == 'resume')}")
    print(f"  Supplemental chunks: {sum(1 for c in all_chunks if c['source'] == 'supplemental')}")
    print(f"  Average chunk size: {sum(len(c['content']) for c in all_chunks) // len(all_chunks)} characters")
    print()


if __name__ == "__main__":
    main()
