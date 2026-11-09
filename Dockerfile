FROM python:3.13-slim

LABEL fleet.role="service"

# FLEET_DATA_DIR is the mounted data root. HOME points under it so the server's
# ~/.math-trace cache and logs land in the writable volume for the non-root user.
ENV FLEET_DATA_DIR=/data \
    FLEET_PORT=8080 \
    HOME=/data

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY README.md ./
COPY pyproject.toml ./
COPY src/ ./src/
COPY examples/ ./examples/
COPY docs/ ./docs/

# Install dependencies
RUN pip install --no-cache-dir -e .

# Create cache and data directory, owned by the non-root service user
RUN mkdir -p /data/.math-trace/arxiv-cache \
    && chown -R 10001:10001 /data

# Expose FastAPI port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${FLEET_PORT}/healthz || exit 1

USER 10001:10001

# Default: run FastAPI server with uvicorn on FLEET_PORT
CMD ["sh", "-c", "exec uvicorn math_trace.server:app --host 0.0.0.0 --port \"$FLEET_PORT\""]
