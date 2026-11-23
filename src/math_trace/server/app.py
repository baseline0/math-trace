"""FastAPI application wiring for math-trace."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .routes_arxiv import router as arxiv_router
from .routes_formulas import router as formulas_router
from .routes_hardness import router as hardness_router
from .ui import DASHBOARD_HTML


def create_app() -> FastAPI:
    app = FastAPI(
        title="math-trace Slide Editor",
        description="Interactive slide development with live formula preview",
        version="0.1.0",
    )

    @app.get("/healthz")
    @app.get("/api/health")
    async def health():
        """Liveness check: cheap, no dependencies. /api/health is an alias."""
        return {"status": "ok", "version": "0.1.0"}

    @app.get("/", response_class=HTMLResponse)
    async def dashboard():
        """Serve interactive slide editor dashboard."""
        return DASHBOARD_HTML

    @app.get("/health", response_class=HTMLResponse)
    async def root():
        """Redirect root to dashboard."""
        return DASHBOARD_HTML

    app.include_router(arxiv_router)
    app.include_router(formulas_router)
    app.include_router(hardness_router)
    return app


app = create_app()
