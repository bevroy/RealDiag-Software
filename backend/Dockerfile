
FROM python:3.11-slim
WORKDIR /app
COPY backend /app/backend
# Copy shared top-level modules/config used by the backend
COPY config.py /app/config.py
COPY diagnostics /app/diagnostics
# Install runtime dependencies directly instead of building the backend as a distribution.
# Building the package fails in a flat layout with multiple top-level packages. The source
# is already copied into /app/backend so Python can import it directly at runtime.
RUN pip install --no-cache-dir fastapi pyyaml uvicorn[standard] jinja2
EXPOSE 8000
CMD ["uvicorn","backend.main:app","--host","0.0.0.0","--port","8000"]
