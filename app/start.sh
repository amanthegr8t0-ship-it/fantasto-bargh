#!/bin/bash
celery -A api.tasks worker --loglevel=info --pool=solo &
uvicorn api.api:app --host 0.0.0.0 --port $PORT