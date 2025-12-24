import logging
from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import JSONResponse

from app.core.rate_limiter import limiter
from app.core.config import settings
from app.db.init_db import init_db
from app.api.claims import router as claims_router
from app.api.providers import router as providers_router
from app.api.health import router as health_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Claims Analytics API",
    version="1.0.0",
)

@app.on_event("startup")
def on_startup():
    init_db()

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"},
    )

app.include_router(claims_router)
app.include_router(providers_router)
app.include_router(health_router)
