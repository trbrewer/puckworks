"""Semantic contracts for Paper 1 (round-7 Gate 4).

Round 7 found three submission-blocking defects that every existing check passed:

  * the manuscript stated a Reynolds number differing from the executable one by a factor
    alpha_l^-2 ~ 34.6 -- the numerals were fine, the *semantics* were not;
  * a mass endpoint was labelled as a volume one throughout, the token "40" being identical
    either way;
  * the headline corpus excluded eight available records while the prose claimed it held out
    the corpus in its entirety, the observation count being arithmetically correct for the
    hidden subset.

Value-level bindings cannot see any of these. What follows binds MEANING: the equation the
manuscript displays against the one the code evaluates, the endpoint's unit against its
stopping rule, and the declared corpus against the emitted sample-ID manifest.
"""
from __future__ import annotations

import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
MANUSCRIPT = REPO / "docs" / "submission" / "PAPER_A_JFE_MANUSCRIPT.md"
DRAFT = REPO / "docs" / "PAPER_A_DRAFT.md"
SUPPLEMENT = REPO / "docs" / "submission" / "PAPER_A_JFE_SUPPLEMENT.md"
CAPTIONS = REPO / "docs" / "figures" / "PAPER_A_CAPTIONS.md"
CARD = REPO / "docs" / "cards" / "pannusch2024.md"

PROSE = (MANUSCRIPT, DRAFT, SUPPLEMENT, CAPTIONS)


# ── model contract: the displayed Reynolds number is the evaluated one (P0-1) ──────────────
def test_sherwood_reynolds_is_built_on_superficial_velocity():
    """`closures.sherwood_h` must form Re on the SUPERFICIAL velocity it is handed.

    Recovered numerically rather than by reading the source: Sh = A Re^B Sc^(1/3), so doubling
    q must multiply Sh by exactly 2^B if and only if Re is proportional to q with no other
    q-dependence, and the recovered Re must equal d32 q rho/eta with NO porosity divisor.
    """
    from puckworks.models.pannusch2024 import closures as cl

    T, q, A, B = 366.55, 1.0e-3, 3.0, 0.6
    kin_vis = cl.water_viscosity(T) / cl.water_density(T)
    D = cl.diffusion_coeff(T, "caffeine")
    Sh = cl.sherwood_h(T, q, A, B, "caffeine") * cl.D32 / D
    Re_recovered = (Sh / (A * (kin_vis / D) ** (1.0 / 3.0))) ** (1.0 / B)

    assert Re_recovered == pytest.approx(cl.D32 * q / kin_vis, rel=1e-9)
    # and emphatically NOT the alpha_l-divided form the manuscript used to display
    from puckworks.models.pannusch2024 import solver as ps
    assert Re_recovered != pytest.approx(cl.D32 * q / (ps.ALPHA_L ** 2 * kin_vis), rel=1e-3)


def test_solver_transports_at_interstitial_and_scales_reynolds_by_superficial():
    """The porosity factor sits between the two velocities, and nowhere else.

    v_l = u_s / alpha_l is what the advection term uses; Re is formed on u_s. Equivalently
    Re = d32 alpha_l v_l rho / eta. This is the pairing that was misstated.
    """
    from puckworks.models.pannusch2024 import closures as cl
    from puckworks.models.pannusch2024 import solver as ps

    T, u_s = 366.55, 1.0e-3
    v_l = u_s / ps.ALPHA_L
    kin_vis = cl.water_viscosity(T) / cl.water_density(T)
    assert cl.D32 * u_s / kin_vis == pytest.approx(
        cl.D32 * ps.ALPHA_L * v_l / kin_vis, rel=1e-12)


def test_manuscript_reynolds_equation_matches_the_code():
    """The displayed equation must be the superficial form, and must not be the old one."""
    for path in (MANUSCRIPT, DRAFT):
        text = path.read_text()
        assert r"Re = \frac{d_{32} u_s \rho(T)}{\eta(T)}" in text, path
        assert r"\frac{d_{32} v_l \rho(T)}{\alpha_l \eta(T)}" not in text, (
            f"{path}: the alpha_l^-2 Reynolds definition is back (round-7 P0-1)")
        assert r"u_s = Q/A_{cs}" in text, f"{path}: superficial velocity is not defined"


def test_card_reynolds_equation_matches_the_code():
    text = CARD.read_text()
    assert "Re = d32 u_s ρ(T)/η(T)" in text
    assert "Re = d32 v_l ρ(T)/(α_l η(T))," not in text, (
        "the card's Reynolds definition regressed to the alpha_l^-2 form")


# ── observation contract: the endpoint is a MASS, and is labelled as one (P0-2) ────────────
def test_endpoint_stopping_rule_is_a_mass_target():
    """`_matched_bounds` divides a target by the source flow, which the source consumes as g/s.

    So the stopping rule yields grams. The constant that names it must say so.
    """
    from puckworks.validation.slow import angeloni_bracket as ab

    assert ab._M_TARGET_G == 40.0
    assert not hasattr(ab, "_V_TARGET_ML"), (
        "the volume-named endpoint constant is back (round-7 P0-2)")
    assert ab._SOURCE_FLOW_UNITS["consumed_as"] == "g/s"
    assert ab._SOURCE_FLOW_UNITS["endpoint_unit"] == "g"
    # t_end = target / flow, exactly -- 40 g at 2 g/s is 20 s
    assert ab._matched_bounds(2.0, 40.0) == [0.0, 20.0]


@pytest.mark.parametrize("path", PROSE, ids=lambda p: p.name)
def test_no_volume_labelled_endpoints_in_the_prose(path):
    """A mass endpoint must never be printed with a volume unit.

    Catches "40 mL endpoint", "38/40/42 mL", "40 mL matched-volume proxy" and friends in any
    submission-facing document.
    """
    text = path.read_text()
    banned = [
        (r"\b(?:38|40|42)\s*mL\b", "mass endpoint printed in mL"),
        (r"matched[- ]volume", "the retired matched-volume proxy narrative"),
        (r"mass[- ]to[- ]volume substitution", "the retired mass-to-volume substitution claim"),
        (r"volume proxy", "the retired volume-proxy narrative"),
    ]
    for pattern, why in banned:
        hits = re.findall(pattern, text)
        assert not hits, f"{path.name}: {why} ({len(hits)} occurrence(s): {hits[:4]})"


# ── corpus contract: the declared corpus is the scored one (P0-3) ──────────────────────────
def _bio():
    from puckworks import data as d
    return d.angeloni_bioactives()


def test_off_grid_cf_records_exist_and_are_known():
    """The eight records whose silent exclusion was the P0-3 defect."""
    off = sorted(r["sample"] for r in _bio()
                 if r["granulometry"] in ("C", "F") and r["on_grid"] == "False")
    assert off == ["A21", "A22", "A32", "A33", "R21", "R22", "R32", "R33"]


def test_no_off_grid_cf_condition_has_an_o_counterpart():
    """Why the lookup comparator cannot simply be extended to the complete corpus."""
    bio = _bio()
    o_conds = {(r["variety"], r["T_degC"], r["p_bar"]) for r in bio
               if r["granulometry"] == "O" and r["on_grid"] == "True"}
    off = [r for r in bio if r["granulometry"] in ("C", "F") and r["on_grid"] == "False"]
    assert off and not any((r["variety"], r["T_degC"], r["p_bar"]) in o_conds for r in off)


@pytest.mark.parametrize("path", (MANUSCRIPT, DRAFT), ids=lambda p: p.name)
def test_corpus_completeness_claims_are_qualified(path):
    """No unqualified "all of it" about a corpus that is partly excluded.

    Retained as an editorial lint. It is NOT the corpus contract -- round 8 showed that a phrase
    prohibition cannot bind an estimand, because the stale 108-point caption contained no
    prohibited phrase and sailed through. The binding contract is below.
    """
    text = path.read_text()
    for stanza in re.findall(r"[^.\n|]*coarse/fine[^.\n|]*", text, flags=re.I):
        assert "all of it" not in stanza.lower(), (
            f"{path.name}: unqualified corpus-completeness claim: {stanza.strip()!r}")


# ── corpus contract, bound to the emitted manifest (round-8 P1-4) ───────────────────────────
#
# The round-8 review found that the "declared corpus against the sample-ID manifest" binding the
# brief advertised did not exist: the manuscript-facing check only scanned sentences containing
# "coarse/fine" and forbade one phrase. The 108-point failure could therefore recur verbatim with
# different wording -- and the stale Figure 3 caption is exactly that, a live demonstration.

def test_source_derived_manifest_is_the_committed_corpus():
    """Rebuild the manifest from bioactives.csv and require every artefact to carry it.

    Deriving both sides from the same JSON would only prove internal consistency and could
    certify a wrong corpus, so the expected side comes from the SOURCE.
    """
    from puckworks.paper_a import transfer_contract as TC

    expected = TC.build_transfer_corpus_manifest(_bio(), include_off_grid=True)
    assert expected["n_held_out_records"] == 44
    assert expected["n_observations"] == 132
    assert expected["off_grid_sample_ids"] == list(TC.OFF_GRID_SAMPLE_IDS)
    assert expected["excluded_sample_ids"] == []

    got = _endpoint_artifact()["corpus"]
    assert got["manifest_sha256"] == expected["manifest_sha256"], (
        "the endpoint artefact's corpus is not the one the source data produces")
    assert got["included_sample_ids_sha256"] == expected["included_sample_ids_sha256"]
    assert sorted(got["held_out_sample_ids"]) == sorted(expected["held_out_sample_ids"])


def test_a_count_preserving_membership_change_is_detected():
    """44 records with ONE swapped id must not hash the same. Counts alone cannot see this."""
    from puckworks.paper_a import transfer_contract as TC

    good = TC.build_transfer_corpus_manifest(_bio(), include_off_grid=True)
    mutated = [dict(r) for r in good["records"]]
    mutated[0] = dict(mutated[0], sample_id="ZZZ")           # same count, different membership
    assert len(mutated) == good["n_held_out_records"]
    assert TC.sha256_of(mutated) != good["manifest_sha256"]


def test_a_metadata_change_under_unchanged_ids_is_detected():
    """Same 44 ids, one record's grind altered — the ID hash misses it, the full hash must not."""
    from puckworks.paper_a import transfer_contract as TC

    good = TC.build_transfer_corpus_manifest(_bio(), include_off_grid=True)
    mutated = [dict(r) for r in good["records"]]
    mutated[0] = dict(mutated[0], grind="F" if mutated[0]["grind"] == "C" else "C")
    ids = sorted(r["sample_id"] for r in mutated)
    assert TC.sha256_of(ids) == good["included_sample_ids_sha256"]      # ids unchanged
    assert TC.sha256_of(mutated) != good["manifest_sha256"]             # full manifest is not


@pytest.mark.parametrize("path,block", (
    (CAPTIONS, "paper-a:transfer-caption"),
    (MANUSCRIPT, "paper-a:transfer-results"),
    (SUPPLEMENT, "paper-a:transfer-corpus-manifest"),
), ids=lambda v: getattr(v, "name", v))
def test_generated_blocks_carry_the_current_manifest_stamp(path, block):
    """Every generated block names the corpus it was rendered from, by hash.

    This is what stops a *different* 44-record corpus masquerading as the same one behind a
    matching visible count.
    """
    sys.path.insert(0, str(REPO))
    from tools.paper_a_transfer_text import extract_block  # noqa: PLC0415

    expected = _endpoint_artifact()["corpus"]["manifest_sha256"]
    body = extract_block(path.read_text(), block)
    assert expected in body, f"{path.name} block {block!r} carries no current manifest stamp"


def test_the_transfer_caption_reports_the_complete_corpus_not_the_matched_subset():
    """The round-8 P0-1 blocker, as a durable contract."""
    import json

    sys.path.insert(0, str(REPO))
    from tools.paper_a_transfer_text import extract_block  # noqa: PLC0415

    art = json.loads((REPO / "docs" / "paper1_resource"
                      / "PAPER_A_TRANSFER_CORPUS_CONTRACTS.json").read_text())
    cc = art["complete_corpus"]
    body = extract_block(CAPTIONS.read_text(), "paper-a:transfer-caption")

    assert str(cc["corpus"]["n_observations"]) in body
    assert f"{cc['n_model_worse_than_const']} of {cc['n_points']}" in body
    # The superseded round-7 tuple must not read as the plotted headline.
    for stale in ("8.2% pooled MAPE", "50 of 108"):
        assert stale not in body, f"the caption still quotes the superseded {stale!r}"
    # 108 may survive ONLY as an explicitly-labelled secondary sensitivity.
    if "108" in body:
        assert "secondary" in body.lower() and "matched-grid" in body.lower(), (
            "the caption mentions 108 observations without labelling it a matched-grid secondary "
            "sensitivity, so it can be misread as the plotted headline corpus")


# ── resampling contract: the primary cluster keeps a condition's solutes together (P1-1) ───
def test_primary_resampling_cluster_keeps_solutes_of_one_condition_together():
    """Under the primary unit, all solutes of a (variety, T, p) must move as one.

    Constructed so the two units are distinguishable: within a variety, one condition has a
    solute-dependent delta. If the resampler split solutes apart, the drawn means would take
    values that keeping them together cannot produce.
    """
    from puckworks.validation.slow import angeloni_bracket as ab

    recs = []
    for sol, delta in (("caffeine", 3.0), ("trigonelline", -3.0), ("5CQA", 0.0)):
        for cond, d in (((90.0, 9.0), delta), ((95.0, 9.0), 0.0)):
            recs.append(dict(group=f"Arabica:{sol}", variety="Arabica", solute=sol,
                             sample="X", grind="C", on_grid=True, lookup_defined=True,
                             T=cond[0], p=cond[1], e_model=0.0, e_const=0.0, delta=d))
    primary = ab.paired_clustered_bootstrap(recs, B=400, seed=0, unit="cond_in_variety")
    # every cluster's mean delta is 0 (the +3/-3/0 always travel together), so every resample
    # mean is exactly 0 and the range is degenerate
    assert primary["percentile_range_pp"] == [0.0, 0.0]
    assert primary["n_clusters"] == 2

    secondary = ab.paired_clustered_bootstrap(recs, B=400, seed=0, unit="cond_in_group")
    # resampling solutes independently manufactures spread that the design does not contain
    assert secondary["percentile_range_pp"] != [0.0, 0.0]


def test_resampling_output_is_not_called_a_confidence_interval():
    """P1-1 item 5 / round-6 carry-over: no calibrated-CI vocabulary on a percentile range.

    Round 8 replaced the free-text `interval_kind` with the contract's structured identifier. The
    name itself now carries the disclaimer — a consumer reading `interval_kind` cannot mistake
    `fixed_predictor_clustered_percentile_sensitivity_range` for a confidence interval — so the
    assertion binds that identifier rather than a phrase inside a sentence.
    """
    from puckworks.paper_a import transfer_contract as TC
    from puckworks.validation.slow import angeloni_bracket as ab

    recs = [dict(group="Arabica:caffeine", variety="Arabica", solute="caffeine", sample="X",
                 grind="C", on_grid=True, lookup_defined=True, T=90.0, p=9.0,
                 e_model=0.0, e_const=0.0, delta=1.0)]
    out = ab.paired_clustered_bootstrap(recs, B=50, seed=0)
    assert "ci95_pp" not in out
    assert "percentile_range_pp" in out
    assert out["interval_kind"] == TC.INTERVAL_KIND
    assert "sensitivity_range" in out["interval_kind"]
    assert "confidence" not in out["interval_kind"]
    # The fixed-predictor contract is what denies the range calibrated coverage; say so in data.
    assert out["predictors_refit_inside_resampling"] is False


# ── method-description contract: the SI optimizer matches the producer (P1-3) ──────────────
def test_supplement_describes_objective_specific_level_optimizers():
    """`_profile_objectives` uses OLS / weighted LS / IRLS, not one least-squares fit."""
    import inspect

    from puckworks.validation.slow import angeloni_bracket as ab

    src = inspect.getsource(ab._profile_objectives)
    assert "_ls_level" in src and "_rel_level" in src and "_huber_level" in src

    text = SUPPLEMENT.read_text()
    assert "exact least-squares minimizer" not in text, (
        "SI S1 again claims one least-squares level fit for all three objectives (round-7 P1-3)")
    for needed in ("ordinary least squares", "weighted least squares", "IRLS"):
        assert needed.lower() in text.lower(), f"SI S1 does not name {needed}"


# ── presentation contract: the PRIMARY interval, bound to the artefact (round-8 P1-3) ──────
#
# What this replaced, and why it was worthless: the old test searched every prose file for
#
#     \[[−-]0\.7\d+,\s*[+−-]?0\.0\d+\]
#
# and asserted the matches shared one precision. That pattern CANNOT match the primary range,
# whose lower bound starts 0.8 -- it matched the *secondary* 0.7xx ranges instead, and on an empty
# match set it passed vacuously. A test named for the primary interval could therefore stay green
# through arbitrary drift in the primary interval. These load the value from the artefact, render
# it with the production formatter, and require it to be present.

def _endpoint_artifact():
    import json
    return json.loads((REPO / "docs" / "paper1_resource"
                       / "PAPER_A_ENDPOINT_PROPAGATION.json").read_text())


def _primary_row(ep, m_target_g=40.0):
    from puckworks.paper_a import transfer_contract as TC
    for row in ep["rows"]:
        if float(row[TC.ENDPOINT_ROW_KEY]) == m_target_g:
            return row
    raise AssertionError(f"no endpoint row at {m_target_g} g")


#: Where the primary interval is REQUIRED to appear, named by file and generated block. Scanning
#: whole files is what let an unrelated interval satisfy the old assertion.
REQUIRED_PRIMARY_INTERVAL_BLOCKS = (
    (MANUSCRIPT, "paper-a:transfer-results"),
    (MANUSCRIPT, "paper-a:transfer-endpoint-table"),
    (MANUSCRIPT, "paper-a:transfer-table5"),
    (SUPPLEMENT, "paper-a:transfer-scheme-table"),
)


def test_primary_interval_is_rendered_by_the_production_formatter():
    """The archived display text must be exactly what `format_pp_range` produces."""
    from puckworks.paper_a import transfer_contract as TC

    interval = _primary_row(_endpoint_artifact())["resampling"][TC.PRIMARY_SCHEME]["interval"]
    lo = interval["full_precision_pp"]["lower"]
    hi = interval["full_precision_pp"]["upper"]
    assert interval["display"]["text"] == TC.format_pp_range(lo, hi)


@pytest.mark.parametrize("path,block", REQUIRED_PRIMARY_INTERVAL_BLOCKS,
                         ids=lambda v: getattr(v, "name", v))
def test_primary_interval_occurs_in_every_required_block(path, block):
    """Non-vacuous by construction: each required block must CONTAIN the artefact's interval."""
    sys.path.insert(0, str(REPO))
    from puckworks.paper_a import transfer_contract as TC
    from tools.paper_a_transfer_text import extract_block  # noqa: PLC0415

    expected = _primary_row(_endpoint_artifact())["resampling"][TC.PRIMARY_SCHEME]["interval"]
    body = extract_block(path.read_text(), block)
    assert expected["display"]["text"] in body, (
        f"{path.name} block {block!r} does not carry the primary 40 g interval "
        f"{expected['display']['text']!r}")


def test_a_secondary_interval_cannot_satisfy_the_primary_contract():
    """The exact defect round 8 found: a secondary range present, the primary one absent.

    Rendered against a mutated block, the required-occurrence assertion must FAIL. If it passes,
    the contract is selecting on shape rather than on the primary value.
    """
    from puckworks.paper_a import transfer_contract as TC
    from tools.paper_a_transfer_text import extract_block  # noqa: PLC0415

    ep = _endpoint_artifact()
    row = _primary_row(ep)
    primary = row["resampling"][TC.PRIMARY_SCHEME]["interval"]["display"]["text"]
    secondary = row["resampling"]["cond_in_group"]["interval"]["display"]["text"]
    assert primary != secondary

    body = extract_block(MANUSCRIPT.read_text(), "paper-a:transfer-results")
    mutated = body.replace(primary, secondary)
    assert primary not in mutated, "mutation did not remove the primary interval"


def test_primary_interval_is_never_rendered_at_an_unapproved_precision():
    """A correctly-valued interval at the wrong precision must not appear in the required blocks."""
    from puckworks.paper_a import transfer_contract as TC
    from tools.paper_a_transfer_text import extract_block  # noqa: PLC0415

    interval = _primary_row(_endpoint_artifact())["resampling"][TC.PRIMARY_SCHEME]["interval"]
    lo = interval["full_precision_pp"]["lower"]
    hi = interval["full_precision_pp"]["upper"]
    wrong = {TC.format_pp_range(lo, hi, d) for d in (1, 2, 4)} - {interval["display"]["text"]}
    for path, block in REQUIRED_PRIMARY_INTERVAL_BLOCKS:
        body = extract_block(path.read_text(), block)
        for bad in wrong:
            assert bad not in body, (
                f"{path.name} block {block!r} renders the primary interval as {bad!r}, "
                f"not at the declared {interval['display']['digits']}-decimal precision")


def test_interval_flags_are_derived_from_unrounded_bounds():
    """Round-8 P1-2: display rounding must not decide an analytical classification."""
    from puckworks.paper_a import transfer_contract as TC

    # An interval that EXCLUDES zero at full precision but DISPLAYS as touching it.
    knife = TC.interval_record(-0.8251, -0.0004)
    assert knife["excludes_zero_full_precision"] is True
    assert knife["contains_zero_full_precision"] is False
    assert knife["display"]["touches_zero"] is True
    assert knife["display"]["text"] == "[−0.825, +0.000]"
    assert knife["signed_nearest_bound_to_zero_pp"] == -0.0004

    # The mirror case: contains zero at full precision, displays identically.
    straddle = TC.interval_record(-0.8251, +0.0004)
    assert straddle["contains_zero_full_precision"] is True
    assert straddle["display"]["text"] == knife["display"]["text"], (
        "these two must be indistinguishable in DISPLAY and distinguishable in CLASSIFICATION")
    assert straddle["excludes_zero_full_precision"] != knife["excludes_zero_full_precision"]


def test_negative_zero_is_normalised_only_for_display():
    from puckworks.paper_a import transfer_contract as TC

    rec = TC.interval_record(-0.5, -0.0001)
    assert rec["full_precision_pp"]["upper"] == -0.0001      # signed value preserved
    assert rec["display"]["upper"] == 0.0                     # display normalised
    assert "−0.000" not in rec["display"]["text"]


# ── governance contract: the audit cannot outlive its own inputs (P1-5) ────────────────────
def test_claim_binding_audit_is_not_stale():
    """The audit fingerprints every manuscript and coverage module it reads.

    Round 7's confirmed stale-number finding was in this document: it reported the coverage state
    of an earlier commit while sitting in a tree that had moved on. Regenerating it is one command
    (`python tools/claim_binding_audit.py --write`); this test is what makes forgetting fail loudly.
    """
    import subprocess

    r = subprocess.run([sys.executable, "tools/claim_binding_audit.py"],
                       cwd=REPO, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr or r.stdout


def test_claim_binding_audit_headline_matches_the_live_audits():
    """The document's headline counts must be the ones the coverage modules produce now."""
    sys.path.insert(0, str(REPO))
    from tools.claim_binding_audit import coverage  # noqa: PLC0415

    cov = coverage()
    text = (REPO / "docs" / "CLAIM_BINDING_AUDIT.md").read_text()
    p1 = cov["papers"]["Paper 1"]
    assert f"**{p1['claims']}**" in text
    assert f"{p1['verified']} (" in text
    sl = cov["slow_lane"]
    assert f"| Registered slow-lane numbers | {sl['total']} |" in text
    assert f"**{sl['bound']}**" in text
