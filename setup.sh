#!/bin/bash
# Setup script for virtual environment and dependencies

echo "Setting up virtual environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

echo "Setup complete!"
echo ""
echo "To start the server:"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "Or use the start script:"
echo "  ./start.sh"