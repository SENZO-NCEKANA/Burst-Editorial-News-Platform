# Burst News Application - Docker image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies for Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN adduser --disabled-password --gecos '' appuser

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY --chown=appuser:appuser . .

# Make entrypoint executable
RUN chmod +x /app/docker-entrypoint.sh

# Create directories for DB, media, and data
RUN mkdir -p /app/media /app/static /app/data && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Default: run Django dev server (override for production with gunicorn)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
