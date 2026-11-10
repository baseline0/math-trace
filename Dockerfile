FROM python:3.13-slim

LABEL fleet.role="service"
ARG FLEET_BASE_SHA
LABEL fleet.sibling.fleet-base="${FLEET_BASE_SHA}"

ENV FLEET_DATA_DIR=/data
ENV HOME=/home/app

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Sibling snapshot: fleet-base at the pinned commit in the label above, exported
# by `git archive` into .sibling/ (ADR-021). Lands where ../fleet-base resolves from /workspace.
COPY .sibling/fleet-base /fleet-base

# Copy project files
COPY README.md ./
COPY pyproject.toml ./
COPY src/ ./src/
COPY examples/ ./examples/
COPY docs/ ./docs/

# Install the sibling first: pip ignores [tool.uv.sources], so the
# fleet-base>=0.6.0 requirement must be satisfied locally, not from PyPI.
RUN pip install --no-cache-dir -e /fleet-base \
    && pip install --no-cache-dir -e .

# Non-root service user (uid 10001) with its cache and data directories
RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid 10001 --home-dir /home/app --create-home app \
    && mkdir -p /home/app/.math-trace/arxiv-cache /data \
    && chown -R 10001:10001 /home/app /data

USER 10001

# Expose FastAPI port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/healthz || exit 1

# Default: run FastAPI server with uvicorn
CMD ["uvicorn", "math_trace.server:app", "--host", "0.0.0.0", "--port", "8080"]
