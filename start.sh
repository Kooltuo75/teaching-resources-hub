#!/bin/bash
# Startup script for Render deployment
# Runs database migrations before starting the server

echo "Running database migrations..."
python migrate_db.py

echo "Starting Gunicorn server..."
gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 60 run:app
