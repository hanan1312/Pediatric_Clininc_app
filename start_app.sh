#!/bin/bash
echo "Starting Pediatric Doctor Management System..."
echo "Please wait while the application loads..."

# Navigate to the application directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Start the application
echo "Application starting at http://localhost:8000"
echo "Press Ctrl+C to stop the application"
python src/main.py
