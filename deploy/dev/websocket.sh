#!/usr/bin/env bash

source "$(dirname "$0")/../libs/helper.sh"

cd "$APP_DIR"

activate_venv

uvicorn config.asgi:application --host 0.0.0.0 --port 8001