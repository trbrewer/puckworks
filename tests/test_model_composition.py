"""PV-05 "More Physics Made It Worse" — data-contract + static-site tests (Sections 5-9).

Offline. The quick lane runs the FAST producers (kappa_t_ladder / degeneracy_rmse /
composition_residual / simulate) and verifies the committed snapshot + static site. Every headline
number must trace to a producer — no hand-typed numbers in the HTML or JavaScript. The story rejects
ONE tested composition; the tests guard against it ever reading as a universal claim.
"""
import json
import re
import threading
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from puckworks.public import model_composition as MC
from puckworks.public.claims import PUBLIC_CLAIMS

_ROOT = Path(__file__).resolve().parents[1]
SITE = _ROOT / "docs" / "public" / "site" / "model-composition"
SNAPSHOT = _ROOT / "puckworks" / "public" / "data" / "pv05_model_composition.json"


@pytest.fixture(scope="module")
def snap():
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


# ── data contract: schema / units / provenance (9,10,11,12) ──────────────────────
def test_snapshot_has_required_schema(snap):
    for f in ("schema_version", "story_id", "title", "generator", "producers", "source_commit",
              "source_data_sha256", "dataset_manifest_ids", "source_ids", "attribution",
              "redistribution_class", "models", "model_params", "badge", "evidence_strength",
              "time_axis_s", "values", "units", "series", "composition_checklist", "scope",
              "caveat", "fidelity_ceiling"):
        assert f in snap, f"missing {f}"
    assert snap["story_id"] == "PV-05"
    assert snap["badge"] == "EXPLORATORY_SIMULATION"
    assert snap["evidence_strength"] in ("qualitative", "negative validation")


def test_every_value_has_a_unit_and_is_finite(snap):
    for k, v in snap["values"].items():
        assert k in snap["units"] and str(snap["units"][k]).strip(), f"{k} has no unit"
        assert MC._all_finite(v), f"{k} non-finite"


def test_no_non_finite_in_json():
    js = SNAPSHOT.read_text(encoding="utf-8")
    assert not re.search(r"\bNaN\b|\bInfinity\b", js)


def test_every_series_has_a_role_unit_and_finite_values(snap):
    n = len(snap["time_axis_s"])
    roles = set()
    for s in snap["series"]:
        for key in ("label", "values", "unit", "role", "component", "method", "caveat"):
            assert s.get(key) not in (None, ""), f"series missing {key}"
        assert s["role"] in ("observed", "benchmark", "simulated", "derived")
        assert MC._all_finite(s["values"]) and len(s["values"]) == n
        roles.add(s["role"])
    assert {"observed", "simulated", "benchmark"} <= roles     # distinct series kinds present


def test_attribution_and_redistribution_rights(snap):
    # the ONE redistributed observation (the trace) is CC-BY and attributed with its Zenodo DOI
    assert "CC-BY" in snap["redistribution_class"] or "CC-BY" in snap["attribution"]
    assert "10.5281/zenodo.18046315" in snap["attribution"]
    assert "waszkiewicz2025/traces_time_dependent" in snap["dataset_manifest_ids"]
    obs = [s for s in snap["series"] if s["role"] == "observed"]
    assert obs and any("CC-BY" in s["caveat"] for s in obs)
    # the paywalled swelling source is only shown as derived model output, never redistributed raw
    assert "paywalled" in snap["attribution"].lower() or "paywalled" in json.dumps(snap["source_ids"]).lower()


def test_dataset_ids_exist_in_manifest(snap):
    ids = set()
    with open(_ROOT / "puckworks" / "data" / "MANIFEST.csv", newline="", encoding="utf-8") as f:
        import csv
        for row in csv.DictReader(f):
            ids.add(row["dataset_id"])
    for did in snap["dataset_manifest_ids"]:
        assert did in ids, f"dataset '{did}' not in MANIFEST.csv"


# ── deterministic, producer-bound transform (1,2) ────────────────────────────────
def test_transform_is_deterministic_and_matches_snapshot():
    a = MC._canonical_json(MC.build_payload(source_commit="x"))
    b = MC._canonical_json(MC.build_payload(source_commit="x"))
    assert a == b
    stored = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    fresh = MC.build_payload(source_commit=stored["source_commit"])
    assert MC._canonical_json(fresh) == SNAPSHOT.read_text(encoding="utf-8"), "snapshot stale (run export)"


def test_source_data_sha_binds(snap):
    # the snapshot records the live hash of each canonical source file; a drift is detectable
    for name, path in MC._SOURCE_DATA_FILES.items():
        assert snap["source_data_sha256"][name] == MC._sha256_file(path)


def test_verify_clean_on_committed_state():
    assert MC.verify() == []


# ── producer cross-checks (3,4,5,6,7) ────────────────────────────────────────────
def test_producers_agree_and_comparison_facts_hold(snap):
    from puckworks import harness
    from puckworks.models.brewer2026 import coupled_kappa_t as ck
    ladder = harness.kappa_t_ladder(window=MC.WINDOW)
    deg = float(ck.degeneracy_rmse(P_bar=MC.P_BAR, window=MC.WINDOW))
    comp = ck.composition_residual(P_bar=MC.P_BAR, powder=MC.POWDER, window=MC.WINDOW)
    v = snap["values"]

    # (3) the four producers agree where they describe the same model/window
    assert abs(round(deg, 3) - ladder["rung4_phi_of_t"]) <= 1e-3          # extraction-only == rung4
    assert v["extraction_only_rmse_g_per_s"] == ladder["rung4_phi_of_t"]
    assert v["extraction_only_rmse_degeneracy_g_per_s"] == round(deg, 3)
    assert v["degeneracy_agreement_g_per_s"] <= 1e-3
    assert round(comp["rmse"], 3) == v["composite_rmse_g_per_s"]
    assert round(comp["eps_min_reached"], 4) == v["min_shared_porosity"]

    # (4,5,6) the load-bearing comparison: extraction < constant < composite
    assert v["extraction_only_rmse_g_per_s"] < v["const_baseline_rmse_g_per_s"]
    assert v["composite_rmse_g_per_s"] > v["extraction_only_rmse_g_per_s"]
    assert v["composite_rmse_g_per_s"] > v["const_baseline_rmse_g_per_s"]

    # (7) closure/clamping state reported exactly as the producer returns it
    assert v["swelling_closes_shared_state"] == bool(comp["swelling_closes"])
    assert v["composite_clamped"] == bool(comp["clamped"])
    assert v["min_shared_porosity"] < v["eps0_reference_porosity"]        # over-closure


def test_verify_flags_a_broken_composition(tmp_path, monkeypatch, snap):
    # if the composite ever stopped scoring worse than the constant, verify must fail on the fact
    bad = json.loads(json.dumps(snap))
    bad["values"]["composite_rmse_g_per_s"] = 0.01           # pretend the composite "got good"
    snap_file = tmp_path / "pv05.json"
    snap_file.write_text(MC._canonical_json(bad), encoding="utf-8")
    monkeypatch.setattr(MC, "SNAPSHOT", snap_file)
    monkeypatch.setattr(MC, "build_payload", lambda source_commit=None: bad)
    problems = MC.verify(out_dir=tmp_path)                   # empty out_dir -> site checks skip
    assert any("composite RMSE is not above the constant baseline" in p for p in problems)


# ── producer-to-claim equality (2) ───────────────────────────────────────────────
def test_pv05_claim_regenerates_from_fast_producer():
    claim = next(c for c in PUBLIC_CLAIMS if c.claim_id == "PV-05")
    assert claim.validate() == []
    assert claim.producer.slow is False
    assert claim.producer.ref() == "puckworks.public.model_composition.pv05_values"
    regen = claim.producer.compute()
    for k, val in claim.numeric_result.items():
        assert regen[k] == val, f"PV-05 {k}: claim {val} != producer {regen[k]}"


def test_pv05_values_returns_snapshot_values(snap):
    assert MC.pv05_values() == snap["values"]


# ── static site: no hand-typed numbers, security, no external deps (8,21,22,23) ───
def _strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"(?m)//[^\n]*", " ", text)
    return text


def _site_code():
    return "\n".join(_strip_comments((SITE / n).read_text(encoding="utf-8"))
                     for n in ("index.html", "app.js", "styles.css"))


def test_site_number_audit_passes():
    assert MC._site_number_audit(SITE, json.loads(SNAPSHOT.read_text())) == []


def test_site_has_no_external_dependencies():
    text = _site_code()
    for pat in ("cdn", "googleapis", "unpkg", "jsdelivr", 'http-equiv="refresh"'):
        assert pat not in text.lower()
    for u in re.findall(r"https?://[^\s\"'<>)]+", text):
        assert "github.com/trbrewer/puckworks" in u or "w3.org/2000/svg" in u, f"external URL: {u}"


def test_site_has_no_tracking_or_unsafe_js():
    low = _site_code().lower()
    for bad in ("analytics", "gtag(", "eval(", "new function(", ".innerhtml", "localstorage",
                "document.cookie", 'fetch("http', "importscripts", "sessionstorage"):
        assert bad not in low, f"site contains forbidden construct: {bad}"


def test_site_has_strict_csp_and_viewport():
    idx = (SITE / "index.html").read_text(encoding="utf-8")
    assert "Content-Security-Policy" in idx and "default-src 'none'" in idx
    assert "script-src 'self'" in idx and "connect-src 'self'" in idx
    assert 'name="viewport"' in idx and "width=device-width" in idx


# ── the story stays honest: no universal / disproof / validation claims (17,18,19,20) ─
def test_no_universal_or_overclaimed_wording():
    text = "\n".join((SITE / n).read_text(encoding="utf-8") for n in ("index.html", "static-summary.txt"))
    low = text.lower()
    for bad in ("physics makes models worse", "swelling is wrong", "the simpler model is true",
                "prove swelling does not occur", "more physics is always", "more physics is worse"):
        assert bad not in low, f"overclaimed wording present: {bad}"
    # "validated composition" may appear ONLY as an explicit disclaimer (never/not a ...)
    for m in re.finditer(r"(\w+\s+){0,2}validated composition", low):
        assert "never" in m.group(0) or "not" in m.group(0), f"un-negated: {m.group(0)!r}"
    # the qualifying language IS present
    assert "not swelling physics in general" in low or "not swelling in general" in low
    assert "rejects this composition" in low or "rejects one tested composition" in low


def test_site_states_what_it_does_not_prove_and_no_guided_pull_coupling():
    idx = (SITE / "index.html").read_text(encoding="utf-8").lower()
    assert "what this does not prove" in idx
    assert "in-sample verification" in idx or "not independent validation" in idx
    assert "guided espresso pull" in idx and "not" in idx        # explicitly not coupled


# ── accessibility (24,25,26,27,28) ───────────────────────────────────────────────
def test_accessibility_controls_labels_and_static_equivalents():
    idx = (SITE / "index.html").read_text(encoding="utf-8")
    assert 'type="radio"' in idx and 'type="checkbox"' in idx      # native keyboard controls (no slider)
    assert idx.count("<label") >= 3 and "aria-live" in idx
    assert "no-js-only" in idx and "static-summary.txt" in idx     # JS-off static equivalent
    assert 'name="viewport"' in idx and "width=device-width" in idx   # (27) mobile viewport
    assert (SITE / "static-summary.txt").exists() and (SITE / "static-summary.png").exists()  # (25)
    alts = re.findall(r'alt="([^"]*)"', idx)                        # (28) meaningful alt text
    assert alts and all(len(a.strip()) >= 15 for a in alts)
    app = (SITE / "app.js").read_text(encoding="utf-8")
    assert "aria-label" in app                                     # SVG plots labelled
    assert "createtextnode" in app.lower() and ".innerhtml" not in app.lower()  # safe DOM
    css = (SITE / "styles.css").read_text(encoding="utf-8")
    assert "focus-visible" in css                                  # (24) visible keyboard focus
    assert "prefers-reduced-motion" in css                         # (26) reduced-motion support


def test_landing_page_links_model_composition_without_displacing_primary_paths():
    land = (_ROOT / "docs" / "public" / "site" / "index.html").read_text(encoding="utf-8")
    # the three primary paths remain
    assert "guided_espresso_pull_colab.ipynb" in land
    assert "puckworks_quickstart_colab.ipynb" in land
    assert 'href="flat-valley/"' in land
    # plus the new model-composition card
    assert 'href="model-composition/"' in land


# ── packaging: exact snapshot path, no broad wildcard (14,15,16) ──────────────────
def test_packaging_declares_exact_snapshot_no_wildcard():
    pj = (_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r'"puckworks\.public"\s*=\s*\[([^\]]*)\]', pj)
    assert m, "no puckworks.public package-data entry"
    entry = m.group(1)
    assert "data/pv05_model_composition.json" in entry
    assert "*.json" not in entry, "must not use a broad wildcard under puckworks.public"


def test_site_directory_only_intended_files():
    intended = {"index.html", "app.js", "styles.css", "data.json", "static-summary.png",
                "static-summary.txt"}
    present = {p.name for p in SITE.iterdir() if p.is_file()}
    assert present == intended, f"unexpected site files: {present ^ intended}"
    # no raw source data (e.g. a copied CSV) leaked into the deployed site
    assert not any(p.suffix == ".csv" for p in SITE.iterdir())


# ── local HTTP-server smoke: every site file serves 200 (29) ─────────────────────
def test_local_http_server_serves_all_site_files():
    handler = partial(SimpleHTTPRequestHandler, directory=str(SITE))
    srv = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = srv.server_address[1]
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    try:
        for name in ("index.html", "app.js", "styles.css", "data.json", "static-summary.txt",
                     "static-summary.png"):
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/{name}", timeout=5) as r:
                assert r.status == 200, f"{name} -> {r.status}"
                assert r.read(1)                                    # non-empty body
    finally:
        srv.shutdown()
        th.join(timeout=5)
