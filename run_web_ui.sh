#!/bin/bash
# Quick start script for the Web UI

echo ""
echo "========================================"
echo "Parallel Computing Web UI - Quick Start"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Start the Flask app
echo ""
echo "========================================"
echo "Starting Flask application..."
echo "========================================"
echo ""
echo "Open your browser and go to:"
echo "http://127.0.0.1:5000"
echo ""
python app/app.py
