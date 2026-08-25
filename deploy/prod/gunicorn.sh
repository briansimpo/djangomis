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

# Start Gunicorn with default synchronous worker
echo "Starting Gunicorn..."

exec gunicorn config.wsgi:application \
    --bind 127.0.0.1:8000 \
    --chdir "$APP_DIR" \
    --timeout 300 \
    --workers 4 \
    --log-level info \
    --access-logfile - \
    --error-logfile -
