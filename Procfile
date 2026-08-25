# 1. The Web Server (Handles HTTP)
web: python manage.py runserver 8000

# 2. The Frontend (Vite Dev Server)
vite: npm run dev

# 3. The Background Task Worker
worker: celery -A config.celery_app worker --loglevel=info

# 4. The Task Scheduler (Beat)
# beat: celery -A config.celery_app beat --loglevel=info


# 5. The Websocket Server
# websocket: uvicorn config.asgi:application --host 0.0.0.0 --port 8001