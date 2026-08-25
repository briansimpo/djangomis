#!/usr/bin/env bash

source "$(dirname "$0")/../libs/helper.sh"

cd "$APP_DIR"

activate_venv

watchmedo auto-restart --directory=./ --pattern="*.py" --recursive -- celery -A config.celery_app worker -l info