#!/bin/bash

# Smart Research Hub - Local Development Setup (without Docker)

echo "==================================="
echo "Smart Research Hub - Local Setup"
echo "==================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
cd backend
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your database credentials"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads logs models

echo ""
echo "==================================="
echo "✅ Setup complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Start PostgreSQL and Redis (using Docker or native):"
echo "   docker-compose up -d db redis"
echo ""
echo "2. Edit backend/.env with your configuration"
echo ""
echo "3. Run the development server:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload"
echo ""
echo "4. Access the API at http://localhost:8000"
echo "==================================="
