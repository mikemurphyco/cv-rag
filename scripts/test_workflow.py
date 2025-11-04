"""
n8n Workflow Test Script
========================

Tests the complete CV-RAG pipeline by sending queries to the n8n webhook
and validating responses.

Usage:
    python scripts/test_workflow.py

This script will:
1. Test the embedding service is running
2. Send sample queries to the n8n webhook
3. Validate response structure and content
4. Report success/failure for each component

Prerequisites:
- Embedding service running (python scripts/embedding_service.py)
- n8n workflow active at flow.imurph.com
- Database populated with embeddings
- Ollama running on VPS
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv
from typing import Dict, Any, List

# Load environment variables
load_dotenv()

# Configuration
EMBEDDING_SERVICE_URL = "http://localhost:8000"
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

# ANSI color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

# Test queries
TEST_QUERIES = [
    "What programming languages does Mike know?",
    "Tell me about Mike's AI and machine learning experience",
    "What YouTube tutorials has Mike created?",
    "What is Mike's educational background?",
    "Describe Mike's experience with data visualization"
]


def print_status(message: str, status: str = "info"):
    """Print colored status messages"""
    colors = {
        "success": GREEN,
        "error": RED,
        "warning": YELLOW,
        "info": BLUE
    }
    color = colors.get(status, RESET)
    print(f"{color}{message}{RESET}")


def test_embedding_service() -> bool:
    """Test that the embedding service is running and responsive"""
    print_status("\n=== Testing Embedding Service ===", "info")

    try:
        # Test health endpoint
        response = requests.get(f"{EMBEDDING_SERVICE_URL}/health", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print_status(f"✓ Embedding service is healthy", "success")
            print_status(f"  Model: {data.get('model')}", "info")
            print_status(f"  Dimension: {data.get('dimension')}", "info")
        else:
            print_status(f"✗ Embedding service returned status {response.status_code}", "error")
            return False

        # Test embedding generation
        test_response = requests.post(
            f"{EMBEDDING_SERVICE_URL}/embed",
            json={"text": "test query"},
            timeout=10
        )

        if test_response.status_code == 200:
            embedding_data = test_response.json()
            if len(embedding_data.get('embedding', [])) == 384:
                print_status(f"✓ Embedding generation working (384 dimensions)", "success")
                return True
            else:
                print_status(f"✗ Invalid embedding dimension: {len(embedding_data.get('embedding', []))}", "error")
                return False
        else:
            print_status(f"✗ Embedding generation failed: {test_response.status_code}", "error")
            return False

    except requests.exceptions.ConnectionError:
        print_status("✗ Cannot connect to embedding service", "error")
        print_status("  Run: python scripts/embedding_service.py", "warning")
        return False
    except Exception as e:
        print_status(f"✗ Embedding service test failed: {str(e)}", "error")
        return False


def test_n8n_webhook(query: str) -> Dict[str, Any]:
    """Test the n8n workflow with a single query"""

    if not N8N_WEBHOOK_URL:
        print_status("✗ N8N_WEBHOOK_URL not set in .env", "error")
        return None

    try:
        response = requests.post(
            N8N_WEBHOOK_URL,
            json={"query": query},
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            print_status(f"✗ Webhook returned status {response.status_code}", "error")
            print_status(f"  Response: {response.text}", "error")
            return None

    except requests.exceptions.Timeout:
        print_status("✗ Request timed out (>30s)", "error")
        print_status("  Check if Ollama is running and responsive", "warning")
        return None
    except requests.exceptions.ConnectionError:
        print_status("✗ Cannot connect to n8n webhook", "error")
        print_status(f"  URL: {N8N_WEBHOOK_URL}", "warning")
        return None
    except Exception as e:
        print_status(f"✗ Webhook test failed: {str(e)}", "error")
        return None


def validate_response(response: Dict[str, Any], query: str) -> bool:
    """Validate the structure and content of the n8n response"""

    required_fields = ["answer", "query", "chunks_used", "model", "timestamp"]

    # Check all required fields are present
    for field in required_fields:
        if field not in response:
            print_status(f"✗ Missing required field: {field}", "error")
            return False

    # Validate field types and values
    if not isinstance(response["answer"], str) or len(response["answer"]) == 0:
        print_status("✗ Answer is empty or not a string", "error")
        return False

    if response["query"] != query:
        print_status(f"✗ Query mismatch: expected '{query}', got '{response['query']}'", "error")
        return False

    if not isinstance(response["chunks_used"], int) or response["chunks_used"] < 1:
        print_status(f"✗ Invalid chunks_used: {response['chunks_used']}", "error")
        return False

    if response["model"] != "llama3.2:latest":
        print_status(f"⚠ Unexpected model: {response['model']}", "warning")

    return True


def run_workflow_tests():
    """Run all workflow tests"""
    print_status("\n=== Testing n8n RAG Workflow ===", "info")

    if not N8N_WEBHOOK_URL:
        print_status("✗ N8N_WEBHOOK_URL not configured in .env", "error")
        print_status("  Add: N8N_WEBHOOK_URL=https://flow.imurph.com/webhook/cv-rag-query", "warning")
        return False

    print_status(f"Webhook URL: {N8N_WEBHOOK_URL}", "info")

    passed = 0
    failed = 0

    for idx, query in enumerate(TEST_QUERIES, 1):
        print_status(f"\n--- Test Query {idx}/{len(TEST_QUERIES)} ---", "info")
        print_status(f"Query: {query}", "info")

        response = test_n8n_webhook(query)

        if response is None:
            failed += 1
            continue

        if validate_response(response, query):
            print_status(f"✓ Query successful", "success")
            print_status(f"  Chunks used: {response['chunks_used']}", "info")
            print_status(f"  Answer preview: {response['answer'][:150]}...", "info")
            passed += 1
        else:
            print_status(f"✗ Response validation failed", "error")
            failed += 1

    # Print summary
    print_status(f"\n=== Test Summary ===", "info")
    print_status(f"Passed: {passed}/{len(TEST_QUERIES)}", "success" if passed == len(TEST_QUERIES) else "warning")
    print_status(f"Failed: {failed}/{len(TEST_QUERIES)}", "error" if failed > 0 else "info")

    return failed == 0


def main():
    """Main test runner"""
    print_status("=" * 60, "info")
    print_status("CV-RAG Workflow Test Suite", "info")
    print_status("=" * 60, "info")

    # Step 1: Test embedding service
    embedding_ok = test_embedding_service()

    if not embedding_ok:
        print_status("\n✗ Embedding service test failed. Fix this before proceeding.", "error")
        sys.exit(1)

    # Step 2: Test n8n workflow
    workflow_ok = run_workflow_tests()

    # Final result
    print_status("\n" + "=" * 60, "info")
    if embedding_ok and workflow_ok:
        print_status("✓ All tests passed! Your RAG pipeline is working.", "success")
        sys.exit(0)
    else:
        print_status("✗ Some tests failed. Review the errors above.", "error")
        sys.exit(1)


if __name__ == "__main__":
    main()
