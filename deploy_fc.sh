#!/bin/bash
# Deploy to Alibaba Cloud Function Compute

echo "=== Alibaba Cloud Function Compute Deployment ==="

# Check environment variables
if [ -z "$DASHSCOPE_API_KEY" ]; then
    echo "Error: DASHSCOPE_API_KEY not set"
    echo "Run: export DASHSCOPE_API_KEY=your-api-key"
    exit 1
fi

if [ -z "$BAILIAN_AGENT_ID" ]; then
    echo "Error: BAILIAN_AGENT_ID not set"
    echo "Run: export BAILIAN_AGENT_ID=your-agent-id"
    exit 1
fi

# Build and deploy
./build_fc.sh && s deploy