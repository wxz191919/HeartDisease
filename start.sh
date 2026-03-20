#!/bin/bash
set -e
cd backend
pip install -r requirements.txt
exec gunicorn --bind "0.0.0.0:${PORT:-5000}" "app:create_app()"
