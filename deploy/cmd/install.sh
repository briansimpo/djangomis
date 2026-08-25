#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

# ------------------------------
# Ensure root
# ------------------------------
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root."
    exit 1
fi

# ------------------------------
# Load helper
# ------------------------------
source "$(dirname "$0")/../libs/helper.sh"

# ------------------------------
# Core Paths
# ------------------------------
APP_DIR="$(detect_app_dir)"
APP_NAME="$(basename "$APP_DIR")"

LOG_DIR="/var/log/$APP_NAME"
VENV_DIR="$APP_DIR/venv"
REQUIREMENTS_FILE="$APP_DIR/pypi/prod.txt"

SUPERVISOR_CONF_DIR="/etc/supervisor/conf.d"

DEPLOY_DIR="$APP_DIR/deploy"
STUB_DIR="$DEPLOY_DIR/stubs"
PROD_DIR="$DEPLOY_DIR/prod"

ENV_FILE="$APP_DIR/.env"
ENV_EXAMPLE_FILE="$APP_DIR/.env-example"

USER="www-data"
GROUP="www-data"

cd "$APP_DIR"

# ------------------------------
# User & Group
# ------------------------------
create_group_and_user() {
    if ! getent group "$GROUP" &>/dev/null; then
        groupadd "$GROUP"
    fi

    if ! id "$USER" &>/dev/null; then
        useradd -m -s /bin/bash "$USER"
    fi

    usermod -aG "$GROUP" root
    usermod -aG "$GROUP" "$USER"
}

# ------------------------------
# System Dependencies
# ------------------------------
install_system_dependencies() {
    apt update -qq

    apt install -y -qq \
        redis supervisor nginx \
        python3-venv python3-dev python3-setuptools \
        build-essential libpq-dev \
        libpango-1.0-0 libpango1.0-dev \
        libcairo2 libffi-dev \
        libgdk-pixbuf2.0-0 libpangocairo-1.0-0 \
        python3-certbot-nginx
}

# ------------------------------
# Python Env
# ------------------------------
setup_python_environment() {
    if [[ ! -d "$VENV_DIR" ]]; then
        python3 -m venv "$VENV_DIR"
    fi

    source "$VENV_DIR/bin/activate"

    pip install --upgrade pip setuptools
    pip install uvicorn[standard]
    pip install -r "$REQUIREMENTS_FILE"
}

# ------------------------------
# Permissions
# ------------------------------
set_permissions() {
    chown -R "$USER:$GROUP" "$APP_DIR"

    find "$DEPLOY_DIR" -type f -name "*.sh" -exec chmod +x {} \;
}

# ------------------------------
# Logs
# ------------------------------
create_log_dirs() {
    mkdir -p "$LOG_DIR"
    chown -R "$USER:$GROUP" "$LOG_DIR"
    chmod 755 "$LOG_DIR"
}

# ------------------------------
# ENV
# ------------------------------
setup_env_file() {
    if [[ -f "$ENV_FILE" ]]; then
        return
    fi

    cp "$ENV_EXAMPLE_FILE" "$ENV_FILE"
}

# ------------------------------
# STUB ENGINE (CORE)
# ------------------------------
generate_conf_files() {
    echo "Generating configuration files from metadata stubs..."

    if [[ -z "${STUB_DIR:-}" ]] || [[ ! -d "$STUB_DIR" ]]; then
        echo "ERROR: STUB_DIR is invalid" >&2
        return 1
    fi

    # 1. Declare locals once at the top of the function
    local stub target owner mode output

    while IFS= read -r -d '' stub; do
        echo "Processing: $stub"

        # -----------------------------
        # Robust metadata parsing
        # -----------------------------
        # 2. Use 'sub' to prevent truncating values that contain an '=' sign
        target=$(awk '/^# target=/{sub(/^# target=/, ""); print; exit}' "$stub")
        owner=$(awk '/^# owner=/{sub(/^# owner=/, ""); print; exit}' "$stub")
        mode=$(awk '/^# mode=/{sub(/^# mode=/, ""); print; exit}' "$stub")

        # -----------------------------
        # Validate metadata contract
        # -----------------------------
        if [[ -z "$target" ]]; then
            echo "ERROR: Missing # target in $stub" >&2
            return 1
        fi

        if [[ "${target:0:1}" != "/" ]]; then
            echo "ERROR: target must be absolute path: $target" >&2
            return 1
        fi

        output="$target"
        mkdir -p "$(dirname "$output")"

        echo "-> Writing $output"

        # -----------------------------
        # Render template safely
        # -----------------------------
        sed \
            -e '/^# target=/d' \
            -e '/^# owner=/d' \
            -e '/^# mode=/d' \
            -e "s|{{project_name}}|${APP_NAME:-}|g" \
            -e "s|{{app_name}}|${APP_NAME:-}|g" \
            -e "s|{{app_dir}}|${APP_DIR:-}|g" \
            -e "s|{{log_dir}}|${LOG_DIR:-}|g" \
            -e "s|{{venv_dir}}|${VENV_DIR:-}|g" \
            -e "s|{{user}}|${USER:-}|g" \
            -e "s|{{group}}|${GROUP:-}|g" \
            "$stub" > "$output"

        # -----------------------------
        # Permissions (safe + explicit)
        # -----------------------------
        if [[ -n "$owner" ]]; then
            chown "$owner" "$output" \
                || echo "WARNING: chown failed for $output" >&2
        fi

        if [[ -n "$mode" ]]; then
            chmod "$mode" "$output" \
                || echo "WARNING: chmod failed for $output" >&2
        else
            chmod 644 "$output"
        fi

    done < <(find "$STUB_DIR" -type f -name "*.stub" -print0)
}

# ------------------------------
# Supervisor
# ------------------------------
setup_supervisor() {
    generate_conf_files

    supervisorctl reread
    supervisorctl update
}

# ------------------------------
# Django Tasks
# ------------------------------
run_django_tasks() {
    source "$VENV_DIR/bin/activate"

    python manage.py collectstatic --noinput
    python manage.py migrate
}

# ------------------------------
# MAIN
# ------------------------------
main() {
    create_group_and_user
    install_system_dependencies
    setup_python_environment
    set_permissions
    create_log_dirs
    setup_env_file
    setup_supervisor
    run_django_tasks

    echo "Deployment completed successfully for $APP_NAME"
}

main "$@"