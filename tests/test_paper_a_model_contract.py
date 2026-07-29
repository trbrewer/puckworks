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

    The manuscript may hold out the complete C/F corpus or a named subset of it, but it may not
    describe a subset as the whole.
    """
    text = path.read_text()
    for stanza in re.findall(r"[^.\n|]*coarse/fine[^.\n|]*", text, flags=re.I):
        assert "all of it" not in stanza.lower(), (
            f"{path.name}: unqualified corpus-completeness claim: {stanza.strip()!r}")


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
    """P1-1 item 5 / round-6 carry-over: no calibrated-CI vocabulary on a percentile range."""
    from puckworks.validation.slow import angeloni_bracket as ab

    recs = [dict(group="Arabica:caffeine", variety="Arabica", solute="caffeine", sample="X",
                 grind="C", on_grid=True, lookup_defined=True, T=90.0, p=9.0,
                 e_model=0.0, e_const=0.0, delta=1.0)]
    out = ab.paired_clustered_bootstrap(recs, B=50, seed=0)
    assert "ci95_pp" not in out
    assert "percentile_range_pp" in out
    assert "not a calibrated" in out["interval_kind"]


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


# ── presentation contract: one interval, one precision (P1-6) ──────────────────────────────
def test_primary_range_is_rendered_at_one_precision_everywhere():
    """The 40 g primary clustered range must not appear at two different precisions."""
    rendered = set()
    for path in PROSE:
        rendered |= set(re.findall(r"\[[−-]0\.7\d+,\s*[+−-]?0\.0\d+\]", path.read_text()))
    decimals = {len(v.split(".")[1].split(",")[0]) for v in rendered} if rendered else set()
    assert len(decimals) <= 1, (
        f"the primary range is rendered at mixed precision: {sorted(rendered)}")


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
