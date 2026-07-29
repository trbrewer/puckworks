"""Unit contracts for `puckworks.paper_a.transfer_contract` and the artefact writer.

Round-8 §2.5 asks for two independent layers, and the split is the point:

  1. does the ARTEFACT faithfully represent the source data and the producer?
  2. do the manuscript, caption, package and figures faithfully represent the artefact?

Deriving both sides of an assertion from the same JSON proves only internal consistency and can
certify a wrong artefact. Everything here that checks corpus membership rebuilds it from
`bioactives.csv`; everything that checks a rendered string calls the production formatter.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from puckworks.paper_a import transfer_contract as TC  # noqa: E402


def _bio():
    from puckworks import data as d
    return d.angeloni_bioactives()


# ── endpoint contract (round-8 P0-3) ────────────────────────────────────────────────────────
def test_endpoint_is_a_collected_mass_in_grams():
    ep = TC.endpoint_object()
    assert ep["quantity"] == "collected_mass"
    assert ep["unit"] == "g"
    assert ep["targets"] == [38.0, 40.0, 42.0]
    assert TC.endpoint_label() == "38/40/42 g"


def test_a_valid_endpoint_artifact_passes():
    art = {"endpoint": TC.endpoint_object(),
           "rows": [{"m_target_g": v} for v in (38.0, 40.0, 42.0)]}
    assert TC.validate_endpoint_contract(art) == []


@pytest.mark.parametrize("mutate,expect", [
    (lambda a: a.update({"v_targets": [38.0, 40.0, 42.0]}), "retired volume-endpoint key"),
    (lambda a: a["endpoint"].update({"unit": "mL"}), "endpoint.unit"),
    (lambda a: a["endpoint"].update({"quantity": "collected_volume"}), "endpoint.quantity"),
    (lambda a: a["endpoint"].update({"targets": [38.0, 40.0]}), "endpoint.targets"),
    (lambda a: a["rows"].pop(), "endpoint rows cover"),
    (lambda a: a["rows"].append({"m_target_g": 42.0}), "endpoint rows cover"),
    (lambda a: a["rows"][0].update({"v_target_ml": 38.0}), "retired key"),
    (lambda a: a.pop("endpoint"), "no typed `endpoint` object"),
])
def test_endpoint_mutations_are_rejected(mutate, expect):
    """Every one of these is a way the retired mL contract could creep back in."""
    art = {"endpoint": TC.endpoint_object(),
           "rows": [{"m_target_g": v} for v in (38.0, 40.0, 42.0)]}
    mutate(art)
    problems = TC.validate_endpoint_contract(art)
    assert any(expect in p for p in problems), (problems, expect)


def test_a_volume_schema_is_rejected_not_coerced():
    """Silently translating v_targets to m_targets would hide a unit error, not fix one."""
    art = {"v_targets": [38.0, 40.0, 42.0], "rows": [{"v_target_ml": 38.0}]}
    problems = TC.validate_endpoint_contract(art)
    assert problems and any("must be migrated explicitly, not coerced" in p for p in problems)


# ── display formatting (round-8 P1-2, P1-3) ─────────────────────────────────────────────────
@pytest.mark.parametrize("lo,hi,expect", [
    (-0.825, 0.0, "[−0.825, +0.000]"),
    (-0.742, -0.044, "[−0.742, −0.044]"),
    (-0.8251, -0.0004, "[−0.825, +0.000]"),
    (-0.8251, 0.0049, "[−0.825, +0.005]"),
])
def test_range_formatting_matches_the_papers_typography(lo, hi, expect):
    assert TC.format_pp_range(lo, hi) == expect
    assert "-" not in expect                       # Unicode minus only, never an ASCII hyphen


def test_percentages_are_two_decimals():
    assert TC.format_pct(8.44) == "8.44%"
    assert TC.format_pct(8.8) == "8.80%"


def test_display_quantisation_normalises_negative_zero():
    assert str(TC.quantize_for_display(-0.0004, 3)) == "0.000"
    assert str(TC.quantize_for_display(-0.0006, 3)) == "-0.001"


# ── interval classification (round-8 P1-2) ──────────────────────────────────────────────────
@pytest.mark.parametrize("lo,hi,contains,touches", [
    (-0.8251, -0.0004, False, True),     # excludes zero; displays as touching it
    (-0.8251, +0.0004, True, True),      # contains zero; displays identically
    (+0.0004, +0.8251, False, True),     # excludes zero on the other side
    (-0.8251, 0.0, True, True),          # closed-interval convention: a 0.0 bound touches
])
def test_zero_classification_uses_full_precision(lo, hi, contains, touches):
    rec = TC.interval_record(lo, hi)
    assert rec["contains_zero_full_precision"] is contains
    assert rec["excludes_zero_full_precision"] is (not contains)
    assert rec["display"]["touches_zero"] is touches


def test_width_uses_full_precision_bounds():
    rec = TC.interval_record(-0.82512, -0.00041)
    assert rec["width_pp"] == pytest.approx(0.82471, abs=1e-9)


def test_interval_validation_catches_a_hand_edited_display():
    rec = TC.interval_record(-0.825, 0.0)
    assert TC.validate_interval_record(rec) == []
    rec["display"]["text"] = "[−0.82, +0.00]"
    assert any("production formatter" in p for p in TC.validate_interval_record(rec))
    rec = TC.interval_record(-0.825, 0.0)
    rec["excludes_zero_full_precision"] = True                # contradicts its own bounds
    assert any("disagrees with its full-precision bounds" in p
               for p in TC.validate_interval_record(rec))


# ── corpus manifest (round-8 P1-4) ──────────────────────────────────────────────────────────
def test_complete_corpus_census_from_source():
    m = TC.build_transfer_corpus_manifest(_bio(), include_off_grid=True)
    assert (m["n_held_out_records"], m["n_observations"]) == (44, 132)
    assert m["n_lookup_observations"] == 108
    assert m["off_grid_sample_ids"] == list(TC.OFF_GRID_SAMPLE_IDS)
    assert m["lookup_undefined_sample_ids"] == list(TC.OFF_GRID_SAMPLE_IDS)
    assert m["excluded_sample_ids"] == []
    assert m["support_set"] == TC.SUPPORT_COMPLETE
    assert TC.validate_corpus_manifest(m, True) == []


def test_matched_grid_corpus_is_a_distinct_support_set():
    m = TC.build_transfer_corpus_manifest(_bio(), include_off_grid=False)
    assert (m["n_held_out_records"], m["n_observations"]) == (36, 108)
    assert sorted(m["excluded_sample_ids"]) == sorted(TC.OFF_GRID_SAMPLE_IDS)
    assert m["support_set"] == TC.SUPPORT_MATCHED_GRID
    assert m["support_set"] != TC.SUPPORT_COMPLETE, (
        "the headline and lookup supports must not share one identifier — that is how a "
        "108-observation number gets printed as the 132-observation headline")


def test_every_record_carries_the_canonical_three_solutes():
    m = TC.build_transfer_corpus_manifest(_bio(), include_off_grid=True)
    assert all(r["solutes"] == list(TC.SOLUTES) for r in m["records"])


def test_manifest_hash_is_order_independent_but_content_sensitive():
    m1 = TC.build_transfer_corpus_manifest(_bio(), include_off_grid=True)
    m2 = TC.build_transfer_corpus_manifest(list(reversed(_bio())), include_off_grid=True)
    assert m1["manifest_sha256"] == m2["manifest_sha256"], "row order must not change the hash"
    mutated = [dict(r) for r in m1["records"]]
    mutated[3] = dict(mutated[3], temperature_degC=1.0)
    assert TC.sha256_of(mutated) != m1["manifest_sha256"]


def test_condition_cluster_ids_include_variety():
    """Without variety, Arabica and Robusta conditions at one (T,p) collide into a cluster."""
    a = TC.condition_cluster_id("Arabica", 93.4, 9.0)
    r = TC.condition_cluster_id("Robusta", 93.4, 9.0)
    assert a != r and a.startswith("Arabica")


# ── resampling design (round-8 P0-2, P1-1) ──────────────────────────────────────────────────
def _records():
    """Per-observation records with the real corpus structure; deltas are irrelevant here."""
    out = []
    for variety in TC.VARIETIES:
        for sol in TC.SOLUTES:
            for g in ("C", "F"):
                for r in _bio():
                    if r["variety"] != variety or r["granulometry"] != g:
                        continue
                    out.append(dict(group=f"{variety}:{sol}", variety=variety, solute=sol,
                                    sample=r["sample"], grind=g, T=float(r["T_degC"]),
                                    p=float(r["p_bar"]), delta=0.0))
    return out


def test_primary_cluster_census_is_eighteen_by_six_plus_eight_by_three():
    """The exact composition the manuscript previously misstated as universally six."""
    d = TC.resampling_design(_records())
    prim = d["schemes"][TC.PRIMARY_SCHEME]
    assert prim["n_clusters"] == 26
    assert prim["cluster_size_distribution"] == {"3": 8, "6": 18}
    threes = {s for c in prim["membership"] if c["n_observations"] == 3 for s in c["sample_ids"]}
    assert threes == set(TC.OFF_GRID_SAMPLE_IDS)


def test_sample_record_scheme_is_forty_four_clusters_of_three():
    d = TC.resampling_design(_records())
    s = d["schemes"]["sample_in_variety_grind"]
    assert s["n_clusters"] == 44
    assert s["cluster_size_distribution"] == {"3": 44}
    assert s["n_strata"] == 4                       # variety x grind


def test_all_schemes_partition_the_same_observation_set():
    d = TC.resampling_design(_records())
    assert TC.validate_resampling_design(d, 132) == []
    sets = []
    for name in TC.SCHEME_ORDER:
        obs = sorted(o for c in d["schemes"][name]["membership"] for o in c["observation_ids"])
        assert len(obs) == len(set(obs)) == 132
        sets.append(obs)
    assert all(s == sets[0] for s in sets)


def test_no_sample_has_its_solutes_split_across_clusters():
    """A sample's three co-measured solutes are the clearest dependency the source establishes."""
    d = TC.resampling_design(_records())
    for name in ("cond_in_variety", "sample_in_variety_grind"):
        owner = {}
        for c in d["schemes"][name]["membership"]:
            for obs in c["observation_ids"]:
                owner.setdefault(obs.split("|")[0], set()).add(c["cluster_id"])
        assert all(len(v) == 1 for v in owner.values()), f"{name} splits a sample's solutes"


def test_a_scheme_that_drops_an_observation_is_rejected():
    d = TC.resampling_design(_records())
    d["schemes"][TC.PRIMARY_SCHEME]["membership"][0]["observation_ids"].pop()
    problems = TC.validate_resampling_design(d, 132)
    assert any("covers 131 observations" in p or "membership hash" in p for p in problems)


def test_declaring_refitting_inside_resampling_is_rejected():
    d = TC.resampling_design(_records())
    d["predictors_refit_inside_resampling"] = True
    assert any("fixed-predictor contract is violated" in p
               for p in TC.validate_resampling_design(d, 132))


# ── the checker actually runs (round-8: no contract may be untested at the CLI) ─────────────
def test_transfer_artifact_check_cli_passes():
    r = subprocess.run([sys.executable, "tools/paper_a_transfer_artifacts.py", "--check"],
                       cwd=REPO, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr or r.stdout


def test_transfer_text_check_cli_passes():
    r = subprocess.run([sys.executable, "tools/paper_a_transfer_text.py", "--check"],
                       cwd=REPO, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr or r.stdout


# ── claim-binding coverage arithmetic (round-8 P2-1) ────────────────────────────────────────
#
# The round-8 review asked for the brief's "11 of 95 unbound" to be reconciled to 6, on the
# authority of docs/CLAIM_BINDING_AUDIT.md. That would have been the wrong direction. The audit
# was computing `registered_results - binding_rules`, mixing two populations: five binding rules
# resolve values that are not registered slow-lane results, so subtracting credited them against
# results they do not cover and UNDERSTATED the gap. 11 was right; the audit is now fixed and
# asserts its own arithmetic, which is what should have caught this in the first place.

def test_slow_lane_categories_reconcile_to_the_registered_total():
    from puckworks.paper_a.claim_coverage import binding_coverage

    cov = binding_coverage()
    assert (cov["n_archive_bound"] + cov["n_declared_unbindable"] + cov["n_still_unbound"]
            == cov["n_slow_lane"])


def test_binding_rules_and_registered_results_are_distinct_populations():
    """Guards the exact conflation that produced the wrong number."""
    from puckworks.paper_a import claim_coverage as ca
    from puckworks.paper_a import slow_lane_bindings as sb

    rules = len(sb.BINDINGS) + len(sb.DERIVED) + len(sb.CODE_CONSTANTS)
    registered = len(ca.SLOW_LANE_RESULTS)
    cov = ca.binding_coverage()
    assert cov["n_archive_bound"] <= rules
    assert registered - rules != cov["n_still_unbound"] or rules == cov["n_archive_bound"], (
        "registered_total - binding_rules must not be used as the unbound count; it is only "
        "correct when every rule binds a registered result")


def test_the_audit_generator_refuses_to_publish_unreconciled_counts():
    from tools.claim_binding_audit import _reconcile_slow_lane  # noqa: PLC0415

    good = dict(total=95, bound=84, declared_unbindable=0, unbound=11,
                binding_rules=89, matching=89, mismatched=0, unresolvable=0)
    _reconcile_slow_lane(good)                                   # must not raise

    with pytest.raises(AssertionError, match="does not reconcile"):
        _reconcile_slow_lane(dict(good, unbound=6))              # the round-8 defect, exactly


def test_round8_coverage_snapshot_is_commit_pinned_and_reconciles():
    """The historical brief must not drift when later work changes live coverage."""
    import json

    snap = json.loads((REPO / "docs" / "paper1_resource"
                       / "PAPER_1_ROUND_8_COVERAGE_SNAPSHOT.json").read_text())
    assert snap["review_target_commit"].startswith("21b138a")
    assert (snap["bound"] + snap["declared_unbindable"] + snap["unbound"]
            == snap["registered_slow_lane_results"])
    assert snap["unbound"] == 11, "the round-8 brief's unbound count was 11, not 6"


def test_round8_brief_states_the_snapshot_counts():
    """The brief must ASSERT 11 of 95.

    "6 of 95" may still appear inside the correction note — the note exists precisely to record
    that the round-8 reviewer proposed that number and why it was wrong — so the assertion is
    scoped to live claim lines, excluding the blockquoted correction.
    """
    brief = (REPO / "docs" / "paper1_resource" / "PAPER_1_REVIEW_BRIEF_ROUND_8.md").read_text()
    assert "11 of 95" in brief
    live = [ln for ln in brief.splitlines() if not ln.lstrip().startswith(">")]
    assert not any("6 of 95" in ln for ln in live), (
        "the brief asserts 6 of 95 outside the correction note")
