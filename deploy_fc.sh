#!/bin/bash
# Quick deployment script for Alibaba Cloud Function Compute

echo "=== Alibaba Cloud Function Compute Deployment ==="
echo ""

# Check environment variables
if [ -z "$DASHSCOPE_API_KEY" ]; then
    echo "Error: DASHSCOPE_API_KEY environment variable not set"
    echo "Please run: export DASHSCOPE_API_KEY=your-api-key"
    exit 1
fi

if [ -z "$BAILIAN_AGENT_ID" ]; then
    echo "Error: BAILIAN_AGENT_ID environment variable not set"
    echo "Please run: export BAILIAN_AGENT_ID=your-agent-id"
    exit 1
fi

# Build deployment package
echo "Step 1: Building deployment package..."
./build_fc.sh

if [ ! -f "fc_deploy.zip" ]; then
    echo "Error: Failed to create deployment package"
    exit 1
fi

echo ""
echo "Step 2: Deployment Options"
echo ""
echo "Choose your deployment method:"
echo ""
echo "1. Serverless Devs (Recommended - requires 's' CLI)"
echo "   Run: s deploy"
echo ""
echo "2. Fun CLI (requires 'fun' CLI)"
echo "   Run: fun deploy -t fc_template.yml"
echo ""
echo "3. Manual Console Upload"
echo "   - Log in to: https://fc.console.aliyun.com"
echo "   - Upload: fc_deploy.zip"
echo "   - Handler: index.handler"
echo "   - Runtime: Python 3.9"
echo "   - Set environment variables in console"
echo ""
echo "Deployment package ready: fc_deploy.zip ($(du -h fc_deploy.zip | cut -f1))"
echo ""
echo "Environment variables configured:"
echo "  DASHSCOPE_API_KEY: ${DASHSCOPE_API_KEY:0:10}..."
echo "  BAILIAN_AGENT_ID: $BAILIAN_AGENT_ID"