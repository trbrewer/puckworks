"""PV-04 "How We Falsified Our Own Espresso Headline" — data-contract + static-site integrity tests.

Offline. Binds the compact public snapshot to the authoritative producer
(`result1_magnitude_comparison`) and to the CC-BY Schmieder source files, guards the corrected-analysis
facts (so a silent regression to the superseded interior-maximum headline fails the suite), and treats
the deployed static site as an integrity boundary: no hand-typed science, strict CSP, safe DOM, native
accessible controls, and honest copy that never over-claims. Mirrors the PV-05 test pattern.

The producer `result1_magnitude_comparison` does real model work; it is computed ONCE per module.
"""
import csv
import json
import math
import re
import threading
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from puckworks.public import analysis_autopsy as AA
from puckworks.public.claims import PUBLIC_CLAIMS

_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = _ROOT / "puckworks" / "public" / "data" / "pv04_analysis_autopsy.json"
SITE = _ROOT / "docs" / "public" / "site" / "analysis-autopsy"
SITE_FILES = ("index.html", "app.js", "styles.css", "data.json", "static-summary.txt",
              "static-summary.png")


@pytest.fixture(scope="module")
def snap():
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def producer():
    from puckworks import harness
    return harness.result1_magnitude_comparison()


def _obs(snap):
    return next(s for s in snap["series"] if s["role"] == "observed")


def _derived(snap):
    return next(s for s in snap["series"] if s["role"] == "derived")


def _model(snap):
    return next(s for s in snap["series"] if s["role"] == "simulated")


def _site_text():
    return "\n".join((SITE / n).read_text(encoding="utf-8")
                     for n in ("index.html", "static-summary.txt"))


def _strip_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"(?m)//[^\n]*", " ", text)
    return text


def _site_code():
    return "\n".join(_strip_comments((SITE / n).read_text(encoding="utf-8"))
                     for n in ("index.html", "app.js", "styles.css"))


def _negated_only(text, phrase):
    """Every occurrence of `phrase` sits in a sentence that also carries a negation."""
    low = text.lower()
    for m in re.finditer(re.escape(phrase), low):
        seg = low[max(0, m.start() - 140):m.end() + 60]
        assert any(w in seg for w in ("not", "no ", "never", "n't", "rules out", "does not")), \
            f"un-negated {phrase!r}: …{seg}…"


# ══════════════════════════════ DATA CONTRACT ══════════════════════════════
def test_snapshot_schema_and_version(snap):
    for f in ("schema_version", "story_id", "title", "generator", "producer", "source_commit",
              "source_data_sha256", "dataset_manifest_ids", "attribution", "redistribution_class",
              "badge", "evidence_strength", "values", "units", "series", "evidence_partitions",
              "revision_record", "scope", "caveat", "fidelity_ceiling"):
        assert f in snap, f"missing {f}"
    assert snap["story_id"] == "PV-04"
    assert snap["schema_version"] == 2 == AA.SCHEMA_VERSION
    assert snap["producer"] == "puckworks.harness.result1_magnitude_comparison"
    # global evidence labels carried UNCHANGED
    assert snap["badge"] == "OBSERVED"
    assert snap["evidence_strength"] == "independent"


def test_no_wall_clock_field(snap):
    for bad in ("timestamp", "generated_at", "datetime", "wall_clock", "date", "time_generated"):
        assert bad not in snap, f"snapshot carries a wall-clock field: {bad}"


def test_json_is_finite_no_nan_infinity():
    js = SNAPSHOT.read_text(encoding="utf-8")
    assert not re.search(r"\bNaN\b|\bInfinity\b|\b-Infinity\b", js)


def test_every_value_has_a_unit_and_is_finite(snap):
    for k, v in snap["values"].items():
        assert k in snap["units"] and str(snap["units"][k]).strip(), f"{k} has no unit"
        assert AA._all_finite(v), f"{k} non-finite"


def test_observed_series_has_actual_replicate_arrays(snap):
    o = _obs(snap)
    assert isinstance(o["replicates"], list) and len(o["replicates"]) == 3
    assert all(isinstance(c, list) and c for c in o["replicates"])
    assert len(o["cell_stds"]) == 3 and len(o["ns"]) == 3


def test_per_cell_ns_reproduce_from_producer(snap, producer):
    assert _obs(snap)["ns"] == list(producer["raw_tds_ey_ns"]) == [3, 6, 3]


def test_means_recompute_from_exposed_replicates(snap):
    o = _obs(snap)
    for i, cell in enumerate(o["replicates"]):
        recomputed = sum(cell) / len(cell)
        assert abs(recomputed - o["values"][i]) <= 1e-2, f"cell {i} mean mismatch"


def test_cell_sds_recompute_from_exposed_replicates(snap):
    # the producer computes the DESCRIPTIVE within-cell std (uncorrected, ddof=0 — see
    # schmieder_grind_response); the exposed cell_stds must recompute on that same basis
    o = _obs(snap)
    for i, cell in enumerate(o["replicates"]):
        mean = sum(cell) / len(cell)
        var = sum((x - mean) ** 2 for x in cell) / len(cell)          # ddof=0 (descriptive)
        assert abs(math.sqrt(var) - o["cell_stds"][i]) <= 2e-2, f"cell {i} SD mismatch"


def test_descriptive_mean_sd_recomputes_from_cell_sds(snap):
    o = _obs(snap)
    mean_sd = sum(o["cell_stds"]) / len(o["cell_stds"])
    assert abs(mean_sd - snap["values"]["mean_within_cell_std_EYpt"]) <= 2e-3
    # the descriptive mean SD equals the compatibility alias exactly
    assert snap["values"]["mean_within_cell_std_EYpt"] == snap["values"]["within_cell_std_EYpt"]


def test_source_data_sha_binds(snap):
    for name, path in AA._SOURCE_DATA_FILES.items():
        assert snap["source_data_sha256"][name] == AA._sha256_file(path)


def test_dataset_ids_exist_in_manifest(snap):
    ids = set()
    with open(_ROOT / "puckworks" / "data" / "MANIFEST.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ids.add(row["dataset_id"])
    for did in snap["dataset_manifest_ids"]:
        assert did in ids, f"dataset '{did}' not in MANIFEST.csv"


def test_attribution_is_cc_by_and_no_raw_csv_redistributed(snap):
    assert "CC-BY" in snap["attribution"]
    assert "10.3390/foods12152871" in snap["attribution"]
    for did in snap["dataset_manifest_ids"]:
        assert did.startswith("schmieder2023/")
    # the redistribution class distinguishes DERIVED replicate-level values from the source CSV
    rc = snap["redistribution_class"].lower()
    assert "derived" in rc and ("no raw" in rc and "csv" in rc)


def test_deterministic_and_matches_snapshot():
    a = AA._canonical_json(AA.build_payload(source_commit="x"))
    b = AA._canonical_json(AA.build_payload(source_commit="x"))
    assert a == b
    stored = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    fresh = AA.build_payload(source_commit=stored["source_commit"])
    assert AA._canonical_json(fresh) == SNAPSHOT.read_text(encoding="utf-8"), "snapshot stale (run export)"


def test_verify_clean_on_committed_state():
    assert AA.verify() == []


def test_site_data_is_byte_identical_to_snapshot():
    assert (SITE / "data.json").read_bytes() == SNAPSHOT.read_bytes()


# ══════════════════════════════ SCIENTIFIC CROSS-CHECKS ══════════════════════════════
def test_all_values_trace_to_the_authoritative_producer(snap, producer):
    for key, path in AA._VALUE_PATHS.items():
        live = AA._dig(producer, path)
        want = snap["values"][key]
        if isinstance(want, bool):
            assert bool(live) == want, f"{key}: {live} != {want}"
        else:
            assert abs(float(live) - float(want)) <= 5e-3, f"{key}: {live} != {want}"


def test_contrast_operation_is_dial_1p7_minus_dial_2p0(snap):
    # the CANONICAL operation: middle (dial 1.7) mean minus coarse (dial 2.0) mean
    o = _obs(snap)
    mid = sum(o["replicates"][1]) / len(o["replicates"][1])
    coarse = sum(o["replicates"][2]) / len(o["replicates"][2])
    assert abs((mid - coarse) - snap["values"]["mid_vs_coarse_contrast_EYpt"]) <= 1e-2


def test_canonical_and_compat_contrast_keys_agree(producer):
    assert producer["raw_mid_vs_coarse_contrast_EYpt"] == producer["raw_mid_vs_endpoint_contrast_EYpt"]
    assert producer["raw_mean_within_cell_std_EYpt"] == producer["raw_within_cell_std_EYpt"]


def test_contrast_and_interval_values(snap):
    v = snap["values"]
    assert abs(v["mid_vs_coarse_contrast_EYpt"] - (-0.241)) <= 1e-3
    assert v["welch_ci95_lo_EYpt"] < 0 and v["welch_ci95_hi_EYpt"] < 0    # interval excludes zero
    assert abs(v["welch_ci95_lo_EYpt"] - (-0.422)) <= 1e-3
    assert abs(v["welch_ci95_hi_EYpt"] - (-0.06)) <= 1e-3


def test_observed_middle_below_coarse_no_interior_max(snap):
    v = snap["values"]
    assert v["ey_dial_1p7_pct"] < v["ey_dial_2p0_pct"]              # middle below coarse
    assert not (v["ey_dial_1p7_pct"] > v["ey_dial_1p4_pct"]
                and v["ey_dial_1p7_pct"] > v["ey_dial_2p0_pct"])    # no interior maximum


def test_ordered_not_statistically_monotone_wording():
    _negated_only(_site_text(), "statistically monotone")


def test_model_bumps_reproduce_and_are_below_descriptive_spread(snap, producer):
    v = snap["values"]
    assert abs(v["model_prominence_5bar_EYpt"] - producer["model_prominence_5bar_EYpt"]) <= 5e-3
    assert abs(v["model_prominence_9bar_EYpt"] - producer["model_prominence_9bar_EYpt"]) <= 5e-3
    assert v["model_bump_lt_within_cell_var"] is True
    assert max(v["model_prominence_5bar_EYpt"], v["model_prominence_9bar_EYpt"]) \
        < v["mean_within_cell_std_EYpt"]


def test_no_formal_noise_floor_or_mde_claim():
    text = _site_text()
    _negated_only(text, "noise floor")
    _negated_only(text, "minimum-detectable-effect")
    _negated_only(text, "minimum detectable effect")


def test_rsm_predictions_reproduce_and_never_labelled_a_coefficient(snap, producer):
    v = snap["values"]
    assert abs(v["rsm_printed_central_g"] - producer["rsm_printed_central_g"]) <= 5e-3
    assert abs(v["rsm_refit_central_g"] - producer["rsm_refit_central_g"]) <= 5e-3
    assert abs(v["rsm_raw_central_g"] - producer["rsm_raw_central_g"]) <= 5e-3
    # the ~6.723 g value is a prediction from rounded coefficients, never itself "a coefficient"
    hay = (_site_text() + "\n" + SNAPSHOT.read_text(encoding="utf-8")).lower()
    for bad in ("6.723 g coefficient", "central coefficient = 6.723", "printed coefficient 6.723",
                "coefficient = 6.723", "6.723 g rsm coefficient"):
        assert bad not in hay, f"6.723 g labelled a coefficient: {bad}"
    assert "rounded published coefficients" in hay          # the correct framing IS present


# ══════════════════════════════ EVIDENCE PARTITIONS ══════════════════════════════
def test_per_series_evidence_partitions(snap):
    o, dr, mo = _obs(snap), _derived(snap), _model(snap)
    assert (o["badge"], o["strength"]) == ("OBSERVED", "independent")
    assert (dr["badge"], dr["strength"]) == ("RECONSTRUCTED", "verification")  # a computational audit
    assert (mo["badge"], mo["strength"]) == ("EXPLORATORY_SIMULATION", "qualitative")
    assert dr["strength"] != "independent"           # the audit is NOT independent experimental proof


def test_evidence_partitions_named_and_superseded_has_no_badge(snap):
    parts = {ep["partition"]: ep for ep in snap["evidence_partitions"]}
    for need in ("corrected_replicate_data", "rounded_coefficient_and_refit_audit",
                 "model_interior_feature", "superseded_headline"):
        assert need in parts
    sup = parts["superseded_headline"]
    assert sup.get("badge") in (None, "")            # superseded claim carries no current badge
    assert "superseded" in str(sup.get("status", "")).lower()


def test_global_evidence_does_not_overwrite_per_series(snap):
    # the global badge is OBSERVED, but the simulated/derived series keep their own labels
    assert snap["badge"] == "OBSERVED"
    assert _model(snap)["badge"] == "EXPLORATORY_SIMULATION"
    assert _derived(snap)["badge"] == "RECONSTRUCTED"


def test_fidelity_ceiling_states_capacity_not_identification(snap):
    fc = snap["fidelity_ceiling"].lower()
    assert "capacity" in fc and "identification" in fc


# ══════════════════════════════ PUBLICCLAIM ══════════════════════════════
def test_pv04_claim_uses_snapshot_producer_and_regenerates():
    c = next(c for c in PUBLIC_CLAIMS if c.claim_id == "PV-04")
    assert c.validate() == []
    assert c.producer.ref() == "puckworks.public.analysis_autopsy.pv04_values"
    assert c.producer.slow is False
    assert c.reproduction == "python -m puckworks.public.analysis_autopsy verify"
    regen = c.producer.compute()
    for k, val in c.numeric_result.items():
        assert regen[k] == val, f"PV-04 {k}: claim {val} != producer {regen[k]}"


def test_pv04_claim_stays_dial_scoped_and_only_observed_values():
    c = next(c for c in PUBLIC_CLAIMS if c.claim_id == "PV-04")
    assert c.compares_grinder_dials is True
    cav = c.primary_caveat.lower()
    assert any(w in cav for w in ("non-portable", "not portable", "adapter", "calibrat"))
    # the claim's numeric_result never silently carries the SIMULATED model or DERIVED RSM values
    for forbidden in ("model_prominence_5bar_EYpt", "model_prominence_9bar_EYpt",
                      "rsm_printed_central_g", "rsm_refit_central_g"):
        assert forbidden not in c.numeric_result, f"{forbidden} must not ride the OBSERVED claim"


def test_pv04_values_returns_snapshot_values(snap):
    assert AA.pv04_values() == snap["values"]


# ══════════════════════════════ NO HAND-TYPED SCIENCE ══════════════════════════════
def test_site_number_audit_passes(snap):
    assert AA._site_number_audit(SITE, snap) == []


def test_static_summary_txt_derives_from_payload(snap):
    assert (SITE / "static-summary.txt").read_text(encoding="utf-8") == AA._static_summary_text(snap)


def test_static_summary_png_derives_from_payload_and_is_deterministic(snap):
    png = (SITE / "static-summary.png").read_bytes()
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert png == AA._static_summary_png(snap)               # regenerates byte-identically


# ══════════════════════════════ SECURITY ══════════════════════════════
def test_site_has_no_external_dependencies():
    text = _site_code()
    for pat in ("cdn", "googleapis", "unpkg", "jsdelivr", 'http-equiv="refresh"'):
        assert pat not in text.lower()
    for u in re.findall(r"https?://[^\s\"'<>)]+", text):
        assert "github.com/trbrewer/puckworks" in u or "w3.org/2000/svg" in u, f"external URL: {u}"


def test_site_has_no_tracking_storage_or_unsafe_js():
    low = _site_code().lower()
    for bad in ("analytics", "gtag(", "eval(", "new function(", ".innerhtml", "localstorage",
                "sessionstorage", "document.cookie", 'fetch("http', "importscripts",
                "service worker", "navigator.sendbeacon"):
        assert bad not in low, f"forbidden construct: {bad}"


def test_site_has_strict_csp_and_viewport():
    idx = (SITE / "index.html").read_text(encoding="utf-8")
    assert "Content-Security-Policy" in idx and "default-src 'none'" in idx
    assert "script-src 'self'" in idx and "style-src 'self'" in idx
    assert "connect-src 'self'" in idx and "img-src 'self' data:" in idx
    assert 'name="viewport"' in idx and "width=device-width" in idx


def test_app_uses_safe_dom_and_local_data_source():
    app = (SITE / "app.js").read_text(encoding="utf-8")
    assert "createTextNode" in app and "createElementNS" in app
    assert ".innerHTML" not in app
    assert 'fetch("data.json"' in app                 # same-origin, relative


def test_data_fields_have_no_executable_content(snap):
    blob = SNAPSHOT.read_text(encoding="utf-8").lower()
    for bad in ("<script", "javascript:", "onerror=", "onload=", "function(", "=>"):
        assert bad not in blob, f"executable-looking content in data: {bad}"


# ══════════════════════════════ ACCESSIBILITY ══════════════════════════════
def test_native_controls_labels_and_static_equivalents():
    idx = (SITE / "index.html").read_text(encoding="utf-8")
    assert idx.count('type="radio"') >= 4              # four scenes via native radios
    assert 'type="checkbox"' in idx                    # optional native overlays
    assert idx.count("<label") >= 4 and "aria-live" in idx
    assert "no-js-only" in idx and "static-summary.txt" in idx and "static-summary.png" in idx
    assert (SITE / "static-summary.txt").exists() and (SITE / "static-summary.png").exists()
    alts = re.findall(r'alt="([^"]*)"', idx)
    assert alts and all(len(a.strip()) >= 15 for a in alts)


def test_svg_labelled_and_tables_present():
    app = (SITE / "app.js").read_text(encoding="utf-8")
    assert 'setAttribute("role", "img")' in app and "aria-label" in app
    idx = (SITE / "index.html").read_text(encoding="utf-8")
    assert idx.count("text table") >= 3                # a text table for every plotted view


def test_css_focus_visible_reduced_motion_and_dark_mode():
    css = (SITE / "styles.css").read_text(encoding="utf-8")
    assert "focus-visible" in css
    assert "prefers-reduced-motion" in css
    assert "prefers-color-scheme: dark" in css


def test_landing_page_links_analysis_autopsy_without_displacing_primary_paths():
    land = (_ROOT / "docs" / "public" / "site" / "index.html").read_text(encoding="utf-8")
    assert 'href="analysis-autopsy/"' in land
    # the existing primary paths remain
    assert "guided_espresso_pull_colab.ipynb" in land
    assert "puckworks_quickstart_colab.ipynb" in land
    assert 'href="flat-valley/"' in land
    assert 'href="model-composition/"' in land


# ══════════════════════════════ PACKAGING ══════════════════════════════
def test_packaging_declares_exact_snapshot_no_wildcard():
    pj = (_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r'"puckworks\.public"\s*=\s*\[([^\]]*)\]', pj)
    assert m, "no puckworks.public package-data entry"
    entry = m.group(1)
    assert "data/pv04_analysis_autopsy.json" in entry
    assert "*.json" not in entry, "must not use a broad wildcard under puckworks.public"
    # no site asset is declared as package data
    for bad in ("analysis-autopsy", "index.html", "app.js", "styles.css", "static-summary"):
        assert bad not in entry


def test_site_directory_only_intended_files():
    present = {p.name for p in SITE.iterdir() if p.is_file()}
    assert present == set(SITE_FILES), f"unexpected site files: {present ^ set(SITE_FILES)}"
    assert not any(p.suffix == ".csv" for p in SITE.iterdir())    # no copied source CSV


def test_pv04_values_reads_the_packaged_snapshot():
    # the runtime producer reads the packaged snapshot path (works from an installed wheel)
    assert AA.SNAPSHOT == _ROOT / "puckworks" / "public" / "data" / "pv04_analysis_autopsy.json"
    assert AA.pv04_values() == json.loads(AA.SNAPSHOT.read_text(encoding="utf-8"))["values"]


# ══════════════════════════════ SERVING ══════════════════════════════
def test_local_http_server_serves_all_site_files():
    handler = partial(SimpleHTTPRequestHandler, directory=str(SITE))
    srv = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = srv.server_address[1]
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    try:
        for name in SITE_FILES:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/{name}", timeout=5) as r:
                assert r.status == 200, f"{name} -> {r.status}"
                assert r.read(1)
    finally:
        srv.shutdown()
        th.join(timeout=5)


# ══════════════════════════════ HONEST COPY ══════════════════════════════
def test_no_material_overclaims_in_site():
    text = _site_text()
    low = text.lower()
    # phrases that must be ABSENT entirely — no honest use, even negated
    for bad in ("fine-grind dip is fake", "channeling caused the bump", "channeling caused it",
                "universal optimum", "dial equals particle size", "dial is a particle size",
                "6.723 g coefficient", "highest-minus-middle", "higher-minus-middle",
                "swelling is harmful", "the simpler model is true"):
        assert bad not in low, f"overclaimed / forbidden wording present: {bad}"
    # claims that are only acceptable as an explicit disclaimer (must be negated where they appear)
    _negated_only(text, "too-fine optimum")
    _negated_only(text, "channeling is disproved")
    _negated_only(text, "channeling was disproved")
    _negated_only(text, "self-correction proves")
    _negated_only(text, "reversal is 'fake'")
    # the honest framing IS present
    assert "model capacity is not parameter identification" in low or \
           "capacity, not identification" in low or "not identification" in low
    assert "middle-minus-coarse" in low or "dial 1.7 − dial 2.0" in low or "dial 1.7 - dial 2.0" in low


def test_no_humiliation_or_blame_framing():
    low = _site_text().lower()
    for bad in ("authors were wrong", "authors erred", "the authors' error", "blame the authors",
                "authors got it wrong", "humiliat"):
        assert bad not in low, f"humiliation/blame framing present: {bad}"
    # explicitly frames the revision as the project correcting itself
    assert "correcting its own" in low or "our own" in low
