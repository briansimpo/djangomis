#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

echo "Stopping all services..."

sudo supervisorctl stop gunicorn
sudo supervisorctl stop celery_worker
sudo supervisorctl stop celery_beat
sudo supervisorctl stop websocket

echo "All services have been stopped successfully."

