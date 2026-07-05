# Multi-stage build for Marketing AI Platform

# Stage 1: Base Python image
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Dependencies
FROM base as dependencies

# Copy requirements
COPY backend/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Application
FROM base as application

# Copy installed dependencies from previous stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY backend/ /app/backend/
COPY api/ /app/api/
COPY database/ /app/database/
COPY frontend/ /app/frontend/

# Create necessary directories
RUN mkdir -p /app/frontend/static/uploads
RUN mkdir -p /app/database/migrations

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=backend/app.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

# Run with Gunicorn
CMD ["gunicorn", "-c", "deployment/gunicorn/gunicorn_config.py", "backend.wsgi:application"]
