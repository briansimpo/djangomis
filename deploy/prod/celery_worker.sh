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

# Start Celery Workers
echo "Starting Celery Workers..."

exec celery -A config.celery_app worker --concurrency=4 --loglevel=info
