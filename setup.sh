#!/bin/bash

# Update package list
echo "Updating package list..."
sudo apt-get update

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    libpq-dev \
    sqlite3

# Create data directory
echo "Creating data directory..."
mkdir -p data

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Initialize database
echo "Initializing database..."
python -m app.init_db

# Set up environment variables
echo "Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from template"
fi

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

echo "Setup complete! Activate virtual environment with: source venv/bin/activate"
