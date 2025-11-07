"""
⚠️ DEPRECATED - This service is no longer used in the n8n-native approach.

Embedding Service for CV-RAG
============================

Flask HTTP server that generates 384-dimensional embeddings using
the sentence-transformers 'all-MiniLM-L6-v2' model.

DEPRECATION NOTICE:
-------------------
This Flask service is no longer needed. The n8n-native approach uses:
- Ollama's nomic-embed-text model (768-dim embeddings)
- n8n "Embeddings Ollama" node (calls Ollama API directly)

No separate embedding service required!

This file is kept for reference only.

For the current implementation, see: n8n/README.md

This service was called by the n8n workflow to convert user queries
into vector embeddings for semantic search.

Usage:
    python scripts/embedding_service.py

The service will start on http://localhost:8000

Endpoint:
    POST /embed
    Body: {"text": "your query here"}
    Response: {"embedding": [...], "dimension": 384, "model": "all-MiniLM-L6-v2"}

Example:
    curl -X POST http://localhost:8000/embed \
      -H "Content-Type: application/json" \
      -d '{"text": "What programming languages does Mike know?"}'
"""

from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load the embedding model (happens once at startup)
logger.info("Loading sentence-transformers model: all-MiniLM-L6-v2")
model = SentenceTransformer('all-MiniLM-L6-v2')
logger.info("Model loaded successfully. Embedding dimension: 384")


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model': 'all-MiniLM-L6-v2',
        'dimension': 384
    }), 200


@app.route('/embed', methods=['POST'])
def embed():
    """
    Generate embedding for input text

    Expected JSON body:
    {
        "text": "your text here"
    }

    Returns:
    {
        "embedding": [0.123, -0.456, ...],
        "dimension": 384,
        "model": "all-MiniLM-L6-v2"
    }
    """
    try:
        data = request.json

        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400

        text = data.get('text', '')

        if not text:
            return jsonify({'error': 'No text provided in request body'}), 400

        if not isinstance(text, str):
            return jsonify({'error': 'Text must be a string'}), 400

        logger.info(f"Generating embedding for text: {text[:100]}...")

        # Generate embedding
        embedding = model.encode(text)

        # Convert numpy array to list for JSON serialization
        embedding_list = embedding.tolist()

        logger.info(f"Embedding generated successfully. Dimension: {len(embedding_list)}")

        return jsonify({
            'embedding': embedding_list,
            'dimension': len(embedding_list),
            'model': 'all-MiniLM-L6-v2'
        }), 200

    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}", exc_info=True)
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with usage instructions"""
    return jsonify({
        'service': 'CV-RAG Embedding Service',
        'model': 'all-MiniLM-L6-v2',
        'dimension': 384,
        'endpoints': {
            'health': 'GET /health - Health check',
            'embed': 'POST /embed - Generate embedding from text'
        },
        'example': {
            'url': 'http://localhost:8000/embed',
            'method': 'POST',
            'body': {
                'text': 'What programming languages does Mike know?'
            }
        }
    }), 200


if __name__ == '__main__':
    logger.info("Starting CV-RAG Embedding Service on http://0.0.0.0:8000")
    app.run(host='0.0.0.0', port=8000, debug=False)
