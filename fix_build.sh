#!/bin/bash
set -e

# 1️⃣ Update debug-toolbar in pyproject.toml if it exists
if [ -f "pyproject.toml" ] && grep -q 'debug-toolbar' pyproject.toml; then
    echo "Updating debug-toolbar version to 6.0.0..."
    sed -i 's/debug-toolbar = .*/debug-toolbar = "6.0.0"/' pyproject.toml
fi

# 2️⃣ Remove old lock file
echo "Removing old poetry.lock..."
rm -f poetry.lock

# 3️⃣ Install/Update Poetry
echo "Installing/updating Poetry..."
python -m pip install --upgrade pip
python -m pip install --upgrade "poetry>=1.8.2,<1.9"

# 4️⃣ Generate new lock file
echo "Generating new poetry.lock..."
poetry lock --no-update

# 5️⃣ Install dependencies locally
echo "Installing dependencies..."
poetry install --no-interaction --no-ansi --no-root --only main

# 6️⃣ Install dev dependencies
echo "Installing dev dependencies..."
poetry install --no-interaction --no-ansi --with dev

# 7️⃣ Build Docker containers without cache
echo "Building Docker containers..."
docker-compose build --no-cache

# 8️⃣ Start the containers
echo "Starting Docker containers..."
docker-compose up