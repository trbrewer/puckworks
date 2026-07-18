"""PV-03 "The Cup Hides the Clock" — data-contract + static-site tests (issue #54, Section 7).

Offline. The quick lane transforms and verifies the COMMITTED Paper A result bundle; it never reruns
the slow scientific computation. Every headline number must trace to a bundle field or a named
producer — no hand-typed numbers in the HTML or JavaScript.
"""
import json
import re
from pathlib import Path

import pytest

from puckworks.public import flat_valley as FV
from puckworks.public.claims import PUBLIC_CLAIMS

_ROOT = Path(__file__).resolve().parents[1]
SITE = _ROOT / "docs" / "public" / "site" / "flat-valley"
SNAPSHOT = _ROOT / "puckworks" / "public" / "data" / "pv03_flat_valley.json"


@pytest.fixture(scope="module")
def snap():
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


# ── data contract (1,6,7,8,9,12) ─────────────────────────────────────────────────
def test_snapshot_has_required_schema(snap):
    for f in ("schema_version", "story_id", "source_commit", "source_bundle_sha256", "generator",
              "badge", "evidence_strength", "objective", "null_benchmark", "values", "units", "axes",
              "dataset_manifest_ids", "scope", "caveat", "right_censoring", "threshold_definitions"):
        assert f in snap, f"missing {f}"
    assert snap["story_id"] == "PV-03"
    assert snap["badge"] in ("OBSERVED", "RECONSTRUCTED", "PREDICTED", "EXPLORATORY_SIMULATION")
    assert snap["evidence_strength"] in ("independent", "post-fit reconstruction", "verification",
                                         "qualitative", "reference", "negative validation")


def test_every_value_has_a_unit_and_is_finite(snap):
    for k, v in snap["values"].items():
        assert k in snap["units"] and str(snap["units"][k]).strip(), f"{k} has no unit"
        assert FV._all_finite(v), f"{k} non-finite"
    for k, v in snap["axes"].items():
        assert FV._all_finite(v), f"axis {k} non-finite"


def test_no_non_finite_in_json(snap):
    js = SNAPSHOT.read_text(encoding="utf-8")
    assert not re.search(r"\bNaN\b|\bInfinity\b", js)


def test_right_censoring_and_null_benchmark_present(snap):
    assert snap["right_censoring"]["profile_upper_censored"] is True
    assert "level-only" in snap["null_benchmark"].lower()


def test_threshold_never_confidence_interval_and_coupling_never_correlation(snap):
    blob = json.dumps(snap).lower()
    assert "confidence interval" in blob   # only ever as an explicit NOT
    # every mention of 'confidence interval' is a negation
    for m in re.finditer(r"[^.]*confidence interval[^.]*", blob):
        assert "not" in m.group(0), m.group(0)
    # the coupling is explicitly NOT a statistical correlation
    assert "not a statistical" in blob and "correlation" in blob


# ── deterministic, hash-bound transform (2,3) ────────────────────────────────────
def test_transform_is_deterministic_and_matches_snapshot():
    a = FV._canonical_json(FV.build_payload())
    b = FV._canonical_json(FV.build_payload())
    assert a == b
    assert a == SNAPSHOT.read_text(encoding="utf-8"), "packaged snapshot is stale (run export)"


def test_source_bundle_sha_binds(snap, tmp_path):
    # a changed source bundle -> verify fails (hash binding)
    bad = tmp_path / "results.json"
    src = json.loads(FV.SOURCE_BUNDLE.read_text())
    src["panel_caffeine"]["condition_number"] = 9999.0
    bad.write_text(json.dumps(src))
    problems = FV.verify(source_path=bad)
    assert any("SHA-256 drift" in p or "stale" in p for p in problems)


def test_verify_clean_on_committed_state():
    assert FV.verify() == []


# ── held-out values match the bundle (13) ────────────────────────────────────────
def test_held_out_values_match_bundle(snap):
    bundle = json.loads(FV.SOURCE_BUNDLE.read_text())
    assert snap["values"]["held_out_model_mape"] == bundle["transfer_skill"]["pooled_model_mape"]
    assert snap["values"]["held_out_const_mape"] == bundle["transfer_skill"]["pooled_const_mape"]
    assert snap["values"]["n_model_worse_than_const"] == bundle["transfer_skill"]["n_model_worse_than_const"]
    assert snap["values"]["n_points"] == bundle["transfer_skill"]["n_points"]


# ── producer-to-claim equality (4) ───────────────────────────────────────────────
def test_pv03_claim_regenerates_from_producer():
    claim = next(c for c in PUBLIC_CLAIMS if c.claim_id == "PV-03")
    assert claim.validate() == []                      # structural guardrails clean
    regen = claim.producer.compute()                   # reads the packaged snapshot
    for k, v in claim.numeric_result.items():
        assert regen[k] == v, f"PV-03 {k}: claim {v} != producer {regen[k]}"
    assert claim.producer.slow is False


def test_pv03_values_returns_snapshot_values(snap):
    assert FV.pv03_values() == snap["values"]


# ── static site: no hand-typed numbers, no external deps, security (5,16,17,18) ───
def _strip_comments(text: str) -> str:
    """Remove JS/CSS block comments, JS line comments, and HTML comments (so the scans check CODE,
    not documentation that legitimately names the forbidden constructs)."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)      # /* ... */
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)     # <!-- ... -->
    text = re.sub(r"(?m)//[^\n]*", " ", text)               # // ...
    return text


def _site_code():
    return "\n".join(_strip_comments((SITE / n).read_text(encoding="utf-8"))
                     for n in ("index.html", "app.js", "styles.css"))


def test_site_number_audit_passes():
    # every science-looking decimal in app.js/index.html is present in the generated data
    assert FV._site_number_audit(SITE, json.loads(SNAPSHOT.read_text())) == []


def test_site_has_no_external_dependencies():
    text = _site_code()
    for pat in ("cdn", "googleapis", "unpkg", "jsdelivr", 'http-equiv="refresh"'):
        assert pat not in text.lower()
    # the only external URLs are the two Colab notebooks + the repo + the SVG namespace
    urls = re.findall(r"https?://[^\s\"'<>)]+", text)
    for u in urls:
        assert ("colab.research.google.com" in u or "github.com/trbrewer/puckworks" in u
                or "w3.org/2000/svg" in u), f"unexpected external URL: {u}"


def test_site_has_no_tracking_or_unsafe_js():
    low = _site_code().lower()
    for bad in ("analytics", "gtag(", "eval(", "new function(", ".innerhtml", "localstorage",
                "document.cookie", 'fetch("http', "importscripts"):
        assert bad not in low, f"site contains forbidden construct: {bad}"


def test_site_has_strict_csp_and_viewport():
    idx = (SITE / "index.html").read_text(encoding="utf-8")
    assert "Content-Security-Policy" in idx and "default-src 'none'" in idx
    assert "script-src 'self'" in idx and "connect-src 'self'" in idx
    assert 'name="viewport"' in idx and "width=device-width" in idx


# ── corrected story / no stale claims (14,15) ────────────────────────────────────
def test_site_has_no_superseded_transfer_failure_story():
    text = "\n".join((SITE / n).read_text(encoding="utf-8")
                     for n in ("index.html", "app.js", "styles.css"))
    for bad in ("25–49", "25-49", "did not transfer across grind", "reveals the transfer failure",
                "change grind", "We got a great result"):
        assert bad not in text, f"site contains superseded claim: {bad}"


def test_site_has_what_this_does_not_prove_and_scope():
    idx = (SITE / "index.html").read_text(encoding="utf-8").lower()
    assert "what this does not prove" in idx
    assert "not mechanistic validation" in idx or "not evidence that the mechanism" in idx
    assert "in-sample verification" in idx


# ── accessibility (19,20,21,22,23) ───────────────────────────────────────────────
def test_accessibility_controls_labels_and_static_equivalents():
    idx = (SITE / "index.html").read_text(encoding="utf-8")
    assert 'type="range"' in idx and 'type="radio"' in idx           # native keyboard controls
    assert idx.count("<label") >= 2 and "aria-live" in idx           # labels + live region
    assert "no-js-only" in idx and "static-summary.txt" in idx       # JS-off static equivalent
    assert (SITE / "static-summary.txt").exists() and (SITE / "static-summary.png").exists()
    assert 'alt="' in idx                                            # image alt text
    app = (SITE / "app.js").read_text(encoding="utf-8")
    assert "prefers-reduced-motion" in app                           # reduced-motion respected
    assert "aria-label" in app                                       # SVG plots labelled
    css = (SITE / "styles.css").read_text(encoding="utf-8")
    assert "focus-visible" in css                                    # visible keyboard focus


def test_landing_page_has_three_public_paths():
    land = (_ROOT / "docs" / "public" / "site" / "index.html").read_text(encoding="utf-8")
    assert "guided_espresso_pull_colab.ipynb" in land
    assert "puckworks_quickstart_colab.ipynb" in land
    assert 'href="flat-valley/"' in land


# ── generated site contains only intended files (24) ─────────────────────────────
def test_site_directory_only_intended_files():
    intended = {"index.html", "app.js", "styles.css", "data.json", "static-summary.png",
                "static-summary.txt"}
    present = {p.name for p in SITE.iterdir() if p.is_file()}
    assert present == intended, f"unexpected site files: {present ^ intended}"
