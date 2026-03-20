#!/bin/bash
set -e
cd backend
python -m pip install -r requirements.txt --quiet 2>/dev/null || true
exec gunicorn --bind "0.0.0.0:${PORT:-5000}" "app:create_app()"
