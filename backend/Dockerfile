
FROM python:3.11-slim
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN apt-get update \
	&& apt-get install -y --no-install-recommends curl \
	&& rm -rf /var/lib/apt/lists/* \
	&& pip install --no-cache-dir -r requirements.txt \
	&& pip cache purge

# Copy application code AFTER dependencies
# This ensures code changes (including YAML rules) trigger rebuild from here
COPY backend /app/backend
COPY config.py /app/config.py
COPY diagnostics /app/diagnostics

EXPOSE 8000
	# Use gunicorn with the Uvicorn worker for production. Wrap in a shell so ${PORT} is expanded at runtime
	# (Render provides $PORT). Fall back to 8000 when not set. Log to stdout/stderr so platform logs capture output.
	# Using 2 workers for better concurrency (Transaction mode pooler supports high connection count)
	CMD ["sh", "-c", "exec gunicorn -k uvicorn.workers.UvicornWorker -w 2 backend.main:app --bind 0.0.0.0:${PORT:-8000} --timeout 120 --access-logfile - --error-logfile -"]
