"""Heuristic concept tagging for formula records."""

from __future__ import annotations

import re

_INFO_THEORY_PATTERNS: dict[str, tuple[str, ...]] = {
    "entropy": (r"\bH\s*[\(\[]", r"\\mathbb\{H\}", r"\\mathrm\{H\}", r"entropy"),
    "mutual_information": (r"\bI\s*[\(\[]", r"mutual.?information"),
    "kl_divergence": (r"\bD\s*[\(\[]", r"D_\{?KL\}?", r"\\mathrm\{KL\}", r"divergence"),
    "conditional_entropy": (r"H\s*\([^)]*\|", r"conditional.?entropy"),
    "chain_rule": (r"H\s*\([^,]+,\s*[^)]+\)", r"chain.?rule"),
    "data_processing": (r"\bDPI\b", r"data.?processing"),
    "pinsker": (r"Pinsker", r"total.?variation", r"\\|[^|]+\\|_1"),
    "fano": (r"Fano", r"P_e"),
    "markov": (r"Markov", r"\\to"),
    "jensen": (r"Jensen", r"concav", r"convex"),
    "log_sum_inequality": (r"log.?sum", r"\\log\s*\\frac"),
}


def infer_concept_tags(latex: str, context: str = "") -> tuple[str, ...]:
    """Heuristic concept tags for information-theoretic formulas (best-effort)."""
    hay = f"{latex}\n{context}"
    tags = [name for name, pats in _INFO_THEORY_PATTERNS.items() if any(re.search(p, hay, re.IGNORECASE) for p in pats)]
    return tuple(sorted(set(tags)))
