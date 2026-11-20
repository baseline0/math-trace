from __future__ import annotations

from math_trace.formula_records import (
    build_formula_record,
    build_records_from_tex,
    extract_display_formulas,
    infer_concept_tags,
    normalize_latex,
    read_records_jsonl,
    stable_record_id,
    write_records_jsonl,
)


def test_stable_record_id_deterministic():
    a = stable_record_id("p1", "f.tex", "10", "H(X)")
    b = stable_record_id("p1", "f.tex", "10", "H(X)")
    c = stable_record_id("p1", "f.tex", "11", "H(X)")
    assert a == b and a.startswith("sha256:")
    assert a != c


def test_build_record_preserves_raw_and_tags():
    r = build_formula_record(r"H(X,Y)=H(X)+H(Y\mid X)", paper_id="test", file="a.tex", line=10, context="chain rule")
    assert r.latex.startswith("H")
    assert r.source.paper_id == "test"
    assert r.source.line == 10
    assert r.record_id.startswith("sha256:")
    # heuristic tags should pick up entropy-ish content
    tags = set(r.concept_tags)
    assert "entropy" in tags or "chain_rule" in tags or "conditional_entropy" in tags


def test_normalize_best_effort():
    ok, cs, h, _s, err = normalize_latex(r"x + y")
    # may parse depending on environment; must not raise and must be consistent
    assert isinstance(ok, bool)
    if ok:
        assert cs and h and h.startswith("sha256:")
        assert err is None
    else:
        assert err is not None


def test_extract_display_formulas():
    tex = r"""
Some text.
\begin{equation}
H(X) = -\sum_x p(x)\log p(x)
\end{equation}
More text with inline $x$ and display \[I(X;Y)\ge 0\].
"""
    blocks = extract_display_formulas(tex)
    assert len(blocks) == 2
    assert blocks[0][1] == "equation"
    assert blocks[1][1] == "bracket"
    assert "H(X)" in blocks[0][2]
    assert blocks[0][0] >= 3


def test_build_records_from_tex_and_roundtrip(tmp_path):
    tex = r"Intro\\n\begin{align} I(X;Y)=H(X)-H(X|Y) \end{align}"
    recs = build_records_from_tex(tex, paper_id="p", file="m.tex")
    assert len(recs) == 1
    assert recs[0].source.env == "align"
    out = tmp_path / "r.jsonl"
    write_records_jsonl(recs, out)
    loaded = read_records_jsonl(out)
    assert len(loaded) == 1
    assert loaded[0].record_id == recs[0].record_id
    assert loaded[0].latex == recs[0].latex


def test_infer_concept_tags():
    tags = set(infer_concept_tags(r"D(p\|q) \ge 0", "KL divergence Pinsker"))
    assert "kl_divergence" in tags
    assert "pinsker" in tags
