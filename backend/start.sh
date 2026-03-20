#!/bin/bash
set -e
# Nixpacks 把 Python 放在 /opt/venv，确保 PATH 里有
export PATH="/opt/venv/bin:${PATH}"
python3 -m pip install -r requirements.txt --quiet 2>/dev/null || true
exec python3 -m gunicorn --bind "0.0.0.0:${PORT:-5000}" "app:create_app()"
