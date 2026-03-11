#!/bin/sh

echo "Starting API..."
uv run python main.py &

echo "Starting Celery..."
uv run celery -A src.core.celery worker -P solo --concurrency=1 --loglevel=info &

wait