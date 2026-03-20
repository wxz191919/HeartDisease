#!/bin/bash
set -e
cd backend
python3 -m pip install -r requirements.txt --quiet 2>/dev/null || true
exec python3 -m gunicorn --bind "0.0.0.0:${PORT:-5000}" "app:create_app()"
