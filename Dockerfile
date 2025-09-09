# ====== RUNTIME STAGE ======
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies directly
RUN pip install --no-cache-dir \
    aiogram==3.22.0 \
    jinja2==3.1.6 \
    sqlalchemy==2.0.43 \
    alembic==1.16.5 \
    aiosqlite==0.21.0 \
    asyncpg==0.30.0 \
    pydantic==2.11.7 \
    python-dotenv==1.1.1 \
    openpyxl==3.1.5

# Copy source code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Copy and make entrypoint executable
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Start application
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["python", "app.py"]
