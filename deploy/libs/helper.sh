#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

############################################
# Determine location of this library file
############################################

LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

############################################
# Detect Django project root (manage.py)
############################################

detect_app_dir() {

    local dir="$LIB_DIR"

    while [[ "$dir" != "/" ]]; do
        if [[ -f "$dir/manage.py" ]]; then
            echo "$dir"
            return
        fi
        dir="$(dirname "$dir")"
    done

    echo "Error: manage.py not found." >&2
    exit 1
}

APP_DIR="$(detect_app_dir)"
APP_NAME="$(basename "$APP_DIR")"

############################################
# Common variables
############################################

VENV_DIR="$APP_DIR/venv"


############################################
# Activate virtual environment
############################################

activate_venv() {

    if [[ ! -d "$VENV_DIR" ]]; then
        echo "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
    fi

    if [[ -z "${VIRTUAL_ENV:-}" ]]; then
        echo "Activating virtual environment..."
        source "$VENV_DIR/bin/activate"
    fi
}

############################################
# Django helper
############################################

django() {

    if [[ -z "${APP_DIR:-}" ]]; then
        echo "Error: APP_DIR is not set." >&2
        return 1
    fi

    ( cd "$APP_DIR" && python manage.py "$@" )
}