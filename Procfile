# 1. The Web Server (Handles HTTP)
web: python manage.py serve

# 2. The Frontend (Vite Dev Server)
vite: npm run dev

# 3. The Background Task Worker
worker: celery -A config.celery_app worker --loglevel=info

# 4. The Task Scheduler (Beat)
beat: celery -A config.celery_app beat --loglevel=info
