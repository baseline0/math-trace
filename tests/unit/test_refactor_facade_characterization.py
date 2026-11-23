"""Characterization tests for refactor facades/public API seams."""

from __future__ import annotations

from pathlib import Path

import pytest


def test_paper_store_package_exports_preserved():
    import math_trace.paper_store as ps
    from math_trace.paper_store import (
        ALLOWED_LICENCES,
        PaperBrokenError,
        PaperNotFoundError,
        PaperRecord,
        PaperRestrictedError,
        PaperStatus,
        PaperStore,
        PaperStoreError,
    )

    assert ps.PaperStore is PaperStore
    assert ps.PaperStoreError is PaperStoreError
    assert ps.PaperNotFoundError is PaperNotFoundError
    assert ps.PaperBrokenError is PaperBrokenError
    assert ps.PaperRestrictedError is PaperRestrictedError
    assert ps.PaperStatus is PaperStatus
    assert ps.PaperRecord is PaperRecord
    assert ps.ALLOWED_LICENCES == ALLOWED_LICENCES
    # back-compat private helpers used by tests/internal callers
    for name in ["_check_sha256", "_check_arxiv_id", "_parse_manifest", "_parse_membership"]:
        assert hasattr(ps, name)


def test_paper_store_validation_errors_are_characterized(tmp_path: Path):
    from math_trace.paper_store import PaperBrokenError, PaperStore, PaperStoreError

    with pytest.raises(PaperStoreError, match="not a directory"):
        PaperStore(tmp_path / "missing")

    store = PaperStore(tmp_path)
    with pytest.raises(PaperStoreError, match="sha256"):
        store.get_blob("not-a-hash")
    with pytest.raises(PaperStoreError, match="arXiv ID"):
        store.read_manifest("../bad")

    paper_dir = tmp_path / "papers" / "2610.23820"
    paper_dir.mkdir(parents=True)
    (paper_dir / "latest").write_text("bad-name.json", encoding="utf-8")
    with pytest.raises(PaperBrokenError, match="manifest file name"):
        store.read_manifest("2610.23820")


def test_server_routes_formulas_facade_exports():
    from math_trace.server import routes_formulas
    from math_trace.server.routes_formulas import router
    from math_trace.server.routes_formulas_api import get_formulas, get_preview
    from math_trace.server.routes_formulas_browser import (
        browse_arxiv_papers,
        browse_local_models,
        get_arxiv_equations,
        get_local_model_formulas,
    )

    assert routes_formulas.get_formulas is get_formulas
    assert routes_formulas.get_preview is get_preview
    assert routes_formulas.browse_arxiv_papers is browse_arxiv_papers
    assert routes_formulas.browse_local_models is browse_local_models
    assert routes_formulas.get_arxiv_equations is get_arxiv_equations
    assert routes_formulas.get_local_model_formulas is get_local_model_formulas

    paths = {getattr(route, "path", None) for route in router.routes}
    assert "/api/formulas" in paths
    assert "/api/preview/{paper_id}/{formula_id}" in paths
    assert "/api/formulas/arxiv-papers" in paths
    assert "/api/formulas/local-models" in paths
    assert "/api/formulas/arxiv/{paper_id}/equations" in paths
    assert "/api/formulas/local/{path:path}/equations" in paths


def test_server_package_exports_preserve_formula_routes():
    import math_trace.server as server

    for name in [
        "browse_arxiv_papers",
        "browse_local_models",
        "get_arxiv_equations",
        "get_formulas",
        "get_local_model_formulas",
        "get_preview",
    ]:
        assert hasattr(server, name)
