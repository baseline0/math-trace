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


def test_normalize_empty_and_unparsed():
    ok, cs, h, s, err = normalize_latex(r"   \[ \]  ")
    assert (ok, cs, h, s) == (False, None, None, None)
    assert err == "empty"

    ok, _cs, _h, _s, err = normalize_latex(r"\newcommand{\x}{1}")
    assert ok is False
    assert isinstance(err, str) and err


def test_read_records_jsonl_ignores_blank_lines(tmp_path):
    from math_trace.formula_records import FormulaRecord, FormulaSource

    rec = FormulaRecord(
        record_id="sha256:abc",
        latex="x=y",
        canonical_srepr=None,
        expr_hash=None,
        sympy_str=None,
        concept_tags=(),
        source=FormulaSource(paper_id="p", file="f.tex", line=1),
    )
    path = tmp_path / "records.jsonl"
    path.write_text("\n" + __import__("json").dumps(rec.to_dict()) + "\n\n", encoding="utf-8")
    loaded = read_records_jsonl(path)
    assert len(loaded) == 1
    assert loaded[0].record_id == "sha256:abc"


def test_formula_records_package_exports():
    import math_trace.formula_records as fr

    for name in [
        "FormulaRecord",
        "FormulaSource",
        "build_formula_record",
        "build_records_from_tex",
        "extract_display_formulas",
        "infer_concept_tags",
        "normalize_latex",
        "read_records_jsonl",
        "records_to_jsonl",
        "stable_record_id",
        "write_records_jsonl",
    ]:
        assert hasattr(fr, name), name
    assert fr.normalize_latex is normalize_latex


def test_formula_record_from_dict_ignores_unknown_source_keys_and_defaults():
    rec = __import__("math_trace.formula_records", fromlist=["FormulaRecord"]).FormulaRecord.from_dict(
        {
            "record_id": "r1",
            "latex": "x=y",
            "source": {"paper_id": "p1", "unknown_future_key": "ignored", "line": 7},
            "concept_tags": ["entropy"],
        }
    )

    assert rec.record_id == "r1"
    assert rec.latex == "x=y"
    assert rec.source.paper_id == "p1"
    assert rec.source.line == 7
    assert not hasattr(rec.source, "unknown_future_key")
    assert rec.context == ""
    assert rec.concept_tags == ("entropy",)
    assert rec.normalized is False
    assert rec.schema_version == 1


def test_build_formula_record_respects_explicit_record_id():
    rec = build_formula_record("x=y", paper_id="p1", record_id="custom-id")

    assert rec.record_id == "custom-id"
