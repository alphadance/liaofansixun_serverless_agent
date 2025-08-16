#!/bin/bash
# Build deployment package for Alibaba Cloud Function Compute

echo "Building Function Compute deployment package..."

# Clean up previous builds
rm -rf fc_build fc_deploy.zip

# Create build directory
mkdir -p fc_build

# Copy handler file
cp fc_index.py fc_build/index.py

# Copy requirements
cp requirements.txt fc_build/

# Install dependencies to the build directory
cd fc_build
pip3 install --platform manylinux2014_x86_64 --only-binary=:all: -r requirements.txt -t .

# Create deployment zip
zip -r ../fc_deploy.zip .

cd ..
rm -rf fc_build

echo "Deployment package created: fc_deploy.zip"
echo "Size: $(du -h fc_deploy.zip | cut -f1)"
echo ""
echo "Next steps:"
echo "1. Log in to Alibaba Cloud Function Compute console"
echo "2. Create a new function or update existing one"
echo "3. Upload fc_deploy.zip as the function code"
echo "4. Set handler to: index.handler"
echo "5. Configure environment variables:"
echo "   - DASHSCOPE_API_KEY"
echo "   - BAILIAN_AGENT_ID"