"""Paper 2 review item 4.13 — every manuscript number is accounted for.

`verify` answers "are the numbers we chose to check correct?". Before this, 18 claims covered a
manuscript whose body holds ~390 numerals, so most results were unregistered — and an unregistered
number is an unchecked number that looks exactly like a checked one. The audit forces each numeral
into a disposition and reports whatever is left.

These tests hold the audit to the standard that makes it worth having: it must be able to FAIL.
"""
import pytest

from puckworks.paper_b2 import build as B
from puckworks.paper_b2 import claim_coverage as C


@pytest.fixture(scope="module")
def report():
    return C.audit()


def _inject(sentence: str) -> str:
    """Put a sentence in the audited BODY.

    The body ends at the EARLIEST skipped section, not at `## References` — the figure-spec and
    supplementary-plan sections come first. Injecting after that boundary would place the fault
    where the audit deliberately does not look, and the test would pass for the wrong reason.
    """
    src = C.MANUSCRIPT.read_text(encoding="utf-8")
    cut = min((src.index(m) for m in C._SKIP_SECTIONS if m in src), default=len(src))
    assert cut < len(src), "no skipped section found — re-check the audit boundary"
    return src[:cut] + "\n\n" + sentence + "\n\n" + src[cut:]


def test_the_injection_helper_targets_the_audited_region():
    """Non-vacuity for the two fault-injection tests below: prove the sentence really lands inside
    the region `audit` reads, otherwise those tests certify nothing."""
    body = C._body(_inject("A marker sentence with 7.313131 in it."))
    assert "7.313131" in body


def test_nothing_in_the_manuscript_body_is_unaccounted(report):
    lines = [f"L{f['line']} {f['token']}  {f['context'][:90]}" for f in report["unaccounted"]]
    assert report["unaccounted"] == [], "unaccounted numerals:\n  " + "\n  ".join(lines)


def test_the_ratchet_matches_reality(report):
    """The committed baseline must equal the current count, or it is not a ratchet."""
    assert C.BASELINE_UNACCOUNTED == len(report["unaccounted"])


def test_the_audit_can_actually_fail(tmp_path, monkeypatch):
    """NON-VACUITY. An audit that cannot report a problem certifies nothing. Inject a number that
    no producer computes and confirm it is caught."""
    fake = tmp_path / "draft.md"
    fake.write_text(_inject("The reconstruction error is 7.313131 g s per second."),
                    encoding="utf-8")
    out = C.audit(fake)
    assert any(f["token"] == "7.313131" for f in out["unaccounted"]), (
        "an invented number passed the coverage audit")


def test_a_number_that_disagrees_with_its_producer_is_not_silently_accepted(tmp_path):
    """The subtler failure: a value CLOSE to a real claim but not equal to it. Rounding is allowed
    (0.116 for 0.1157); a different number is not."""
    fake = tmp_path / "draft.md"
    fake.write_text(_inject("The held-out spline reaches 0.4271 g s per second."),
                    encoding="utf-8")
    out = C.audit(fake)
    assert any(f["token"] == "0.4271" for f in out["unaccounted"])


def test_a_derived_quantity_that_stops_recomputing_is_reported(monkeypatch, tmp_path):
    """Derived ratios are RECOMPUTED, not waved through. If the underlying producers move so the
    ratio no longer matches the printed value, the audit must say so."""
    # Probe on 2.1 rather than 2.6: third review P0.1 re-based these descriptive ratios on the
    # honest other-four empirical-template RMSE (0.1864) instead of the leave-in dispersion
    # (0.1492), so 2.6/3.2 became 2.1/2.5 and `shot_level.noise_floor` no longer exists.
    monkeypatch.setattr(C, "DERIVED_QUANTITIES",
                        {**C.DERIVED_QUANTITIES,
                         "2.1": ("ratio",
                                 "shot_level.dispersion.other_four_template_rmse_g_per_s",
                                 "shot_level.dispersion.other_four_template_rmse_g_per_s")})
    out = C.audit()                      # that ratio is now 1.0, not 2.1
    assert any(f["token"] == "2.1" and "recomputes to" in f["why"] for f in out["unaccounted"])


def test_the_claim_map_grew_to_cover_the_tables_the_review_named(report):
    """4.13 asks specifically for Tables 2/3, block endpoints, residual diagnostics and
    robustness."""
    labels = " ".join(c[0] for c in B._CLAIMS).lower()
    for needle in ("table 2", "table 3", "per-pressure", "residual", "leave-one-shot-out",
                   "recorded-pressure", "block"):
        assert needle in labels, needle
    assert len(B._CLAIMS) > 100, len(B._CLAIMS)


def test_the_per_pressure_table_is_expanded_from_the_producer_not_hand_written():
    """33 hand-transcribed cells is how Table 3's rc3b column went stale in every row."""
    generated = B._per_pressure_claims()
    assert len(generated) >= 30, len(generated)
    for _label, path, _expected, _tol in generated:
        assert path.startswith("cross_pressure.per_pressure."), path


def test_dotted_keys_resolve(report):
    """The per-pressure table is keyed by pressure ("11.0"), so a naive split on "." reported every
    cell MISSING. Both the dotted key and list indices must resolve."""
    bundle = {"a": {"11.0": {"phi": 1.5}}, "b": {"ci95": [0.1, 0.2]}}
    assert B._get(bundle, "a.11.0.phi") == 1.5
    assert B._get(bundle, "b.ci95.1") == 0.2
    with pytest.raises(KeyError):
        B._get(bundle, "a.12.0.phi")


def test_every_claim_still_passes():
    ok, failures, manifest = B.verify(write_manifest=False)
    assert ok, failures
    assert manifest["n_claims"] == len(B._CLAIMS)


def test_the_recorded_pressure_values_now_have_a_producer():
    """They were transcribed from a reviewer's table until the audit found they had none."""
    from puckworks.analysis import waszkiewicz_shot_level as W
    r = W.recorded_pressure_robustness()
    assert r["static_nominal_rmse_g_per_s"] == pytest.approx(0.647696, abs=1e-5)
    assert r["static_recorded_rmse_g_per_s"] == pytest.approx(0.646846, abs=1e-5)
    assert r["phi_nominal_rmse_g_per_s"] == pytest.approx(0.115769, abs=1e-5)
    assert r["phi_recorded_rmse_g_per_s"] == pytest.approx(0.116443, abs=1e-5)
    assert r["both_shifts_below_0p001"] and r["ordering_unchanged"]


def test_the_pressure_gap_numbers_are_bound_to_the_producer_that_already_existed():
    """A CORRECTION to this work, kept as a test so the mistake cannot recur.

    The coverage audit first reported "up to 0.61 bar" and "a mean 8.71 bar" as unbacked, and they
    were briefly replaced with values computed from a new whole-trace producer (0.508 / 8.768).
    That was wrong: `waszkiewicz_cross_pressure.pressure_domains()` already computed both, scoped
    to the SETTLED EQUILIBRIUM ENDPOINTS rather than the whole trace — which is the right basis for
    "what the rig delivered at this setting", since the early ramp is not delivery. The audit had
    only searched the shot-level module and the bundle.

    Two lessons are pinned here: the manuscript keeps the original values, and there is exactly ONE
    producer for this quantity. Two nearly-equal numbers under different scopes is the precise
    hazard these papers are about.
    """
    from puckworks.analysis import waszkiewicz_cross_pressure as X
    from puckworks.analysis import waszkiewicz_shot_level as W

    d = X.pressure_domains()
    assert d["max_nominal_recorded_gap_bar"] == pytest.approx(0.606, abs=2e-3)
    assert d["primary_analysis_recorded_bar"] == pytest.approx(8.713, abs=2e-3)

    text = C.MANUSCRIPT.read_text(encoding="utf-8")
    assert "0.61 bar" in text and "8.71 bar" in text
    assert "0.508 bar" not in text and "8.768 bar" not in text

    assert not hasattr(W, "nominal_vs_recorded_pressure"), (
        "the competing whole-trace producer is back; there must be exactly one definition of the "
        "nominal-minus-recorded gap")
