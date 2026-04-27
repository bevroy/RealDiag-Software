
# RealDiag Backend API - Version 1.0.1
# Updated 2025-12-11: Comprehensive medical presentations and homeopathy aliases

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
from backend.services.rules_router import router as rules_router
from backend.services.reference_router import router as reference_router
from backend.services.symptom_search import router as symptom_search_router
from backend.services.integration_router import router as integration_router
from backend.services.user_router import router as user_router
from backend.services.education_router import router as education_router
from backend.services.smart_router import router as smart_router
from backend.services.subscription_router import router as subscription_router
from backend.services.homeopathy_router import router as homeopathy_router
from backend.services.mfa_router import router as mfa_router
from backend.services.search_router import router as search_router
from backend.services.context_router import router as context_router

# Import admin router for AI tree management
try:
    from backend.services.admin_router import router as admin_router
    ADMIN_ROUTER_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Admin router not available: {e}")
    ADMIN_ROUTER_AVAILABLE = False
    admin_router = None

# Import test environment utilities
try:
    from backend.services.test_environment import (
        TestEnvironmentMiddleware,
        is_test_mode,
        should_bypass_subscription
    )
    TEST_ENVIRONMENT_AVAILABLE = True
except ImportError:
    TEST_ENVIRONMENT_AVAILABLE = False
    TestEnvironmentMiddleware = None
    def is_test_mode(): return False
    def should_bypass_subscription(): return False

# Import security features with fallback
try:
    from backend.services.security import security_middleware, limiter
    from slowapi.errors import RateLimitExceeded
    from slowapi import _rate_limit_exceeded_handler
    SECURITY_ENABLED = True
except ImportError as e:
    logging.warning(f"Security features not available: {e}. Running without rate limiting.")
    SECURITY_ENABLED = False
    security_middleware = None
    limiter = None

from config import Config

# Basic structured logging (must be first)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("realdiag")

# Initialize Sentry for error tracking (production)
SENTRY_DSN = os.getenv("SENTRY_DSN")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Log environment and test mode status
logger.info(f"🌍 Environment: {ENVIRONMENT}")
if is_test_mode():
    logger.info("🧪 TEST MODE ENABLED - All users granted enterprise access")
    logger.info("🔓 Subscription checks: BYPASSED")
    logger.info("⚠️  This should NEVER appear in production!")
else:
    logger.info("🔒 Production mode - Subscription checks active")

if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            environment=ENVIRONMENT,
            traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
            profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1")),
            integrations=[
                FastApiIntegration(transaction_style="url"),
                LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.ERROR
                ),
            ],
            # Set release version for better tracking
            release=f"realdiag@{Config.APP_VERSION}",
            # Sample errors in production
            before_send=lambda event, hint: event if ENVIRONMENT == "production" else None if ENVIRONMENT == "development" else event,
        )
        logger.info(f"✅ Sentry initialized for environment: {ENVIRONMENT}")
    except ImportError:
        logger.warning("⚠️  Sentry SDK not installed. Error tracking disabled.")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Sentry: {e}")
else:
    logger.info("ℹ️  Sentry DSN not configured. Error tracking disabled.")

app = FastAPI(
    title="RealDiag API", 
    version="1.4.0", 
    description="Clinical Decision Support System with Enhanced Security and Medical Training Tools"
)

# Add test environment middleware FIRST if test mode is enabled
if TEST_ENVIRONMENT_AVAILABLE and is_test_mode():
    app.add_middleware(TestEnvironmentMiddleware)
    logger.info("✅ Test environment middleware enabled")

# Add compression middleware for better performance
try:
    from backend.services.compression_middleware import CompressionMiddleware
    app.add_middleware(CompressionMiddleware, min_size=500, compression_level=6)
    logger.info("✅ Response compression enabled (gzip)")
except ImportError:
    logger.warning("⚠️  Compression middleware not available")

# Add rate limiter to app state if security is enabled
if SECURITY_ENABLED:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    logger.info("✅ Rate limiting enabled: 1000 requests/hour global, specific limits on auth and search endpoints")

# Database initialization on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    try:
        from backend.services.database import DATABASE_AVAILABLE, init_database, check_database_connection
        
        if DATABASE_AVAILABLE:
            logger.info("🔄 Initializing database...")
            
            # Check connection
            if check_database_connection():
                logger.info("✅ Database connection verified")
                
                # Create tables if they don't exist
                init_database()
                logger.info("✅ Database initialized successfully")
            else:
                logger.error("❌ Database connection failed")
        else:
            logger.warning("⚠️  Database not configured - using in-memory storage")
    
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        # Don't crash the app - fall back to in-memory storage
        logger.warning("⚠️  Falling back to in-memory storage")

# Prometheus metrics
REQUEST_COUNTER = Counter('realdiag_requests_total', 'Total HTTP requests', ['path', 'method', 'status'])

# Include routers
app.include_router(diagnostic_router)
app.include_router(rules_router)
app.include_router(reference_router)
app.include_router(symptom_search_router)
app.include_router(integration_router)
app.include_router(user_router)
app.include_router(education_router)
app.include_router(smart_router)
app.include_router(subscription_router)
app.include_router(homeopathy_router)
app.include_router(mfa_router)
app.include_router(search_router)
app.include_router(context_router)

# /analyze endpoint backed by the modular DOMAIN_ANALYZERS chain
from backend.schemas.diagnostic import AnalyzeRequest
from backend.services.diagnostic_engine import analyze_case


@app.post("/analyze", tags=["analyze"])
def analyze_endpoint(payload: AnalyzeRequest):
    return analyze_case(payload)

# Include admin router if available
if ADMIN_ROUTER_AVAILABLE and admin_router:
    app.include_router(admin_router)
    logger.info("✅ Admin endpoints enabled for AI tree management")

# Include monitoring router if available
try:
    from backend.services.monitoring import router as monitoring_router
    app.include_router(monitoring_router)
    logger.info("Monitoring endpoints enabled")
except ImportError:
    logger.warning("Monitoring module not available")


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
    PREVIEW_ORIGIN_REGEX_COMBINED = r"^https?://(?:localhost(?::\d+)?|.+-\d+\.app\.github\.dev|(?:%s))$" % _netlify_part


# Add security middleware FIRST (before CORS) if security is enabled
if SECURITY_ENABLED and security_middleware:
    app.middleware("http")(security_middleware)

# CORS Configuration - Allow all domains (production + development)
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Allow both production and development origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Production domains
        "https://realdiag.com",
        "https://www.realdiag.com",
        "https://api.realdiag.com",
        # Development/Staging domains
        "http://localhost:3000",
        "http://localhost:8080",
        "https://realdiag.netlify.app",
        "https://main--realdiag.netlify.app",
    ],
    allow_origin_regex=PREVIEW_ORIGIN_REGEX_COMBINED,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
logger.info(f"✅ CORS configured for {ENVIRONMENT} (permissive)")


@app.get('/metrics')
def metrics():
    """Expose Prometheus metrics."""
    return generate_latest()


@app.get("/health")
def health_check():
    """
    Health check endpoint with environment status.
    Shows test mode status and feature availability.
    """
    health_status = {
        "status": "healthy",
        "version": Config.APP_VERSION,
        "environment": ENVIRONMENT,
        "test_mode": is_test_mode(),
    }
    
    # Add test mode specific info
    if is_test_mode():
        health_status["test_info"] = {
            "subscription_checks": "bypassed",
            "user_access_level": "enterprise",
            "rate_limiting": "disabled",
            "payment_processing": "disabled",
            "warning": "Test environment - not for production use"
        }
    
    # Add feature flags
    health_status["features"] = {
        "security_enabled": SECURITY_ENABLED,
        "test_environment_available": TEST_ENVIRONMENT_AVAILABLE,
        "subscription_bypass": should_bypass_subscription(),
    }
    
    return health_status


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

