FROM python:3.11-slim

WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ app/

# The commit this image was built from; CI passes it in, /health reports it.
ARG APP_VERSION=dev
ENV APP_VERSION=$APP_VERSION PYTHONUNBUFFERED=1

RUN useradd --create-home appuser
USER appuser

# Render tells the service which port to listen on in $PORT.
# One worker with threads keeps all metrics in one process.
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 8 app.main:app"]
