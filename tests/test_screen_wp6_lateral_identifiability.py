"""Focused tests for the WP6-LC-IDENT cheap screen.

These ESTABLISH the properties the verdict rests on rather than snapshotting the verdict:

  * the hand-derived forward map equals the exact network, recomputed here independently and at
    points that are NOT on the committed grid;
  * the inverse round-trips, and does so from BOUNDARY flows only;
  * injectivity holds on the nondegenerate domain, and the documented degeneracies are exactly
    {Xi = 0} union {c = 0} -- reported as no-information, never regularised;
  * path-swap symmetry, x10 scale invariance and node/global conservation;
  * Q alone is confounded (an explicit family) and Q + outlet share is not;
  * the proxy adversary is the EXISTING harness, called not reimplemented;
  * the mirror-imperfection check is LIVE -- it really does bias the ideal inverse -- while the
    calibrated-axials inversion stays exact;
  * the post-hoc counting diagnostic really exhibits distinct geometries with the same boundary
    flows and different Xi;
  * the frozen decision rule is exercised on inputs OTHER than the live one;
  * the bundle is deterministic and drift-detecting, the protocol commit precedes the result, and
    no generated Foundry artifact, ID registry entry or candidate portfolio file is touched.
"""
import copy
import json
import math
import pathlib
import subprocess

import pytest

from puckworks.models import lateral_coupling as lc
from puckworks.analysis import screen_wp6_lateral_identifiability as S

REPO = pathlib.Path(__file__).resolve().parents[1]
BUNDLE = REPO / "docs/insights/screens/WP6-LC-IDENT"


@pytest.fixture(scope="module")
def result():
    p = BUNDLE / "result.json"
    if not p.exists():
        pytest.skip("bundle not written yet (run --write)")
    return json.loads(p.read_text(encoding="utf-8"))


def _git(*args):
    return subprocess.run(("git",) + args, cwd=REPO, capture_output=True, text=True)


# ------------------------------------------------------------------------------------------
# the geometry really is the harness's isoresistive mirror
# ------------------------------------------------------------------------------------------

def test_primary_case_is_exactly_the_harness_isoresistive_mirror():
    from puckworks.analysis import lateral_coupling_discrimination as lcd
    case = [c for c in lcd.CASES if c.case_id == "isoresistive_mirror"][0]
    assert S.mirror_conductances(S.A_PRIMARY, S.C_PRIMARY) == case.g == (3.0, 1.0, 1.0, 3.0)


def test_mirror_construction_round_trips_c_and_Xi():
    for c in (-0.9, -0.25, 0.1, 0.5, 0.9):
        for A in (4.0, 40.0):
            a, b, b2, a2 = S.mirror_conductances(A, c)
            assert (a, b) == (a2, b2)[::-1] or (a == a2 and b == b2)
            assert a + b == pytest.approx(A)
            assert (a - b) / (a + b) == pytest.approx(c)
            for Xi in (0.05, 0.75, 19.0):
                G = S.g_lat_from_xi(A, Xi)
                assert lc.equalization_number(G, a, b, b2, a2) == pytest.approx(Xi, rel=1e-14)


# ------------------------------------------------------------------------------------------
# A/B — the analytic map and the inverse, recomputed independently OFF the committed grid
# ------------------------------------------------------------------------------------------

OFF_GRID = [(0.37, 0.006), (-0.62, 0.42), (0.83, 3.7), (-0.15, 88.0), (0.5, 0.1875)]


def test_forward_map_equals_the_exact_network_off_the_committed_grid():
    for c, Xi in OFF_GRID:
        o = S.observables_exact(S.A_PRIMARY, c, Xi)
        R_a, s_a = S.forward_map_analytic(c, Xi)
        assert R_a == pytest.approx(o["R"], abs=1e-13)
        assert s_a == pytest.approx(o["s"], abs=1e-13)


def test_forward_map_consequences_hold():
    """R - 1 = [c^2/(1-c^2)]*[Xi/(1+Xi)]  and  s - 1/2 = -c*Xi/(2(1+Xi-c^2))."""
    for c, Xi in OFF_GRID:
        o = S.observables_exact(S.A_PRIMARY, c, Xi)
        assert o["R"] - 1.0 == pytest.approx(
            (c * c / (1 - c * c)) * Xi / (1 + Xi), abs=1e-13)
        assert o["s"] - 0.5 == pytest.approx(
            -c * Xi / (2 * (1 + Xi - c * c)), abs=1e-13)
        assert o["R"] >= 1.0                       # coupling never lowers total flow here


def test_inverse_round_trips_from_boundary_flows_only():
    for c, Xi in OFF_GRID:
        o = S.observables_exact(S.A_PRIMARY, c, Xi)
        # only q1, q2 and Q0 are used to build (R, s) -- nothing interior
        R = (o["q1"] + o["q2"]) / o["Q0"]
        s = o["q1"] / (o["q1"] + o["q2"])
        inv = S.invert(R, s)
        assert inv["status"] == "ok"
        assert inv["c_hat"] == pytest.approx(c, abs=1e-9)
        assert inv["Xi_hat"] == pytest.approx(Xi, rel=1e-7)


def test_committed_recovery_is_within_the_frozen_software_tolerances(result):
    b = result["arm_b_forward_and_recovery"]
    assert b["forward_map_max_abs_error"] <= S.TOL_MAP
    assert b["c_max_abs_error"] <= S.TOL_C
    assert b["Xi_max_rel_error"] <= S.TOL_XI_REL
    assert b["failures"] == []
    assert b["n_nondegenerate"] == len(S.C_GRID) * len(S.XI_LOG_GRID) == 220


# ------------------------------------------------------------------------------------------
# injectivity and the degeneracies
# ------------------------------------------------------------------------------------------

def test_injectivity_on_the_nondegenerate_grid(result):
    inj = result["arm_b_forward_and_recovery"]["injectivity_empirical"]
    assert inj["distinct"] and inj["min_pairwise_Rs_distance"] > 0.0


def test_the_degenerate_fibre_is_exactly_Xi_zero_union_c_zero():
    """R = 1 <=> s = 1/2 <=> c*(t-1) = 0. Checked both ways."""
    for c in (-0.9, -0.1, 0.25, 0.9):
        o = S.observables_exact(S.A_PRIMARY, c, 0.0)
        assert o["R"] == pytest.approx(1.0, abs=1e-14)
        assert o["s"] == pytest.approx(0.5, abs=1e-14)
        assert S.invert(o["R"], o["s"])["status"] == "degenerate_no_information"
    for Xi in (1e-4, 0.75, 1e3):
        o = S.observables_exact(S.A_PRIMARY, 0.0, Xi)
        assert o["R"] == pytest.approx(1.0, abs=1e-14)
        assert o["s"] == pytest.approx(0.5, abs=1e-14)
        assert S.invert(o["R"], o["s"])["status"] == "degenerate_no_information"
    # ... and nowhere else on the grid
    for c in (-0.9, 0.1, 0.5):
        for Xi in (1e-4, 0.75, 1e3):
            o = S.observables_exact(S.A_PRIMARY, c, Xi)
            assert S.invert(o["R"], o["s"])["status"] == "ok"


def test_degeneracy_is_reported_not_regularised():
    inv = S.invert(1.0, 0.5)
    assert inv["Xi_hat"] is None and inv["c_hat"] is None
    assert inv["status"] == "degenerate_no_information"


def test_identical_paths_have_no_lateral_flow_at_any_coupling():
    for Xi in (1e-4, 1.0, 1e3):
        o = S.observables_exact(S.A_PRIMARY, 0.0, Xi)
        assert abs(o["open"]["q_lat_1to2"]) <= 1e-9
        assert o["open"]["p1"] == pytest.approx(o["open"]["p2"], rel=1e-14)


def test_strong_coupling_saturates_at_the_analytic_limit(result):
    lim = result["arm_e_controls"]["strong_coupling_limit"]
    assert lim["matches_analytic_limit"] and lim["saturation_matches"]
    assert lim["R_saturation_analytic"] == pytest.approx(
        1.0 + S.C_PRIMARY ** 2 / (1 - S.C_PRIMARY ** 2))
    assert lim["s_saturation_analytic"] == pytest.approx((1 - S.C_PRIMARY) / 2.0)
    # the residual at finite Xi is the PHYSICAL O(1/Xi) approach, not numerical error
    assert lim["R_approach_observed"] == pytest.approx(lim["R_approach_exact"], abs=1e-12)
    assert lim["s_approach_observed"] == pytest.approx(lim["s_approach_exact"], abs=1e-12)
    assert lim["R_approach_exact"] > 0.0


def test_conditioning_probe_bounds_the_models_float_validity_and_the_grid_is_inside_it(result):
    """The existing solve forms det = a*d - G^2 and loses ~log10(G/A) digits to cancellation.
    The screen must state where that starts and show its own grid sits inside the sound region --
    otherwise 'the analytic and implemented models agree' would be unbounded."""
    cp = result["arm_e_controls"]["numerical_conditioning_of_the_existing_model"]
    assert cp["screen_grid_is_inside_the_sound_region"] is True
    assert cp["screen_grid_max_Xi"] == 1000.0
    bad = cp["first_Xi_with_rel_deviation_above_1e_9"]
    assert bad is None or bad > cp["screen_grid_max_Xi"]
    # and the loss is real further out, so this is a live bound rather than a vacuous one
    worst = max(r["max_rel_deviation_from_analytic"] for r in cp["rows"])
    assert worst > 1e-9, "conditioning probe never sees the cancellation it describes"


# ------------------------------------------------------------------------------------------
# controls: swap, scale, conservation
# ------------------------------------------------------------------------------------------

def test_path_swap_reverses_the_share_but_not_the_recovered_Xi():
    for Xi in (0.05, 0.75, 19.0):
        f = S.observables_exact(S.A_PRIMARY, S.C_PRIMARY, Xi)
        r = S.observables_exact(S.A_PRIMARY, -S.C_PRIMARY, Xi)
        assert f["R"] == pytest.approx(r["R"], abs=1e-13)
        assert (f["s"] - 0.5) == pytest.approx(-(r["s"] - 0.5), abs=1e-13)
        iF, iR = S.invert(f["R"], f["s"]), S.invert(r["R"], r["s"])
        assert iF["c_hat"] == pytest.approx(-iR["c_hat"], abs=1e-9)
        assert iF["Xi_hat"] == pytest.approx(iR["Xi_hat"], rel=1e-9)


def test_x10_conductance_scaling_scales_flows_and_leaves_Xi_invariant():
    for Xi in (0.05, 0.75, 19.0):
        o1 = S.observables_exact(S.A_PRIMARY, S.C_PRIMARY, Xi)
        o2 = S.observables_exact(S.A_SCALED, S.C_PRIMARY, Xi)
        assert o2["Q"] / o1["Q"] == pytest.approx(10.0, rel=1e-13)
        assert o2["Q0"] / o1["Q0"] == pytest.approx(10.0, rel=1e-13)
        assert o2["R"] == pytest.approx(o1["R"], abs=1e-13)
        assert o2["s"] == pytest.approx(o1["s"], abs=1e-13)
        assert S.invert(o2["R"], o2["s"])["Xi_hat"] == pytest.approx(
            S.invert(o1["R"], o1["s"])["Xi_hat"], rel=1e-9)


def test_conservation_and_canonical_sign_hold_across_the_screen(result):
    cs = result["arm_e_controls"]["conservation_and_sign"]
    assert cs["passes"] and cs["max_abs_residual"] <= 1e-6
    for row in cs["rows"]:
        if abs(row["q_lat_1to2"]) > 1e-9:
            assert (row["q_lat_1to2"] > 0) == (row["p1_minus_p2"] > 0)


# ------------------------------------------------------------------------------------------
# C — the minimum-observable result, the load-bearing arm
# ------------------------------------------------------------------------------------------

def test_Q_alone_is_confounded_by_explicit_construction():
    """A family of distinct (c, Xi), BOTH signs of c, reproduces one R exactly."""
    Xi_true = 0.75
    o = S.observables_exact(S.A_PRIMARY, S.C_PRIMARY, Xi_true)
    R_obs = o["R"]
    c_min = math.sqrt(1.0 - 1.0 / R_obs)
    n = 0
    for c_mag in (c_min + 0.02, 0.6, 0.75, 0.9):
        for sgn in (+1.0, -1.0):
            c = sgn * c_mag
            t = (1.0 - R_obs * (1.0 - c * c)) / (c * c)
            Xi = 1.0 / t - 1.0
            assert Xi > 0.0
            assert S.observables_exact(S.A_PRIMARY, c, Xi)["R"] == pytest.approx(R_obs, rel=1e-12)
            n += 1
    assert n >= 8


def test_the_share_identity_that_collapses_the_family():
    """s - 1/2 = -(R-1)/(2 R c) holds identically, so s determines c given R."""
    for c, Xi in OFF_GRID:
        o = S.observables_exact(S.A_PRIMARY, c, Xi)
        assert o["s"] - 0.5 == pytest.approx(
            -(o["R"] - 1.0) / (2.0 * o["R"] * c), abs=1e-13)


def test_committed_minimum_observable_arm_says_both_things(result):
    c_arm = result["arm_c_minimum_observable"]
    assert c_arm["Q_only_is_confounded"] is True
    assert c_arm["Q_plus_share_is_unique"] is True
    for f in c_arm["families"]:
        assert f["all_members_reproduce_R"] is True
        assert f["n_members_also_matching_s"] == 0
        assert f["n_family_members"] >= 8
        assert f["s_sign_separates_the_two_branches"] is True


# ------------------------------------------------------------------------------------------
# D — the proxy adversary is the existing harness
# ------------------------------------------------------------------------------------------

def test_proxy_adversary_calls_the_existing_harness_not_a_copy():
    import inspect
    src = inspect.getsource(S.arm_d_proxy_adversary)
    assert "lcd.physical_row(" in src
    assert "frozen_two_path_proxy(" not in src        # not reimplemented here


def test_no_continuous_alpha_reproduces_the_joint_signature(result):
    d = result["arm_d_proxy_adversary"]
    assert d["no_proxy_reproduces_joint_signature"] is True
    for row in d["rows"]:
        assert row["proxy_share_alpha_invariant"] is True     # s0 = 0.5 structurally
        assert row["mathematically_distinguishable"] is True
        assert row["Xi_reported_by_harness"] == pytest.approx(row["Xi_requested"], rel=1e-9)


def test_no_alpha_to_Xi_law_is_invented():
    import inspect
    src = inspect.getsource(S)
    assert "alpha_of_Xi" not in src and "alpha_from_Xi" not in src
    assert "def alpha" not in src


# ------------------------------------------------------------------------------------------
# F — the mirror-imperfection adversary is LIVE, and the calibrated route is exact
# ------------------------------------------------------------------------------------------

def test_mirror_imperfection_actually_biases_the_ideal_inverse(result):
    """A vacuous adversarial check would show ~0 bias. This one must bite, and bite harder as
    the perturbation grows."""
    levels = result["arm_f_mirror_imperfection"]["levels"]
    biases = [lv["mirror_inverse_max_abs_Xi_rel_bias"] for lv in levels]
    assert all(b > 0.1 for b in biases), "the adversarial check is not biting"
    assert biases == sorted(biases), "bias must grow with the perturbation level"


def test_the_inverse_self_diagnoses_only_partially(result):
    """An impossible Xi_hat is a useful alarm; a possible one is NOT evidence of symmetry. The
    bundle must show both halves, or a reader will treat a physical-looking answer as a check."""
    lv = {l["perturbation_level"]: l for l in result["arm_f_mirror_imperfection"]["levels"]}
    assert lv[0.01]["mirror_inverse_n_nonphysical"] == 0, (
        "at 1 % nothing is flagged -- this is the half that makes the alarm unreliable")
    assert lv[0.05]["mirror_inverse_n_nonphysical"] > 0, "the alarm must fire somewhere"
    # ... and even where it fires, most rows still return a plausible wrong answer
    worst = lv[0.05]
    assert worst["mirror_inverse_n_nonphysical"] < 0.5 * worst["n_rows"]


def test_calibrated_axial_inversion_is_exact_for_arbitrary_geometry(result):
    for lv in result["arm_f_mirror_imperfection"]["levels"]:
        assert lv["calibrated_all_exact"] is True
        assert lv["calibrated_max_Xi_rel_err"] <= 1e-9
        assert lv["bisection_cross_check_passes"] is True


def test_calibrated_inversion_recovers_G_on_a_non_mirror_geometry():
    """Independent of the committed artifact: an asymmetric NONDEGENERATE geometry, no mirror
    assumption. (Requirement 2 of the calibrated-degeneracy correction.)"""
    g = (4.0, 0.8, 1.5, 2.5)                         # lcd's general_asymmetric case
    assert S.cross_product_gap_driver(g) != 0.0
    for G in (0.05, 1.3, 40.0):
        Q = lc.model1_two_path(S.P_IN, *g, G)["Q"]
        Q0 = lc.model1_two_path(S.P_IN, *g, 0.0)["Q"]
        got = S.invert_G_from_known_axials(g, Q / Q0)
        assert got["status"] == "ok"
        assert got["G_lat_hat"] == pytest.approx(G, rel=1e-9)
        assert S._bisect_G(g, Q) == pytest.approx(G, rel=1e-6)


# ------------------------------------------------------------------------------------------
# the calibrated route is NOT valid for "any geometry" — the structural degeneracy
# ------------------------------------------------------------------------------------------

DEGENERATE_GEOMETRIES = [(2.0, 1.0, 4.0, 2.0), (1.0, 3.0, 2.0, 6.0), (5.0, 2.0, 2.5, 1.0)]


def test_derivative_numerator_is_the_squared_cross_product():
    """d(Q/P)/dG = [M*A1*A2 - N0*S]/(...)^2 = (g1t*g2b - g2t*g1b)^2/(...)^2.
    (Requirement 3.) Checked symbolically-by-value on a deterministic spread of geometries."""
    geoms = [(3.0, 1.0, 1.0, 3.0), (4.0, 0.8, 1.5, 2.5), (2.0, 1.0, 4.0, 2.0),
             (0.5, 7.0, 1.25, 0.3), (9.0, 9.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0)]
    for g in geoms:
        X = S.cross_product_gap_driver(g)
        assert S.dQdG_numerator(g) == pytest.approx(X * X, rel=1e-9, abs=1e-9)
    # and it really is the derivative: finite-difference Q/P against the closed form
    for g in geoms[:4]:
        A1, A2 = g[0] + g[1], g[2] + g[3]
        Sm = A1 + A2
        for G in (0.3, 2.0, 11.0):
            h = 1e-5
            qp = lambda x: lc.model1_two_path(S.P_IN, *g, x)["Q"] / S.P_IN
            num = (qp(G + h) - qp(G - h)) / (2 * h)
            closed = S.dQdG_numerator(g) / (A1 * A2 + G * Sm) ** 2
            # abs floor is the round-off of a difference quotient (~eps/h ~ 1e-11), not a
            # scientific tolerance; the nondegenerate closed values are O(0.1), so it still bites
            assert num == pytest.approx(closed, rel=1e-5, abs=1e-9)


def test_proportional_paths_are_structurally_degenerate():
    """Requirement 1: non-identical paths with EXACTLY equal uncoupled mid-node pressure. Q is
    exactly invariant in G_lat and the calibrated inversion must report no information."""
    for g in DEGENERATE_GEOMETRIES:
        assert S.cross_product_gap_driver(g) == 0.0, "must be EXACTLY zero, not merely small"
        assert S.dQdG_numerator(g) == 0.0
        assert g[0] != g[2] or g[1] != g[3], "these must be NON-identical paths"
        blocked = lc.model1_two_path(S.P_IN, *g, 0.0)
        assert blocked["p1"] == blocked["p2"], "exactly equal, not approximately"
        Q0 = blocked["Q"]
        for G in (0.0, 0.5, 5.0, 500.0, 1e6):
            r = lc.model1_two_path(S.P_IN, *g, G)
            assert r["Q"] == Q0, "Q must be EXACTLY independent of G_lat here"
            assert r["q_lat_1to2"] == 0.0
            got = S.invert_G_from_known_axials(g, r["Q"] / Q0)
            assert got["status"] == "structurally_degenerate_no_information"
            assert got["G_lat_hat"] is None
            assert got["structurally_degenerate"] is True


def test_small_nonzero_X_is_numerically_unresolved_NOT_structurally_degenerate():
    """The conflation this correction removes.

    g = (2, 1, 4, 2.000001) has X != 0. The map is therefore mathematically INJECTIVE and Q is
    NOT independent of G_lat -- the uncoupled mid-node pressures are provably UNEQUAL. Labelling
    it a structural degeneracy would assert a falsehood. It must return a distinct
    numerical-resolution status, and its wording must claim neither exact equality nor exact
    Q-independence.
    """
    g = (2.0, 1.0, 4.0, 2.000001)
    X = S.cross_product_gap_driver(g)
    assert X != 0.0, "the whole point: X is nonzero"
    assert S.dQdG_numerator(g) > 0.0, "derivative numerator is strictly positive"
    assert S.dQdG_numerator(g) == pytest.approx(X * X, rel=1e-9)

    blocked = lc.model1_two_path(S.P_IN, *g, 0.0)
    assert blocked["p1"] != blocked["p2"], "the uncoupled pressures are NOT equal"
    Q0 = blocked["Q"]
    spans = [lc.model1_two_path(S.P_IN, *g, G)["Q"] for G in (0.0, 5.0, 500.0)]
    assert max(spans) != min(spans), "Q is NOT exactly independent of G_lat"

    got = S.invert_G_from_known_axials(g, spans[1] / Q0)
    assert got["status"] == "numerically_unresolved_near_degenerate"
    assert got["status"] != "structurally_degenerate_no_information"
    assert got["G_lat_hat"] is None, "no unreliable estimate may be returned"
    assert got["structurally_degenerate"] is False
    why = got["why"]
    assert "mathematically injective" in why.lower()
    assert "NOT independent" in why
    assert "NUMERICAL" in why
    for forbidden in ("EXACTLY", "exactly independent", "are equal"):
        assert forbidden not in why, "must not claim exactness: %r" % forbidden


def test_the_two_statuses_are_never_conflated_in_the_bundle(result):
    cd = result["arm_f_mirror_imperfection"]["calibrated_inversion_degeneracy"]
    assert cd["structurally_degenerate_rows_report_no_information"] is True
    assert cd["numerically_unresolved_rows_report_that_and_not_degeneracy"] is True
    assert cd["no_row_is_both"] is True
    assert "three_classes_never_two" in cd
    struct = [r for r in cd["rows"] if r["structurally_degenerate"]]
    unres = [r for r in cd["rows"] if r["numerically_unresolved"]]
    assert struct and unres, "both classes must be exhibited"
    for r in struct:
        assert r["cross_product_X"] == 0.0
        assert r["mathematically_injective"] is False
        assert r["Q_exactly_independent_of_G_lat"] is True
        assert r["uncoupled_mid_node_gap"] == 0.0
    for r in unres:
        assert r["cross_product_X"] != 0.0
        assert r["mathematically_injective"] is True, "still one-to-one"
        assert r["Q_exactly_independent_of_G_lat"] is False
        assert r["uncoupled_mid_node_gap"] > 0.0, "pressures are NOT equal here"


def test_the_threshold_is_named_as_numerical_not_structural():
    import inspect
    src = inspect.getsource(S)
    assert "_NUMERICAL_RESOLUTION_REL" in src
    assert "_DEGEN_REL" not in src, "the old structural-degeneracy name must be gone"
    assert S._NUMERICAL_RESOLUTION_REL > 0.0


def test_bundle_records_the_degeneracy_and_its_conditioning(result):
    cd = result["arm_f_mirror_imperfection"]["calibrated_inversion_degeneracy"]
    assert cd["identity_verified_on_all_rows"] is True
    assert cd["structurally_degenerate_rows_report_no_information"] is True
    assert cd["well_conditioned_rows_recover_exactly"] is True
    assert any(r["structurally_degenerate"] for r in cd["rows"]), (
        "the structurally degenerate case must be exhibited")
    for r in cd["rows"]:
        if r["structurally_degenerate"]:
            assert r["Q_exactly_independent_of_G_lat"] is True
            assert r["uncoupled_mid_node_gap"] == 0.0
    # conditioning decays continuously rather than failing abruptly
    dec = cd["near_degenerate_conditioning_decay"]
    assert dec["max_rel_err"] > 100 * max(dec["well_conditioned_max_rel_err"], 1e-15)


def test_no_output_claims_the_calibrated_route_works_for_any_geometry(result):
    """The corrected wording must be everywhere, and the old wording nowhere."""
    blob = json.dumps(result)
    assert "ANY geometry" not in blob and "for any geometry" not in blob
    for name in ("decision.md", "README.md", "DECISIVE_EXPERIMENT.md"):
        text = (BUNDLE / name).read_text(encoding="utf-8")
        bad = [ln for ln in text.splitlines()
               if "any geometry" in ln.lower() and "not" not in ln.lower()]
        assert bad == [], "%s still claims 'any geometry': %s" % (name, bad)
    card = (REPO / "docs/cards/lateral_coupling_feasibility.md").read_text(encoding="utf-8")
    assert "for **any** geometry" not in card
    assert "nondegenerate" in card.lower()


def test_protocol_carries_a_post_execution_erratum_and_frozen_text_is_intact():
    """The historical pre-execution statement is NOT rewritten; the correction is appended."""
    text = (BUNDLE / "PROTOCOL.md").read_text(encoding="utf-8")
    assert "POST-EXECUTION FACTUAL ERRATUM" in text
    # the original (incomplete) frozen sentence is still present, unedited
    assert "a Möbius function of `G`, hence invertible" in text
    assert "g1_top·g2_bot − g2_top·g1_bot" in text
    assert "does not affect the mirror result" in text.lower() or \
           "It does not affect the mirror result" in text


def test_blocked_share_flags_the_biasing_corners_on_this_corner_set(result):
    for lv in result["arm_f_mirror_imperfection"]["levels"]:
        assert lv["blocked_share_flags_exactly_the_biasing_corners"] is True
        assert lv["n_corners_still_exact_mirrors"] == 4


def test_post_hoc_counting_exhibits_real_boundary_indistinguishable_alternatives(result):
    """The diagnostic must be a demonstration, not a claim: distinct geometries, same four
    boundary flows, different Xi -- and invisible to the blocked-share test."""
    u = (result["arm_f_mirror_imperfection"]["post_hoc_diagnostics"]
         ["unconstrained_geometry_non_identifiability"])
    assert u["n_solutions_found"] >= 3
    assert u["Xi_spread_factor"] > 2.0
    assert u["all_solutions_have_blocked_share_one_half"] is True
    gs = [tuple(x["g"]) for x in u["solutions"]]
    assert len(set(gs)) == len(gs), "the 'family' must contain genuinely distinct geometries"


def test_post_hoc_diagnostics_are_labelled_and_feed_no_decision_clause(result):
    ph = result["arm_f_mirror_imperfection"]["post_hoc_diagnostics"]
    assert ph["label"] == "POST_HOC_DIAGNOSTIC_NOT_IN_DECISION"
    blob = json.dumps(result["decision_record"])
    for token in ("blocked_share", "post_hoc", "unconstrained_geometry"):
        assert token not in blob


# ------------------------------------------------------------------------------------------
# sensitivity scenarios are scenarios, and the frozen decision rule is a rule
# ------------------------------------------------------------------------------------------

def test_sensitivity_scenarios_are_labelled_as_scenarios(result):
    s = result["sensitivity_envelopes"]
    assert s["not_instrument_accuracies"] is True
    assert s["not_experimental_uncertainty"] is True
    assert s["no_apparatus_feasibility_claim_is_earned"] is True
    assert s["derivative_cross_check_passes"] is True
    assert [r["floor"] for r in
            [s["rows"][0]["scenarios"][k] for k in ("1pct", "2pct", "5pct")]] == [0.01, 0.02, 0.05]


def test_analytic_sensitivity_peaks_are_where_the_algebra_says():
    """peak dR/dlnXi at Xi = 1; peak |ds/dlnXi| at Xi = 1 - c^2."""
    c = S.C_PRIMARY
    dR = lambda Xi: (c * c / (1 - c * c)) * Xi / (1 + Xi) ** 2
    ds = lambda Xi: abs(-(c / 2.0) * Xi * (1 - c * c) / (1 + Xi - c * c) ** 2)
    assert dR(1.0) == pytest.approx((c * c / (1 - c * c)) / 4.0)
    assert ds(1.0 - c * c) == pytest.approx(c / 8.0)
    for x in (0.01, 0.3, 3.0, 100.0):
        assert dR(x) <= dR(1.0) + 1e-15
        assert ds(x) <= ds(1.0 - c * c) + 1e-15


def test_resolution_requirement_is_finite_and_tightens_with_the_floor(result):
    w = result["sensitivity_envelopes"]["well_conditioned_windows"]
    assert w["1pct"]["n_grid_points_recoverable"] > 0, (
        "a finite resolution requirement must be calculable, else the rule routes to "
        "NEEDS_NEW_DATA")
    assert (w["1pct"]["n_grid_points_recoverable"]
            >= w["2pct"]["n_grid_points_recoverable"]
            >= w["5pct"]["n_grid_points_recoverable"])


def test_dropped_scenario_corners_are_counted_not_silently_capped(result):
    """The [Xi_hat_min, Xi_hat_max] band spans only the corners that returned a physical
    inverse, so where corners were dropped the true spread is WORSE than reported. That must be
    recorded, and the factor-of-two flag must not benefit from a dropped corner."""
    se = result["sensitivity_envelopes"]
    for key, w in se["well_conditioned_windows"].items():
        assert "n_grid_points_with_unrecoverable_corners" in w
        assert w["n_grid_points_with_unrecoverable_corners"] == len(
            w["Xi_with_unrecoverable_corners"])
        assert w["interval_is_optimistic_where_corners_were_dropped"] == bool(
            w["Xi_with_unrecoverable_corners"])
    # the flag requires ALL 27 corners physical, so it can never be earned by dropping one
    for r in se["rows"]:
        for key, sc in r["scenarios"].items():
            if sc["n_nonphysical_or_undefined"] > 0:
                assert sc["recovered_within_factor_two"] is False
            assert sc["n_scenario_points"] == 27
    # and the effect is real here, not hypothetical
    assert se["well_conditioned_windows"]["5pct"]["n_grid_points_with_unrecoverable_corners"] > 0


def test_the_observable_hierarchy_is_demonstrated_not_asserted(result):
    """Each rung must be exercised on the exact model, including the rung that shows R ALONE is
    sufficient when c is known -- the fact that qualifies the confounding claim."""
    h = result["arm_c_minimum_observable"]["observable_hierarchy"]
    assert [r["rung"] for r in h] == [1, 2, 3, 4]
    assert h[0]["identifies"] == ["Xi"] and h[0]["rel_err"] <= 1e-9
    assert h[1]["identifies"] == ["c", "Xi"] and h[1]["rel_err"] <= 1e-9
    assert h[2]["identifies"] == ["G_lat"] and h[2]["rel_err"] <= 1e-9
    assert h[3]["identifies"] == []
    assert "NONDEGENERATE" in h[2]["known"]
    # and the qualifier is carried in the claim text itself
    c_arm = result["arm_c_minimum_observable"]
    assert "not independently known" in c_arm["claim_stated_exactly"].lower()
    assert c_arm["Q_only_confounding_is_for_JOINT_inference_of_c_and_Xi"] is True


def test_R_alone_identifies_Xi_when_c_is_known(result):
    """Independent of the artifact: the rung-1 claim, computed here."""
    c = S.C_PRIMARY
    for Xi in (0.05, 0.75, 19.0):
        o = S.observables_exact(S.A_PRIMARY, c, Xi)
        t = (1.0 - o["R"] * (1.0 - c * c)) / (c * c)
        assert 1.0 / t - 1.0 == pytest.approx(Xi, rel=1e-9)


def test_continuous_window_diagnostic_is_post_hoc_and_brackets_the_grid(result):
    """The frozen grid says WHICH POINTS pass; the continuous crossings are a separate post-hoc
    solve. It must be labelled, feed no clause, and be consistent with the grid."""
    se = result["sensitivity_envelopes"]
    cw = se["continuous_window_post_hoc"]
    assert cw["label"] == "POST_HOC_DIAGNOSTIC_NOT_IN_DECISION"
    assert cw["feeds_no_decision_clause"] is True
    blob = json.dumps(result["decision_record"])
    assert "continuous_window" not in blob and "Xi_lower" not in blob

    one = cw["floors"]["1pct"]
    assert one["continuous_passing_interval_exists"] is True
    assert one["n_crossings"] == 2 and one["single_contiguous_interval"] is True
    lo, hi = one["Xi_lower"], one["Xi_upper"]
    # the continuous interval must CONTAIN every passing grid point and be strictly wider
    passing = [r["Xi"] for r in se["rows"]
               if r["scenarios"]["1pct"]["recovered_within_factor_two"]]
    assert len(passing) == 3
    assert lo < min(passing) and hi > max(passing)
    # no passing interval at the looser floors, confirmed independently of the grid
    for key in ("2pct", "5pct"):
        assert cw["floors"][key]["continuous_passing_interval_exists"] is False
        assert cw["floors"][key]["n_passing_scan_points"] == 0
    # the frozen grid result is reported UNCHANGED alongside
    assert se["well_conditioned_windows"]["1pct"]["n_grid_points_recoverable"] == 3
    assert "not a continuous boundary" in se["frozen_grid_note"].lower()


def test_no_output_quotes_the_grid_endpoints_as_a_continuous_window():
    for name in ("decision.md", "README.md", "DECISIVE_EXPERIMENT.md"):
        text = (BUNDLE / name).read_text(encoding="utf-8")
        for bad in ("[0.46, 2.15]", "Ξ ∈ [0.464, 2.15]", "0.46, 2.15]"):
            assert bad not in text, "%s quotes grid endpoints as an interval: %s" % (name, bad)
    card = (REPO / "docs/cards/lateral_coupling_feasibility.md").read_text(encoding="utf-8")
    assert "[0.46, 2.15]" not in card


def test_forward_map_agreement_is_described_as_floating_point_not_exact_zero(result):
    b = result["arm_b_forward_and_recovery"]
    assert b["forward_map_max_abs_error_log10_upper_bound"] <= -12, (
        "the live residual must be at machine-precision scale")
    assert b["forward_map_max_abs_error_log10_upper_bound"] is not None
    note = b["forward_map_error_is_floating_point_not_algebraic"]
    assert "floating-point" in note.lower() and "never as 'exactly zero'" in note
    # the live unrounded value really is nonzero at ~1e-14, recomputed here
    live = max(max(abs(S.forward_map_analytic(c, Xi)[0]
                       - S.observables_exact(S.A_PRIMARY, c, Xi)["R"]),
                   abs(S.forward_map_analytic(c, Xi)[1]
                       - S.observables_exact(S.A_PRIMARY, c, Xi)["s"]))
               for c in S.C_GRID for Xi in S.XI_GRID)
    assert 0.0 < live < 1e-12
    assert round(live, 12) == 0.0, "this is exactly why the rounded field reads 0.0"


def test_frozen_decision_rule_routes_other_inputs_correctly(result):
    """Exercise the rule on inputs OTHER than the live one, so it is a rule and not a label."""
    args = (result["arm_b_forward_and_recovery"], result["arm_c_minimum_observable"],
            result["arm_d_proxy_adversary"], result["arm_e_controls"],
            result["arm_f_mirror_imperfection"], result["sensitivity_envelopes"])
    assert S.decide(*args)["decision"] == "SURVIVE"

    # a broken control must RETIRE
    e_bad = copy.deepcopy(args[3])
    e_bad["path_swap"]["passes"] = False
    assert S.decide(args[0], args[1], args[2], e_bad, args[4], args[5])["decision"] == "RETIRE"

    # a non-injective map must RETIRE
    b_bad = copy.deepcopy(args[0])
    b_bad["injectivity_empirical"]["distinct"] = False
    assert S.decide(b_bad, *args[1:])["decision"] == "RETIRE"

    # an alpha-matchable proxy must RETIRE
    d_bad = copy.deepcopy(args[2])
    d_bad["no_proxy_reproduces_joint_signature"] = False
    assert S.decide(args[0], args[1], d_bad, *args[3:])["decision"] == "RETIRE"

    # identifiable but no calculable resolution requirement must be NEEDS_NEW_DATA
    s_bad = copy.deepcopy(args[5])
    for w in s_bad["well_conditioned_windows"].values():
        w["n_grid_points_recoverable"] = 0
    assert S.decide(*args[:5], s_bad)["decision"] == "NEEDS_NEW_DATA"


def test_licensed_claim_is_only_emitted_on_survive(result):
    dec = result["decision_record"]
    assert dec["decision"] == "SURVIVE"
    claim = dec["licensed_claim"]
    assert "structurally identifiable" in claim
    assert "not mathematically necessary" in claim
    assert "decompose or physically interpret" in claim
    assert len(dec["clauses"]) == 7 and all(c["passes"] for c in dec["clauses"])


# ------------------------------------------------------------------------------------------
# bundle: determinism, drift detection, hash binding, provenance
# ------------------------------------------------------------------------------------------

def test_screen_is_deterministic():
    a, b = S.screen(), S.screen()
    assert a["content_sha256"] == b["content_sha256"]
    assert a == b


def test_committed_result_matches_a_fresh_run(result):
    fresh = S.screen()
    assert fresh["content_sha256"] == result["content_sha256"]


def test_verify_detects_drift(tmp_path, result):
    stale, _ = S.verify()
    assert stale == [], "committed bundle is stale; run --write"
    p = BUNDLE / "result.json"
    original = p.read_text(encoding="utf-8")
    try:
        doc = json.loads(original)
        doc["decision"] = "RETIRE"
        p.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        stale, _ = S.verify()
        assert "result.json (drift)" in stale
    finally:
        p.write_text(original, encoding="utf-8")
    assert S.verify()[0] == []


def test_result_is_hash_bound_to_the_live_protocol_and_inputs(result):
    import hashlib
    proto = BUNDLE / "PROTOCOL.md"
    assert result["protocol"]["sha256"] == hashlib.sha256(proto.read_bytes()).hexdigest()
    for rel, recorded in result["load_bearing_source_hashes"].items():
        got = hashlib.sha256((REPO / rel).read_bytes()).hexdigest()
        assert got == recorded, "load-bearing input %s changed since the screen ran" % rel


def test_protocol_commit_precedes_every_result_producing_commit():
    if _git("rev-parse", "--is-shallow-repository").stdout.strip() == "true":
        pytest.skip("shallow checkout: per-path commit order is not observable")

    def commits(path):
        return _git("log", "--format=%H", "--", path).stdout.split()
    proto = commits("docs/insights/screens/WP6-LC-IDENT/PROTOCOL.md")
    if not proto:
        pytest.skip("protocol not yet committed (working-tree run)")
    results = []
    for rel in ("docs/insights/screens/WP6-LC-IDENT/result.json",
                "puckworks/analysis/screen_wp6_lateral_identifiability.py",
                "docs/insights/screens/WP6-LC-IDENT/decision.md"):
        results += commits(rel)
    if not results:
        pytest.skip("no result-producing commit yet")
    order = _git("log", "--format=%H").stdout.split()
    pos = {h: i for i, h in enumerate(order)}
    assert (max(pos[h] for h in proto if h in pos)
            > max(pos[h] for h in results if h in pos)), (
        "the protocol commit must be OLDER than the first result-producing commit")


def test_bundle_carries_the_four_labels_everywhere():
    for name in ("PROTOCOL.md", "README.md", "decision.md", "DECISIVE_EXPERIMENT.md"):
        p = BUNDLE / name
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        for label in ("HUMAN_SELECTED_POST_SNAPSHOT", "CHEAP_SCIENTIFIC_SCREEN",
                      "NOT_A_PUBLICATION_RESULT", "NOT_A_MODEL_VALIDATION_UPGRADE"):
            assert label in text, "%s is missing %s" % (name, label)


def test_claim_ceiling_refuses_the_things_it_must(result):
    ceiling = result["claim_ceiling"]
    for phrase in ("NOT empirical validation", "no evidence rung", "no real-puck Xi",
                   "not instrument accuracies", "Paper 4 is NOT authorized"):
        assert phrase.lower() in ceiling.lower(), "claim ceiling is missing: %s" % phrase
    assert result["paper_4_authorized"] is False
    assert result["evidence_labels_unchanged"] is True


def test_no_foundry_infrastructure_was_added_or_modified(result):
    """The append-only registry, the candidate records and the layer's CODE must be untouched.

    `docs/insights/generated/**` is deliberately NOT asserted byte-equal: the card correction
    this screen earned is an input the corpus map hashes, so `insights verify` requires a
    regeneration. What must not move is the SUBSTANCE -- see the companion test below.
    """
    flags = result["foundry_infrastructure_unchanged"]
    for k in ("lens_added_or_changed", "generator_added_or_changed", "scoring_added",
              "candidate_portfolio_content_changed", "candidate_added_or_removed",
              "candidate_scored", "id_registry_changed", "generated_artifacts_hand_edited"):
        assert flags[k] is False, k
    assert flags["generated_artifacts_regenerated"] is True, (
        "the regeneration must be declared, not hidden behind an unchanged flag")
    base = result["source_commit"]
    if _git("cat-file", "-e", base + "^{commit}").returncode != 0:
        pytest.skip("base commit unavailable")
    for path in ("docs/insights/ID_REGISTRY.json", "docs/insights/candidates",
                 "puckworks/insights"):
        out = _git("diff", "--numstat", base, "HEAD", "--", path).stdout.strip()
        assert out == "", "%s must be byte-unchanged by this screen, got:\n%s" % (path, out)


# Provenance fields the sanctioned regeneration is ALLOWED to move. Everything else in the
# generated payload must compare equal after these are stripped. Keep this list minimal: it is
# the whole strength of the check.
_PROVENANCE_KEYS = {"source_commit", "commit"}


#: Inputs to the Insight Foundry snapshot that a LATER, separately-reviewed change moved, so this
#: historical proof does not fail on every subsequent regeneration. 2026-08-14 (#73): the Grudeva rights
#: correction — direct written permission recorded in place of the RIGHTS_BLOCKED determination. It moved
#: rights PROSE and rights COLUMNS only; the entity-field assertion below is what keeps the allowance from
#: hiding anything scientific.
_RIGHTS_CORRECTION_INPUTS = {
    "docs/cards/grudeva2025.md",
    "docs/cards/grudeva2026_2.md",
    "puckworks/data/MANIFEST.csv",
}
#: entity id -> the exact attribute set it is permitted to move in, for the same correction
_RIGHTS_CORRECTION_ENTITIES = {
    "card:grudeva2025": {"card_sha256"},
    "card:grudeva2026_2": {"card_sha256", "section_hashes"},
    "dataset:grudeva2025/exp13_vial_stats": {"caveat", "license_access"},
    "dataset:grudeva2025/params": {"caveat"},
    "model:grudeva2025.reduced": {"notes"},
}


def _strip_provenance(obj):
    """Deep-normalise a generated payload by removing provenance stamps at every depth."""
    if isinstance(obj, dict):
        return {k: _strip_provenance(v) for k, v in obj.items() if k not in _PROVENANCE_KEYS}
    if isinstance(obj, list):
        return [_strip_provenance(v) for v in obj]
    return obj


def _baseline_json(base, rel):
    out = _git("show", "%s:%s" % (base, rel))
    return json.loads(out.stdout) if out.returncode == 0 else None


def test_regeneration_moved_only_provenance_deep_payload_comparison(result):
    """The regeneration forced by the card correction may refresh PROVENANCE and nothing else.

    This is a DEEP normalised comparison of the complete generated payloads, not a check on
    counts and summaries: strip `source_commit`/`commit` at every depth, allow the corrected
    card's input hash and the resulting output hashes in the manifest, and require everything
    else to compare EQUAL. Counts alone would not catch a reworded candidate, a changed
    discriminator, a moved status or a newly written score.
    """
    base = result["source_commit"]
    if _git("cat-file", "-e", base + "^{commit}").returncode != 0:
        pytest.skip("base commit unavailable")

    # ---- candidate portfolio: complete payload, deep-normalised -----------------------------
    rel = "docs/insights/generated/candidate_portfolio.json"
    before = _baseline_json(base, rel)
    if before is None:
        pytest.skip("baseline portfolio unavailable")
    after = json.loads((REPO / rel).read_text(encoding="utf-8"))
    assert _strip_provenance(after) == _strip_provenance(before), (
        "the candidate payload changed beyond provenance")
    assert len(after["candidates"]) == 90
    assert {c["status"] for c in after["candidates"]} == {"SEED"}
    assert all(not c.get("scores") for c in after["candidates"]), "no candidate may be scored"

    # ---- tension atlas: complete payload, deep-normalised ------------------------------------
    import csv
    import io
    rel_t = "docs/insights/generated/tension_atlas.csv"
    old_t = _git("show", "%s:%s" % (base, rel_t))
    if old_t.returncode == 0:
        rows_b = list(csv.DictReader(io.StringIO(old_t.stdout)))
        rows_a = list(csv.DictReader(
            io.StringIO((REPO / rel_t).read_text(encoding="utf-8"))))
        assert len(rows_a) == len(rows_b) == 171
        assert ([_strip_provenance(r) for r in rows_a]
                == [_strip_provenance(r) for r in rows_b]), (
            "the tension payload changed beyond provenance")
        assert {r["human_status"] for r in rows_a} == {"UNREVIEWED"}

    # ---- snapshot manifest: SENTINEL-SUBSTITUTED WHOLE-OBJECT comparison ---------------------
    # Not a field-by-field spot check. Everything not explicitly normalised must compare equal,
    # so counts, generator_version, pack, repository, schema_version, every unmodified input
    # path/hash, every output path AND its ordering, and any future top-level field are all
    # protected without being enumerated here.
    rel_m = "docs/insights/generated/snapshot_manifest.json"
    man_b = _baseline_json(base, rel_m)
    if man_b is not None:
        man_a = json.loads((REPO / rel_m).read_text(encoding="utf-8"))
        a, b = copy.deepcopy(man_a), copy.deepcopy(man_b)

        # (2) top-level snapshot commit is provenance
        a.pop("commit", None)
        b.pop("commit", None)

        # (3) identical input path SETS, and the moved-input set is exactly the corrected card
        pa = [i["path"] for i in a["inputs"]]
        pb = [i["path"] for i in b["inputs"]]
        assert pa == pb, "input paths (and their order) must be identical"
        hb = {i["path"]: i["sha256"] for i in b["inputs"]}
        ha = {i["path"]: i["sha256"] for i in a["inputs"]}
        moved_inputs = {p for p in ha if ha[p] != hb[p]}
        assert moved_inputs == {"docs/cards/lateral_coupling_feasibility.md"} | _RIGHTS_CORRECTION_INPUTS, (
            "the moved-input set must be exactly the corrected card plus the separately-reviewed "
            "rights-correction inputs, got: %s" % moved_inputs)

        # (4) sentinel those input hashes in BOTH manifests
        for man in (a, b):
            for i in man["inputs"]:
                if i["path"] == "docs/cards/lateral_coupling_feasibility.md":
                    i["sha256"] = "<SENTINEL-CORRECTED-CARD>"
                elif i["path"] in _RIGHTS_CORRECTION_INPUTS:
                    i["sha256"] = "<SENTINEL-RIGHTS-CORRECTION-INPUT>"

        # (5) identical output path lists INCLUDING ORDER
        assert [o["path"] for o in a["outputs"]] == [o["path"] for o in b["outputs"]], (
            "output paths and their ordering must be identical")

        # (6) sentinel every output hash in both (they are derived from the above)
        for man in (a, b):
            for o in man["outputs"]:
                o["sha256"] = "<SENTINEL-DERIVED-OUTPUT>"

        # (7) the COMPLETE remaining objects must be equal
        assert a == b, "snapshot_manifest changed beyond the permitted provenance fields"

    # ---- corpus map: ONLY the corrected card's own entity attrs may move ---------------------
    # This one is NOT pure provenance: the corpus map records the card's content, so correcting
    # the card legitimately moves that card's hash and section list. Nothing else may move --
    # no other entity, no relation, no warning, no count.
    rel_c = "docs/insights/generated/corpus_map.json"
    cm_b = _baseline_json(base, rel_c)
    if cm_b is not None:
        cm_a = json.loads((REPO / rel_c).read_text(encoding="utf-8"))
        assert cm_a["counts"] == cm_b["counts"]
        assert _strip_provenance(cm_a["relations"]) == _strip_provenance(cm_b["relations"])
        assert _strip_provenance(cm_a["warnings"]) == _strip_provenance(cm_b["warnings"])
        eb = {e["id"]: e for e in cm_b["entities"]}
        ea = {e["id"]: e for e in cm_a["entities"]}
        assert set(ea) == set(eb), "no entity may be added or removed"
        moved = {i for i in ea if _strip_provenance(ea[i]) != _strip_provenance(eb[i])}
        assert moved == {"card:lateral_coupling_feasibility"} | set(_RIGHTS_CORRECTION_ENTITIES), (
            "only the corrected card's entity and the separately-reviewed rights-correction entities "
            "may move, but these did: %s" % moved)
        # the rights-correction entities may move ONLY in rights-descriptive / content-hash fields.
        # A scientific field moving here (evidence_strength, provenance_class, valid_range, units,
        # validation_strength, gate_use, ...) would be caught, not hidden by the allowance.
        for eid, allowed in _RIGHTS_CORRECTION_ENTITIES.items():
            fields = {k for k in set(ea[eid]["attrs"]) | set(eb[eid]["attrs"])
                      if ea[eid]["attrs"].get(k) != eb[eid]["attrs"].get(k)}
            assert fields == allowed, "%s moved in unexpected fields: %s" % (eid, sorted(fields))
        one_a, one_b = ea["card:lateral_coupling_feasibility"], eb["card:lateral_coupling_feasibility"]
        moved_fields = {k for k in set(one_a["attrs"]) | set(one_b["attrs"])
                        if one_a["attrs"].get(k) != one_b["attrs"].get(k)}
        assert moved_fields == {"card_sha256", "section_names", "section_hashes"}, (
            "only the card's own content fields may move, got: %s" % moved_fields)
        # and the movement is exactly the new section -- nothing removed, nothing renamed
        added = set(one_a["attrs"]["section_names"]) - set(one_b["attrs"]["section_names"])
        removed = set(one_b["attrs"]["section_names"]) - set(one_a["attrs"]["section_names"])
        assert removed == set(), "no card section may disappear"
        assert len(added) == 1 and added.pop().startswith("3b."), (
            "the only new section must be the screen's §3b")


def test_provenance_strip_list_is_minimal():
    """Guard the guard: if _PROVENANCE_KEYS grew, the comparison above would weaken silently."""
    assert _PROVENANCE_KEYS == {"source_commit", "commit"}
    # and stripping must not remove anything scientific from a representative record
    rel = REPO / "docs/insights/generated/candidate_portfolio.json"
    one = json.loads(rel.read_text(encoding="utf-8"))["candidates"][0]
    stripped = _strip_provenance(one)
    for k in ("id", "status", "scores"):
        assert k in stripped, "%s must survive provenance stripping" % k


def test_the_existing_lateral_coupling_layer_is_byte_unchanged(result):
    """The screen may not modify the model, the harness, the proxy or the card while landing."""
    base = result["source_commit"]
    if _git("cat-file", "-e", base + "^{commit}").returncode != 0:
        pytest.skip("base commit unavailable")
    for path in ("puckworks/models/lateral_coupling.py",
                 "puckworks/analysis/lateral_coupling_discrimination.py",
                 "puckworks/analysis/lateral_proxy.py",
                 "docs/analysis/generated/lateral_coupling_discrimination.json"):
        out = _git("diff", "--numstat", base, "HEAD", "--", path).stdout.strip()
        assert out == "", "%s must be byte-unchanged, got:\n%s" % (path, out)


def test_screen_uses_Xi_not_the_legacy_lambda_labels(result):
    """The primary result must be about Xi. Lambda may appear only as a harness input name."""
    blob = json.dumps(result)
    for banned in ("uncoupled", "transitional", "homogenized"):
        assert '"%s"' % banned not in blob, "legacy Lambda regime label leaked: %s" % banned
    assert "Xi = G_lat*(1/A1 + 1/A2)" in result["primary_quantity"]
