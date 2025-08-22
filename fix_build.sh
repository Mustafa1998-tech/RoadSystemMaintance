#!/bin/bash
set -e

echo "🚀 Starting Road Maintenance System Setup..."

# 1️⃣ Update debug-toolbar version in pyproject.toml
if grep -q 'debug-toolbar' pyproject.toml; then
    echo "🔧 Updating debug-toolbar version to ^6.0.0..."
    sed -i 's/debug-toolbar = .*/debug-toolbar = "^6.0.0"/' pyproject.toml
fi

# 2️⃣ Remove old lock file
echo "🗑 Removing old poetry.lock..."
rm -f poetry.lock

# 3️⃣ Install/update Poetry
echo "⬆️  Installing/updating Poetry..."
python -m pip install --upgrade pip
pip install --upgrade "poetry>=1.8.2,<1.9"

# 4️⃣ Generate new lock file
echo "📦 Generating poetry.lock..."
poetry lock

# 5️⃣ Install dependencies
echo "📥 Installing dependencies..."
poetry install --no-interaction --no-ansi --no-root --only main

# 6️⃣ Build Docker containers
echo "🐳 Building Docker containers..."
docker-compose build --no-cache

echo "✅ Setup completed successfully!"
echo "▶️ To start the application, run: docker-compose up"