"""DrugLab / DrugPedia - Main FastAPI Application (Phase 2).

Production-ready pharmaceutical knowledge platform, preformulation database,
and multi-tenant enterprise backend.
"""

from contextlib import asynccontextmanager
import logging
from typing import AsyncIterator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from .database import ANONYMOUS, TenantContext, check_db_health, platform_admin_session
from .dependencies import resolve_tenant_context
from .routes.compatibility import router as compatibility_router
from .routes.drugs import router as drugs_router
from .routes.excipients import router as excipients_router
from .routes.literature import router as literature_router
from .routes.rag import router as rag_router

logger = logging.getLogger("druglab")


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Middleware ensuring request.state.tenant_context is always initialized."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Extract headers or query params to establish tenant isolation
        x_tenant_id = request.headers.get("X-Tenant-ID")
        x_platform_admin = request.headers.get("X-Platform-Admin")
        tenant_param = request.query_params.get("tenant_id")

        is_admin = (x_platform_admin or "").lower() in ("true", "1", "yes")

        parsed_tenant_id = None
        if x_tenant_id or tenant_param:
            try:
                import uuid
                parsed_tenant_id = uuid.UUID(x_tenant_id or tenant_param)
            except ValueError:
                pass

        request.state.tenant_context = TenantContext(
            tenant_id=parsed_tenant_id,
            is_platform_admin=is_admin,
        )

        response = await call_next(request)
        return response


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup and shutdown lifecycle handler."""
    logger.info("Starting DrugLab API engine...")
    # Verify DB connectivity on startup
    try:
        with platform_admin_session() as s:
            health = check_db_health(s)
            logger.info("Database connection verified: %s", health)
    except Exception as e:
        logger.error("Database connection warning during startup: %s", e)
    yield
    logger.info("Shutting down DrugLab API engine...")


app = FastAPI(
    title="DrugLab / DrugPedia API",
    description=(
        "Production-grade, source-linked pharmaceutical knowledge platform, "
        "preformulation metrics repository, and drug-excipient compatibility engine."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration for Frontend SPA (Vite / Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # configure specific domains in enterprise production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TenantContextMiddleware)


# Health check endpoints
@app.get("/health", tags=["System"])
@app.get("/api/v1/health", tags=["System"])
def health_check():
    """Verify backend and database health, pgvector extension, and tenancy."""
    with platform_admin_session() as s:
        status_info = check_db_health(s)
    return {
        "status": "healthy",
        "service": "DrugLab API",
        "version": "1.0.0",
        **status_info,
    }


import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Register v1 routes
app.include_router(drugs_router, prefix="/api/v1")
app.include_router(compatibility_router, prefix="/api/v1")
app.include_router(excipients_router, prefix="/api/v1")
app.include_router(literature_router, prefix="/api/v1")
app.include_router(rag_router, prefix="/api/v1")

# Mount production Frontend SPA if built
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    if (FRONTEND_DIST / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Allow API routes, docs, and health checks to pass through or 404 naturally
        if full_path.startswith(("api/", "docs", "redoc", "openapi.json", "health")):
            return Response(status_code=404)
        file_path = FRONTEND_DIST / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")


