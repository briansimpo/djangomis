#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

echo "Restarting all services..."

sudo supervisorctl stop gunicorn
sudo supervisorctl stop celery_worker
sudo supervisorctl stop celery_beat
sudo supervisorctl stop websocket

sudo supervisorctl start gunicorn
sudo supervisorctl start celery_worker
sudo supervisorctl start celery_beat
sudo supervisorctl start websocket

echo "All services have been restarted successfully."
