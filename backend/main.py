
import os
from fastapi import FastAPI, Request
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from backend.services.diagnostic_router import router as diagnostic_router
from config import Config

app = FastAPI(title="RealDiag API")

# Basic structured logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("realdiag")

# Prometheus metrics
REQUEST_COUNTER = Counter('realdiag_requests_total', 'Total HTTP requests', ['path', 'method', 'status'])


# Serve static files (assets)
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# Jinja2 templates directory
templates = Jinja2Templates(directory="backend/templates")


# Allow CORS from local frontend during development
app.add_middleware(
    CORSMiddleware,
    # Allow the local frontend origin and preview hostnames (Codespaces / GitHub preview).
    # The preview regex can be overridden via PREVIEW_ORIGIN_REGEX env var for portability.
    allow_origins=["http://localhost:3000"],
    allow_origin_regex=os.getenv(
        "PREVIEW_ORIGIN_REGEX",
        r"^https?://(?:localhost(?::\d+)?|.+-3000\.app\.github\.dev)$",
    ),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get('/metrics')
def metrics():
    """Expose Prometheus metrics."""
    return generate_latest()


@app.get("/")
def root(request: Request):
    """Serve a Jinja2-rendered HTML index for HTML clients; redirect non-HTML clients to /docs.

    Detection is done via the Accept header: if the client accepts text/html we render the
    template. Otherwise we send a 301 redirect to /docs for API clients and bots.
    """
    accept = request.headers.get("accept", "")
    if "text/html" in accept or "*/*" in accept:
        # Render template with app/version context using the new TemplateResponse signature
        # (request, name, context) to avoid the deprecation warning.
        return templates.TemplateResponse(request, "index.html", {"request": request, "app": Config.APP_NAME, "version": Config.APP_VERSION})
    # Non-browser clients: redirect to docs
    return RedirectResponse(url="/docs", status_code=301)


@app.get("/health")
def health():
    REQUEST_COUNTER.labels(path='/health', method='GET', status='200').inc()
    logger.info('health check')
    return {"ok": True}


@app.get("/version")
def version():
    """Return application name and version."""
    return {"app": Config.APP_NAME, "version": Config.APP_VERSION}


@app.get("/health/version")
def health_version():
    """Return health status plus version metadata."""
    return {"ok": True, "app": Config.APP_NAME, "version": Config.APP_VERSION}


app.include_router(diagnostic_router)
