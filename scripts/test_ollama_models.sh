#!/bin/bash
# Ollama Model Performance Tester
# Tests different models with warm-up to get accurate performance metrics

# Configuration
VPS_HOST="root@158.220.127.4"
TEST_PROMPT="What is Mike Murphy's education background? Be specific about degrees."

# ANSI color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Ollama Model Performance Test ===${NC}\n"

# Models to test (add/remove as needed)
MODELS=(
    "llama3.1:8b"
    "llama3.2:3b"
    "mistral:7b-instruct"
    "phi3:3.8b"
)

# Function to test a model
test_model() {
    local model=$1

    echo -e "${YELLOW}Testing: $model${NC}"

    # Check if model exists on VPS
    echo "  Checking if model is available..."
    ssh $VPS_HOST "ollama list | grep -q '$model'" 2>/dev/null

    if [ $? -ne 0 ]; then
        echo -e "  ${RED}❌ Model not found. Pulling...${NC}"
        ssh $VPS_HOST "ollama pull $model"
    else
        echo -e "  ${GREEN}✓ Model found${NC}"
    fi

    # Warm-up run (discard timing)
    echo "  Warming up model (loading into memory)..."
    ssh $VPS_HOST "ollama run $model 'Hello' >/dev/null 2>&1"

    # Actual timed test run
    echo "  Running timed test..."
    START_TIME=$(date +%s.%N)

    RESPONSE=$(ssh $VPS_HOST "ollama run $model '$TEST_PROMPT' 2>/dev/null")

    END_TIME=$(date +%s.%N)
    DURATION=$(echo "$END_TIME - $START_TIME" | bc)

    # Display results
    echo -e "  ${GREEN}✓ Complete${NC}"
    echo -e "  ${BLUE}Time: ${DURATION}s${NC}"
    echo -e "  ${BLUE}Response preview:${NC}"
    echo "$RESPONSE" | head -c 200
    echo -e "\n  ...\n"

    # Return duration for comparison
    echo "$model:$DURATION" >> /tmp/ollama_test_results.txt
}

# Clear previous results
rm -f /tmp/ollama_test_results.txt

# Test each model
for model in "${MODELS[@]}"; do
    test_model "$model"
    echo ""
done

# Display summary
echo -e "${BLUE}=== Summary ===${NC}\n"
echo -e "${YELLOW}Model Performance (seconds):${NC}"

sort -t: -k2 -n /tmp/ollama_test_results.txt | while IFS=: read -r model duration; do
    printf "  %-20s %s\n" "$model" "${GREEN}${duration}s${NC}"
done

echo -e "\n${YELLOW}Recommendation:${NC}"
FASTEST=$(sort -t: -k2 -n /tmp/ollama_test_results.txt | head -1 | cut -d: -f1)
echo -e "  Fastest model: ${GREEN}$FASTEST${NC}"

# Cleanup
rm -f /tmp/ollama_test_results.txt

echo -e "\n${BLUE}Test complete!${NC}"
