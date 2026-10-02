# Docker Deployment Guide

Run math-trace with Docker Compose for a complete, reproducible environment.

## Quick Start

```bash
# Start FastAPI server with formula browser
docker compose up -d

# Open in browser
open http://localhost:8000

# View logs
docker compose logs -f math-trace
```

## With Ollama (Optional)

Enable overnight batch LaTeX→SymPy conversion:

```bash
# Start with Ollama for batch processing
docker compose --profile dev up -d

# Pull a small LLM (first time only, ~4GB)
docker compose exec ollama ollama pull mistral

# Now you can dispatch batch conversion tasks:
docker compose exec math-trace python -m math_trace.ollama_arxiv_worker convert 2301.13848
```

## Components

### `math-trace` (FastAPI Server)
- **Port:** 8000
- **Endpoints:**
  - `GET /` — Interactive dashboard with formula browser
  - `POST /api/arxiv/extract` — Download and extract paper equations
  - `GET /api/arxiv/papers/{id}` — Get cached paper
  - `GET /api/formulas/arxiv-papers` — List cached papers (HTMX)
  - `GET /api/formulas/local-models` — Find local models (HTMX)

### `ollama` (Optional)
- **Port:** 11434
- **Profile:** `dev` (use `--profile dev` to enable)
- **GPU Support:** Uncomment `deploy.resources` section in `compose.yaml`
- **Models:** Download with `ollama pull <model-name>`

## Volumes

- **`math-trace-cache`**: Stores cached papers at `~/.math-trace/arxiv-cache/`
- **`ollama-models`**: Stores downloaded LLM models

Access cached papers:
```bash
docker compose exec math-trace ls -la ~/.math-trace/arxiv-cache/papers/
```

## Workflows

### 1. Extract Paper + Browse Formulas

```bash
# Terminal 1: Start server
docker compose up

# Terminal 2: Call extraction endpoint
curl -X POST http://localhost:8000/api/arxiv/extract \
  -H "Content-Type: application/json" \
  -d '{"paper_url_or_id": "2301.13848"}'

# Response: 45 equations cached, ready to use

# Terminal 3: Open UI and browse
# http://localhost:8000 → Click "Cached Papers" → Select equations → Compose presentation
```

### 2. Batch Convert Equations (with Ollama)

```bash
# Start with Ollama
docker compose --profile dev up -d

# Download a model (one time)
docker compose exec ollama ollama pull mistral

# Extract paper
curl -X POST http://localhost:8000/api/arxiv/extract \
  -d '{"paper_url_or_id": "2301.13848"}'

# Convert equations asynchronously
docker compose exec math-trace python -m math_trace.ollama_arxiv_worker convert 2301.13848

# Results: cached paper now has sympy_expr field populated
```

### 3. Use Local Models

```bash
# Mount local examples
docker compose exec math-trace python -m math_trace.formula_browser list_local_models \
  --pattern "*/src/model.py" \
  --root examples

# Output: [{path: examples/membrane-dynamics/src/model.py, formula_count: 5}, ...]

# Use in browser: Click "Local Models" → Select model → Browse formulas
```

## Configuration

### Expose to Network

Change port in `compose.yaml`:
```yaml
ports:
  - "0.0.0.0:8000:8000"  # Listen on all interfaces
```

### Enable GPU for Ollama

Uncomment in `compose.yaml`:
```yaml
ollama:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

Requires: `nvidia-docker` + `docker-compose` v1.29+

### Increase Ollama Memory

Set environment variable:
```yaml
environment:
  - OLLAMA_HOST=0.0.0.0:11434
  - OLLAMA_NUM_PARALLEL=4  # Parallel requests
  - OLLAMA_KEEP_ALIVE=5m   # Model stays loaded 5min
```

## Troubleshooting

### Port 8000 already in use

```bash
# Find what's using port 8000
lsof -i :8000

# Use different port
docker compose up -e "FASTAPI_PORT=8001"
# Then visit http://localhost:8001
```

### Ollama out of memory

```bash
# Check container memory
docker compose exec ollama free -h

# Increase Docker memory limit in compose.yaml:
services:
  ollama:
    deploy:
      resources:
        limits:
          memory: 16G
```

### Cache not persisting

Ensure volumes are mounted:
```bash
docker compose exec math-trace ls -la /root/.math-trace/
# Should show: arxiv-cache/
```

### Ollama model not found

```bash
# List available models
docker compose exec ollama ollama list

# Pull a model
docker compose exec ollama ollama pull llama2

# Or use Mistral (smaller, faster)
docker compose exec ollama ollama pull mistral
```

## Cleanup

```bash
# Stop services
docker compose down

# Remove all data (caches, models)
docker compose down -v

# Remove images
docker compose down --rmi all
```

## Production Deployment

For production use:
1. Build image: `docker build -t math-trace:latest .`
2. Push to registry: `docker push myregistry/math-trace:latest`
3. Use in kubernetes/swarm/cloud run with appropriate resource limits
4. Mount persistent volume for `math-trace-cache` across instances
5. Optionally separate Ollama to GPU machine with `docker service` or k8s

## Next Steps

- [arXiv Extraction Workflow](arxiv-extraction-workflow.md)
- [Interactive Presentation Builder](../README.md)
