#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

# Load shared helper library
source "$(dirname "$0")/../libs/helper.sh"

# Move to project root
cd "$APP_DIR"

# Ensure virtual environment is active
activate_venv

# Set environment variables
export PYTHONPATH="$APP_DIR"
export DJANGO_SETTINGS_MODULE="config.settings.production"

echo "Starting WebSocket server..."

# Start Uvicorn ASGI server
exec uvicorn config.asgi:application \
    --host 0.0.0.0 \
    --port 8001 \
    --workers 1
