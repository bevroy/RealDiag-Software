
FROM python:3.11-slim
WORKDIR /app
COPY backend /app/backend
# Copy shared top-level modules/config used by the backend
COPY config.py /app/config.py
COPY diagnostics /app/diagnostics
# Install runtime dependencies directly instead of building the backend as a distribution.
# Building the package fails in a flat layout with multiple top-level packages. The source
# is already copied into /app/backend so Python can import it directly at runtime.
RUN apt-get update \
	&& apt-get install -y --no-install-recommends curl \
	&& rm -rf /var/lib/apt/lists/* \
	&& pip install --no-cache-dir fastapi pyyaml uvicorn[standard] prometheus_client jinja2 gunicorn
EXPOSE 8000
	# Use gunicorn with the Uvicorn worker for production. Wrap in a shell so ${PORT} is expanded at runtime
	# (Render provides $PORT). Fall back to 8000 when not set. Log to stdout/stderr so platform logs capture output.
	CMD ["sh", "-c", "exec gunicorn -k uvicorn.workers.UvicornWorker -w 2 backend.main:app --bind 0.0.0.0:${PORT:-8000} --timeout 120 --access-logfile - --error-logfile -"]
