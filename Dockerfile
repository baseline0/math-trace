FROM python:3.13-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/
COPY examples/ ./examples/
COPY docs/ ./docs/

# Install dependencies
RUN pip install --no-cache-dir -e .

# Create cache directory
RUN mkdir -p /root/.math-trace/arxiv-cache

# Expose FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Default: run FastAPI server
CMD ["python", "-m", "math_trace.server"]
