"""Health routes: /healthz is the liveness probe, /api/health is an alias for it."""

import pytest
from fastapi.testclient import TestClient

from math_trace.server import app

client = TestClient(app)


@pytest.mark.parametrize("path", ["/healthz", "/api/health"])
def test_health_route_returns_ok_json(path: str) -> None:
    response = client.get(path)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "version" in body


def test_healthz_and_api_health_return_the_same_body() -> None:
    assert client.get("/healthz").json() == client.get("/api/health").json()
