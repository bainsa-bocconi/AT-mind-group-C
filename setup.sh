#!/bin/bash

# setup.sh - Run this once on the server

echo "Installing dependencies..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "Setup complete!"
echo ""
echo "Now run: source start.sh"
