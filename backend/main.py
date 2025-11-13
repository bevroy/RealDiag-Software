
import os
import re
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

# Include diagnostic router
app.include_router(diagnostic_router)


# Serve static files (assets)
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# Jinja2 templates directory
templates = Jinja2Templates(directory="backend/templates")

# Compute a safe preview origin regex. If PREVIEW_ORIGIN_REGEX is set in the
# environment (for example, by Render), include its pattern but also ensure the
# Netlify preview hostnames for this site are allowed so Netlify previews can
# call this API without requiring a manual env var change in Render.
_preview_env = os.getenv("PREVIEW_ORIGIN_REGEX")
_netlify_part = r"(?:[A-Za-z0-9-]+--)?realdiag\.netlify\.app"
if _preview_env:
    # strip optional leading scheme anchor and trailing dollar so we can embed
    _p = re.sub(r'^https?://', '', _preview_env)
    _p = re.sub(r'\$$', '', _p)
    PREVIEW_ORIGIN_REGEX_COMBINED = r"^https?://(?:(?:%s)|(?:%s))$" % (_p, _netlify_part)
else:
    PREVIEW_ORIGIN_REGEX_COMBINED = r"^https?://(?:localhost(?::\d+)?|.+-3000\.app\.github\.dev|(?:%s))$" % _netlify_part


# Allow CORS from local frontend during development
app.add_middleware(
    CORSMiddleware,
    # Allow the local frontend origin and preview hostnames (Codespaces / GitHub preview).
    # The preview regex can be overridden via PREVIEW_ORIGIN_REGEX env var for portability.
    # Also allow the Netlify production/preview domains that host the frontend so
    # browser requests from the deployed frontend can reach this API.
    allow_origins=[
        "http://localhost:3000",
        "https://realdiag.netlify.app",
        "https://main--realdiag.netlify.app",
    ],
        # Allow dynamic preview hosts for the frontend. Netlify preview URLs look like
        # <deploy-id>--<site>.netlify.app (for example: 691393f018f33e61caabd45b--realdiag.netlify.app).
        # Use a conservative regex that matches the canonical Netlify preview pattern for this
        # project while still allowing localhost and common Codespaces/GH previews. The regex
        # can be overridden with the PREVIEW_ORIGIN_REGEX env var if needed.
        allow_origin_regex=PREVIEW_ORIGIN_REGEX_COMBINED,
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

