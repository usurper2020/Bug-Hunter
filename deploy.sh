#!/bin/bash

echo "Starting deployment..."

# Pull the latest changes
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Restart the application (example for a Flask app)
pkill -f "python app/main.py"
nohup python app/main.py &

echo "Deployment completed."