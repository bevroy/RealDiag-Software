# PATCHED (audit fix): this image previously had no USER instruction, so
# the app ran as root inside the container. Added a dedicated non-root
# user and switched to it before the final CMD - if the app is ever
# compromised (e.g. via a dependency vuln), it now runs with an unprivileged
# UID instead of root inside the container.

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

# PATCHED: create and switch to a non-root user. Ownership of /app is
# reassigned so the app can still read its own code/data at runtime.
RUN groupadd --system realdiag && useradd --system --gid realdiag --home /app realdiag \
	&& chown -R realdiag:realdiag /app
USER realdiag

EXPOSE 8000
# Use optimized gunicorn configuration for production
# gunicorn.conf.py sets worker count, threads, preload, and other performance settings
CMD ["sh", "-c", "exec gunicorn -c gunicorn.conf.py backend.main:app"]
