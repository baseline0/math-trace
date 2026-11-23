"""Run the math-trace FastAPI server."""

from __future__ import annotations

import os

import uvicorn

from .app import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=int(os.environ.get("FLEET_PORT", "8080")),
        reload=True,
    )
