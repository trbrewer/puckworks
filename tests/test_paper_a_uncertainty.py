"""Tests for the Paper A P0-5 uncertainty helpers (review MC4).

Offline + deterministic. Exercises the two PURE functions (no PDE solves) that the slow
analysis relies on: the objective-family profiler `_profile_objectives` and the dependence-aware
`paired_clustered_bootstrap`. The slow PDE-backed callers (identifiability_panel /
transfer_skill_vs_baselines) are hand-run, not in CI.
"""
import importlib
import sys
from pathlib import Path

import numpy as np
import pytest

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
AB = importlib.import_module("puckworks.validation.slow.angeloni_bracket")


# ── _profile_objectives ───────────────────────────────────────────────────────────
def test_objective_family_structure_and_keys():
    rates = np.geomspace(0.15, 6.5, 18)
    m = np.array([5.0, 6.0, 4.5, 5.5, 6.2, 4.8, 5.1, 5.9, 4.9])
    # NON-degenerate F: the predicted SHAPE varies with rate (not just a scale), so the level
    # cannot fully compensate -> the objectives have a genuine positive minimum with structure.
    F = np.abs(np.array([m * (1.0 + 0.3 * np.sin(0.5 * i + np.arange(len(m))))
                         for i in range(len(rates))])) + 0.1
    fam = AB._profile_objectives(rates, F, m)
    for obj in ("sse", "relative_l2", "huber"):
        assert obj in fam
        for t in ("2pct", "5pct", "10pct", "20pct"):
            s = fam[obj]["sets"][t]
            assert set(s) == {"frac_within", "rate_lo", "rate_hi", "log_width",
                              "lower_censored", "upper_censored"}
            assert 0.0 <= s["frac_within"] <= 1.0
    assert fam["huber_delta"] > 0


def test_degenerate_valley_persists_across_objectives():
    # The inventory-rate degeneracy with a POSITIVE floor: a FIXED shape (m+offset) scaled by
    # 1/L_i, so the level compensates the rate exactly at every point -> the objective is flat
    # at a constant positive misfit across the whole grid (a positive floor, not zero, so the
    # 10%-of-min threshold is well posed).
    rates = np.geomspace(0.15, 6.5, 18)
    m = np.array([5.0, 6.0, 4.5, 5.5, 6.2, 4.8, 5.1, 5.9, 4.9])
    offset = np.array([0.2, -0.15, 0.1, -0.1, 0.2, -0.2, 0.1, -0.1, 0.15])
    L = np.linspace(1.0, 3.0, len(rates))
    F = np.array([(m + offset) / L[i] for i in range(len(rates))])
    fam = AB._profile_objectives(rates, F, m)
    for obj in ("sse", "relative_l2", "huber"):
        s10 = fam[obj]["sets"]["10pct"]
        assert s10["frac_within"] == 1.0                  # flat everywhere
        assert s10["lower_censored"] and s10["upper_censored"]   # right-censored both ends


def test_sharp_objective_localizes():
    # A sharp case: m equals the prediction at exactly one rate; objective rises away from it.
    rates = np.geomspace(0.15, 6.5, 18)
    base = np.array([5.0, 6.0, 4.5, 5.5, 6.2, 4.8, 5.1, 5.9, 4.9])
    i_true = 9
    # shape that changes with rate so the level cannot compensate everywhere
    F = np.array([base * (1.0 + 0.4 * (i - i_true) / len(rates)) ** 2 for i in range(len(rates))])
    m = base * (1.0 + 0.4 * 0.0) ** 2                     # == F[i_true] shape at unit level
    fam = AB._profile_objectives(rates, F, m)
    s10 = fam["sse"]["sets"]["10pct"]
    assert s10["frac_within"] < 1.0                        # NOT flat everywhere
    assert not fam["sse"]["at_boundary"] or fam["sse"]["rate_at_min"] > 0


# ── paired_clustered_bootstrap ────────────────────────────────────────────────────
def _recs(deltas, groups=None, conds=None):
    n = len(deltas)
    groups = groups or ["Arabica:caffeine"] * n
    conds = conds or [(90.0, 9.0)] * n
    return [dict(group=groups[i], grind="C" if i % 2 else "F",
                 T=conds[i][0], p=conds[i][1], delta=float(deltas[i])) for i in range(n)]


def test_zero_delta_ci_brackets_zero():
    recs = _recs([0.0] * 12,
                 groups=["Arabica:caffeine"] * 6 + ["Robusta:caffeine"] * 6,
                 conds=[(88, 6), (88, 6), (93, 9), (93, 9), (98, 12), (98, 12)] * 2)
    for unit in ("cond_in_group", "group"):
        r = AB.paired_clustered_bootstrap(recs, B=500, seed=1, unit=unit)
        assert r["observed_mean_delta_pp"] == 0.0
        assert r["ci95_pp"][0] <= 0.0 <= r["ci95_pp"][1]
        assert r["excludes_zero"] is False


def test_constant_positive_delta_excludes_zero():
    recs = _recs([2.0] * 12,
                 groups=["Arabica:caffeine"] * 6 + ["Robusta:caffeine"] * 6,
                 conds=[(88, 6), (88, 6), (93, 9), (93, 9), (98, 12), (98, 12)] * 2)
    r = AB.paired_clustered_bootstrap(recs, B=500, seed=1, unit="cond_in_group")
    assert r["observed_mean_delta_pp"] == 2.0
    assert r["ci95_pp"] == [2.0, 2.0]               # every resample is 2.0
    assert r["excludes_zero"] is True
    assert r["frac_boot_model_worse"] == 1.0


def test_bootstrap_deterministic_and_units_differ_shape():
    rng = np.random.default_rng(0)
    deltas = rng.normal(-0.4, 3.0, 36)
    groups = sum(([f"g{k}"] * 6 for k in range(6)), [])
    conds = [(88, 6), (88, 6), (93, 9), (93, 9), (98, 12), (98, 12)] * 6
    recs = _recs(deltas, groups=groups, conds=conds)
    a1 = AB.paired_clustered_bootstrap(recs, B=800, seed=7, unit="cond_in_group")
    a2 = AB.paired_clustered_bootstrap(recs, B=800, seed=7, unit="cond_in_group")
    assert a1 == a2                                  # deterministic given seed
    g = AB.paired_clustered_bootstrap(recs, B=800, seed=7, unit="group")
    assert g["unit"] == "group" and g["n_points"] == 36
    # both report the same observed mean (only the resampling unit differs)
    assert a1["observed_mean_delta_pp"] == g["observed_mean_delta_pp"]


def test_bad_unit_raises():
    import pytest
    with pytest.raises(ValueError):
        AB.paired_clustered_bootstrap(_recs([1.0, 2.0]), unit="nonsense")


# ── _oob_coverage_bootstrap (P0-5 sub-analysis C, pure core) ──────────────────────
def test_oob_coverage_perfect_fit_is_zero():
    # every rate predicts m exactly at unit level -> in-bag fit is perfect, OOB error 0.
    m = np.array([5.0, 6.0, 4.5, 5.5, 6.2, 4.8, 5.1, 5.9, 4.9])
    F = np.tile(m, (18, 1))
    r = AB._oob_coverage_bootstrap([(F, m)], 9, n_boot=100, seed=0)
    assert r["oob_pooled_mape_point"] == 0.0
    assert r["coverage_interval95"] == [0.0, 0.0]
    assert r["n_boot_effective"] > 0


def test_oob_coverage_deterministic_and_positive():
    rng = np.random.default_rng(1)
    m = 5.0 + rng.normal(0, 0.5, 9)
    # shape varies with rate so the level cannot fit all conditions -> positive OOB error
    F = np.abs(np.array([m * (1 + 0.2 * np.sin(0.4 * k + np.arange(9))) for k in range(18)])) + 0.1
    a = AB._oob_coverage_bootstrap([(F, m)], 9, n_boot=200, seed=3)
    b = AB._oob_coverage_bootstrap([(F, m)], 9, n_boot=200, seed=3)
    assert a == b                                        # deterministic given seed
    assert a["oob_pooled_mape_point"] > 0
    lo, hi = a["coverage_interval95"]
    assert 0.0 <= lo <= hi
    assert a["n_skipped_empty_oob"] >= 0


# ── objective-family grid record (third review MC3) ───────────────────────────────
# `PAPER_A_P0-5_RESULTS.md` said the objective-family sweep used an 18-point rate grid while the
# machine-readable record and the formal Methods said 29. The archived fractions decide it: every
# panel x objective value is an exact 29th and none is a multiple of 1/18. This binds the four
# places the grid is stated so the supporting record cannot drift from the producer again.
def test_objective_family_grid_record_agrees_across_json_and_notes():
    import json
    import re

    doc = _ROOT / "docs" / "paper1_resource"
    rec = json.loads((doc / "PAPER_A_OBJECTIVE_FAMILY_PANELS.json").read_text(encoding="utf-8"))
    n, domain = rec["n_rate_grid"], tuple(rec["rate_domain"])
    assert (n, domain) == (29, (0.15, 6.5))

    # Every panel carries the same grid.
    for name, panel in rec["panels"].items():
        assert panel["n_rate_grid"] == n, name
        assert tuple(panel["rate_domain"]) == domain, name

    # Every archived 10 % fraction is an exact k/29 -- the evidence that fixes the denominator.
    for name, panel in rec["panels"].items():
        for obj in rec["objectives"]:            # skips the scalar `huber_delta` sibling
            res = panel["objective_family"][obj]
            frac = res["sets"]["10pct"]["frac_within"]
            k = round(frac * n)
            assert abs(k / n - frac) < 5e-4, f"{name}/{obj}: {frac} is not a {n}th"
            assert abs(round(frac * 18) / 18 - frac) > 5e-4 or frac in (0.0, 1.0), (
                f"{name}/{obj}: {frac} is ambiguous between an 18- and {n}-point grid")

    notes = (doc / "PAPER_A_P0-5_RESULTS.md").read_text(encoding="utf-8")
    assert re.search(rf"0\.15[–-]6\.5,\s*\*\*{n}\*\*\s*\n?points", notes), (
        "the P0-5 note must state the 29-point objective-family grid")
    # Counts are printed with their denominator so a bare fraction cannot hide it (MC3).
    assert notes.count(f"/{n} = ") >= 18, "grid counts must print as k/29 for all 18 cells"


def test_manuscript_separates_the_ladder_grid_from_the_objective_family_grid():
    """18 points is correct for the ladder/comparator analyses; 29 for the formal panel. The two
    must stay distinguishable, not be collapsed into one number."""
    man = (_ROOT / "docs" / "submission" / "PAPER_A_JFE_MANUSCRIPT.md").read_text(encoding="utf-8")
    assert "**18** points for the ladder and comparator analyses" in man
    assert "**29** points for the" in man


# ── diffusivity closure provenance (round-4 review P0-2) ──────────────────────────────────────
def test_the_diffusivity_closure_matches_the_SOURCE_CARD_not_just_itself():
    """The previous unit test reproduced the implemented expression, which proves internal
    consistency and nothing about transcription. This binds the implementation to the CARD, which
    is the repository's declared source of truth for a model's physics.

    The card's Eq. 11 is solute-indexed (`M_i`), and the implementation uses the solute molecular
    weight. That is faithful. It is ALSO a departure from the standard Wilke-Chang correlation,
    which pairs the association factor with the SOLVENT molecular weight -- so the manuscript may
    not call it Wilke-Chang without qualification.
    """
    import re
    from puckworks.models.pannusch2024 import closures as pc

    card = (_ROOT / "docs" / "cards" / "pannusch2024.md").read_text(encoding="utf-8")
    card_flat = " ".join(card.split())
    assert "D_i(T) = 7.4·10^{-15}·(2.6 M_i)^{1/2} T / (η(T) V_i^{0.6})" in card_flat, (
        "the card's diffusivity equation has changed -- re-audit the port against it")
    # Solute-indexed on the card; solute molecular weights in the code.
    assert re.search(r"\(2\.6 M_i\)", card_flat), "the card is no longer solute-indexed"
    for name, mw in (("caffeine", 194.19), ("trigonelline", 137.14), ("5CQA", 354.31)):
        assert abs(pc.SOLUTES[name]["M"] - mw) < 0.01, name
        assert pc.SOLUTES[name]["M"] > 100, (
            f"{name} M looks like a solvent mass; the port would then disagree with the card")


def test_the_manuscript_does_not_call_the_closure_wilke_chang_unqualified():
    man = (_ROOT / "docs" / "submission" / "PAPER_A_JFE_MANUSCRIPT.md").read_text(encoding="utf-8")
    flat = " ".join(man.split())
    assert "the last being the **diffusivity closure implemented in the source model**" in flat
    assert "We do not call it the Wilke–Chang relation without qualification" in flat
    # the bounded consequence must be stated, not just the discrepancy
    assert "algebraically identical" in flat and "rate multiplier by \\(r^{2/3}\\)" in flat
    assert "is not physically interpretable as a" in flat


def test_the_closure_audit_is_archived_with_its_unresolved_part():
    import json
    rec = json.loads((_ROOT / "docs" / "paper1_resource"
                      / "PAPER_A_DIFFUSIVITY_CLOSURE_AUDIT.json").read_text(encoding="utf-8"))
    assert "what_remains_unresolved" in rec, (
        "the audit must record what it could NOT settle, not only what it could")
    assert "not held here" in rec["what_remains_unresolved"]
    # the degeneracy is the load-bearing finding
    n = rec["numerical_check_arabica_caffeine_optimal_grind"]
    assert abs(n["minimum_MAPE_pct"]["source_closure"]
               - n["minimum_MAPE_pct"]["solvent_MW"]) < 0.05, "fit quality should be unchanged"
    assert n["rate_at_minimum"]["solvent_MW"] != n["rate_at_minimum"]["source_closure"], (
        "the fitted rate SHOULD move; that is the whole point")


# ── cover-letter declarations (Paper 1 fourth review P0-7) ────────────────────────────────────
def test_cover_letter_asserts_nothing_the_front_matter_does_not_support():
    """A generator must not make representations to an editor on the authors' behalf.

    The cover letter said "all authors have approved the submission" and "we declare no competing
    interests" while `authors` and `competing_interests` were both null in the front matter. Those
    are statements about real people that only the authors can make. This test drives the field
    both ways: with the field unset the sentence must be absent AND the letter must say why; with
    it set the sentence must appear.
    """
    import copy
    # Skip on the DEPENDENCY, not the module. `tools.paper_a_front_matter` imports cleanly
    # without pyyaml -- the yaml import is deliberately lazy, inside `load()` -- so
    # `importorskip` on the module always succeeded and the test then died in `load()` on the
    # min-deps lane. Guard on what is actually missing.
    pytest.importorskip("yaml", reason="pyyaml is a dev/radar extra; not in min-deps")
    from tools import paper_a_front_matter as FM
    fm = FM.load()

    def asserted(letter: str) -> str:
        """The letter's own prose, lower-cased and flattened.

        The blocked-declaration note QUOTES each withheld sentence in order to say it is not being
        made, so searching the whole letter would find the very sentences it withholds. Only
        non-block-quote lines count as assertions.
        """
        body = [ln for ln in letter.splitlines() if not ln.lstrip().startswith(">")]
        return " ".join(" ".join(body).lower().split())

    for key, sentence, _why in FM.LETTER_ASSERTIONS:
        blank = copy.deepcopy(fm)
        blank[key] = None
        letter = FM.cover_letter(blank)
        assert sentence not in asserted(letter), (
            f"cover letter asserts \"{sentence}\" while `{key}` is unset")
        assert "not ready to send" in letter, (
            f"cover letter omits the {key} assertion but does not say the letter is unready")

        filled = copy.deepcopy(fm)
        filled[key] = "A. Author"
        for other, _s, _w in FM.LETTER_ASSERTIONS:
            filled[other] = filled[other] or "placeholder"
        assert sentence in asserted(FM.cover_letter(filled)), (
            f"cover letter drops \"{sentence}\" even when `{key}` is supplied")


def test_shipped_cover_letter_matches_the_current_front_matter_state():
    """The letter on disk must reflect the fields as they actually stand."""
    import pathlib
    # Skip on the DEPENDENCY, not the module. `tools.paper_a_front_matter` imports cleanly
    # without pyyaml -- the yaml import is deliberately lazy, inside `load()` -- so
    # `importorskip` on the module always succeeded and the test then died in `load()` on the
    # min-deps lane. Guard on what is actually missing.
    pytest.importorskip("yaml", reason="pyyaml is a dev/radar extra; not in min-deps")
    from tools import paper_a_front_matter as FM
    fm = FM.load()
    letter = pathlib.Path(FM.COVER_LETTER).read_text(encoding="utf-8")
    prose = " ".join(" ".join(ln for ln in letter.splitlines()
                              if not ln.lstrip().startswith(">")).lower().split())
    for key, sentence, _why in FM.LETTER_ASSERTIONS:
        present = sentence in prose
        assert present == bool(fm.get(key)), (
            f"shipped cover letter {'asserts' if present else 'omits'} \"{sentence}\" but `{key}` "
            f"is {'set' if fm.get(key) else 'unset'}")


# ── solver contract vs the source implementation (Paper 1 round-6 P0-1/P0-2) ──────────────────
def test_the_flow_conversion_matches_the_source_matlab_including_the_density_division():
    """The density division is the SOURCE's, and removing it would break fidelity.

    Round six reported `q = flow/1000/RHO/ACS` as a unit error: a value already in mL/s should not
    be divided by density, making velocity and collected volume 2.041 % high. The original MATLAB
    settles it -- `simulation_Fit2.m:3` reads

        q = flow ./ 1000 ./ paramPh.rho ./ paramPh.Acs;   %[m/s]

    character-for-character our expression, and the same conversion appears at seven call sites.
    The source therefore consumes its `flow` column as MASS flow in g/s while labelling it mL/s;
    the inconsistency is in the label, not the arithmetic.

    Removing the division would invalidate every archived fitted parameter (A, B, K_ref, gamma,
    c_s0 were all estimated under this convention), so this test exists to stop a well-meaning
    correction from silently diverging from the source.
    """
    from puckworks.models.pannusch2024 import solver as ps

    flow, area = 1.0, ps.ACS
    assert ps.RHO == 980.0
    q_source = flow / 1000.0 / ps.RHO / area
    q_volumetric = flow * 1e-6 / area          # what a true mL/s reading would give
    assert q_source == pytest.approx(q_volumetric * 1000.0 / ps.RHO, rel=1e-12)
    assert q_source / q_volumetric == pytest.approx(1000.0 / ps.RHO, rel=1e-12)
    # The 2.041 % is the source's, and it is expected -- pinned so it cannot drift unnoticed.
    assert 100.0 * (q_source / q_volumetric - 1.0) == pytest.approx(2.0408, abs=1e-3)


def test_the_collection_accumulator_is_mass_equivalent_not_volumetric():
    """A nominal 40-unit endpoint is 40 g, not 40 mL, and the manuscript must say so.

    The review asked for a test showing 1.00 mL/s for 40.00 s accumulates exactly 40.00 mL. It does
    not -- it accumulates 40.816 -- because the accumulator inherits the source's mass-flow
    convention. That is the correct behaviour for a faithful port, and it resolves the paper's
    '40 g source endpoint vs 40 mL modelled proxy' tension: the modelled endpoint is already
    mass-equivalent at rho = 980 kg/m^3.
    """
    import numpy as np

    from puckworks.models.pannusch2024 import solver as ps

    captured = {}
    original = ps._record_solve

    def spy(sol, nz):
        captured["y"], captured["nz"] = sol.y, nz
        original(sol, nz)

    ps._record_solve = spy
    try:
        ps.simulate_fractions(93.0, 1.00, [0.0, 40.0], ps._solute_params()["caffeine"], cl1=1.0)
    finally:
        ps._record_solve = original

    volume = float(np.asarray(captured["y"])[3 * captured["nz"]][-1])
    assert volume == pytest.approx(40.0 * 1000.0 / ps.RHO, rel=1e-4), (
        f"accumulated {volume:.4f} for 1.00 x 40.00; the source convention gives "
        f"{40.0 * 1000.0 / ps.RHO:.4f}")
    assert volume == pytest.approx(40.8163, abs=1e-3)


def test_the_reynolds_number_uses_superficial_velocity_as_the_source_does():
    """`SherwoodFunction.m` computes Re from the SUPERFICIAL velocity; the card's equation does not.

    The card (line 40) gives Re = d32 v_l rho/(alpha_l eta) with v_l = Q/(A alpha_l), which is
    alpha_l^-2 ~ 34.6x the implemented value. The source is authoritative for what the fitted
    parameters mean, and it reads `Re = paramPh.d32 .* q ./ kin_vis` with q superficial.
    """

    from puckworks.models.pannusch2024 import closures as pc

    T, q, d32 = 366.15, 4.0e-4, pc.D32
    kin_vis = pc.water_viscosity(T) / pc.water_density(T)
    expected_re = d32 * q / kin_vis

    D = pc.diffusion_coeff(T, "caffeine")
    A, B = 1.0, 0.5
    expected_h = (A * expected_re ** B * (kin_vis / D) ** (1 / 3)) / d32 * D
    assert float(pc.sherwood_h(T, q, A, B, "caffeine", d32)) == pytest.approx(expected_h, rel=1e-12)

    # And the interstitial reading really is the ~34.6x quantity the review computed, so the
    # discrepancy is documented rather than merely asserted.
    alpha_l = 0.17
    assert (expected_re / alpha_l ** 2) / expected_re == pytest.approx(34.6, abs=0.2)


# ── slow-lane numbers bound to their archives (claim-binding sweep, 2026-07-28) ────────────────
def test_every_slow_lane_binding_resolves_and_matches_its_archive():
    """Paper 1's slow-lane numbers must equal the archived run that produced them.

    `SLOW_LANE_RESULTS` records a prose sentence naming the producer and archive for each of these
    numbers. That is documentation, not verification -- nothing opened the archive. Five of the six
    review rounds found stale numbers by hand in exactly this population, because the failure mode
    is: the analysis is rerun and the prose is not updated, or the prose is edited and the analysis
    is not.

    This resolves each binding against the committed archive. It does NOT rerun the slow lane; the
    archives were written by the runs that produced the manuscript's numbers, so comparing against
    them catches the drift that actually happens, at no compute cost.
    """
    from puckworks.paper_a import slow_lane_bindings as B

    r = B.verify()
    assert r["n_bound"] > 0
    assert not r["mismatched"], "manuscript numbers disagree with their archives:\n  " + "\n  ".join(
        f"{t} -> {a}:{p} archived {v!r} (delta {d:+.6g})" for t, a, p, v, d in r["mismatched"])
    assert not r["unresolvable"], "bindings that no longer resolve:\n  " + "\n  ".join(
        f"{t} -> {a}:{p} {why}" for t, a, p, why in r["unresolvable"])


def test_the_binding_verifier_is_not_vacuous(tmp_path):
    """A verifier that cannot fail is decoration. Driven against a drifted archive."""
    import json

    from puckworks.paper_a import slow_lane_bindings as B

    archive = B.ARCHIVE_DIR / B.ENDPOINT
    original = archive.read_text(encoding="utf-8")
    try:
        doc = json.loads(original)
        doc["rows"][1]["paired_difference_pp"] = -0.5
        archive.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        assert B.verify()["mismatched"], "a drifted archive did not produce a mismatch"

        doc = json.loads(original)
        del doc["rows"][1]["paired_difference_pp"]
        archive.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        assert B.verify()["unresolvable"], "a missing archived field did not fail the binding"
    finally:
        archive.write_text(original, encoding="utf-8")
    assert not B.verify()["mismatched"] and not B.verify()["unresolvable"]


def test_unbindable_slow_lane_values_are_declared_not_silent():
    """A number nobody can bind must say so; otherwise it looks identical to a bound one."""
    from puckworks.paper_a import claim_coverage as C
    from puckworks.paper_a import slow_lane_bindings as B

    assert B.UNBINDABLE, "the unbindable set is empty; every slow-lane value cannot be bound yet"
    for token, reason in B.UNBINDABLE.items():
        assert token in C.SLOW_LANE_RESULTS, (
            f"{token!r} is declared unbindable but is not a slow-lane result")
        # The reason must say WHY it cannot be bound -- naming the missing artefact -- rather than
        # deferring to a sibling entry. An earlier version checked reason LENGTH, which is an
        # arbitrary proxy that a terse-but-complete reason fails and a padded empty one passes.
        assert any(k in reason.lower() for k in
                   ("no committed archive", "prose-only", "prose in", "not per-fold",
                    "nothing to resolve", "no committed record")), (
            f"{token!r}: the reason does not name what is missing -- {reason!r}")
    assert not (set(B.BINDINGS) & set(B.UNBINDABLE)), (
        "a value is both bound and declared unbindable")
