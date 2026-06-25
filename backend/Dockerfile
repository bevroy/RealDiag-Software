
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
COPY gunicorn.conf.py /app/gunicorn.conf.py

EXPOSE 8000
# Use optimized gunicorn configuration for production
# gunicorn.conf.py sets worker count, threads, preload, and other performance settings
CMD ["sh", "-c", "exec gunicorn -c gunicorn.conf.py backend.main:app"]
