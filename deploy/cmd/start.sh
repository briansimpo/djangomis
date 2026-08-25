#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

echo "Starting all services..."

sudo supervisorctl start gunicorn
sudo supervisorctl start celery_worker
sudo supervisorctl start celery_beat
sudo supervisorctl start websocket

echo "All services have been started successfully."

