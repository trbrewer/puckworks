"""Synthetic/model-query verification; independent mathematics, no empirical scoring."""
from dataclasses import FrozenInstanceError, asdict, replace
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import warnings

import numpy as np
import pytest
from scipy.integrate import IntegrationWarning, quad
from scipy.optimize import brentq
from scipy.special import expit

from puckworks.analysis import conditional_tail_delivery as f
from puckworks.analysis import conditional_tail_envelope as e
from puckworks.analysis import conditional_tail_stopping as s
from puckworks.analysis import conditional_tail_robust_stopping as r

MODELS = Path(__file__).resolve().parents[1] / 'docs/analysis/sci_md_mass_delivery_006/models'
RECORDS = []


@pytest.fixture(autouse=True)
def accounting(monkeypatch):
    original = r.solve_robust_stopping_ranges
    def recorded(model, box, query, **kwargs):
        result = original(model, box, query, **kwargs)
        RECORDS.append(dict(case=f.identity([model.sha256, box.to_dict(), query.to_dict()]),
            status=result.status, extent=result.achieved_unresolved_neighborhood_kg,
            qualified=result.resolution_qualified, resources=asdict(result.resources),
            feasible=[asdict(z) for z in result.feasible_regions],
            excluded=[asdict(z) for z in result.excluded_regions],
            unresolved=[asdict(z) for z in result.unresolved_regions]))
        if path := os.environ.get('ROBUST_ACCOUNTING_FILE'):
            with open(path, 'w') as stream:
                json.dump(RECORDS, stream, indent=2)
        return result
    monkeypatch.setattr(r, 'solve_robust_stopping_ranges', recorded)


def manufactured(arm='C2', intercepts=(-2.,) * 5, columns=None):
    model = f.synthetic_model(arm)
    n = len(model.means) - 2
    columns = columns if columns is not None else [(1.,) * 5] * n
    return replace(model, means=(.004, .004, .5, .5)[:n+2],
        minima=(.002, .002, 0., 0.)[:n+2], maxima=(.008, .008, 1., 1.)[:n+2],
        theta=tuple((a, 0., 0., *(col[k] * .1 for col in columns)) for k, a in enumerate(intercepts)))


def box_for(model, bounds=None):
    bounds = bounds if bounds is not None else [(q, q) for q in model.means[2:]]
    return e.AssayBox(model.arm, *model.means[:2], input_class='SYNTHETIC',
                      **dict(zip(f.feature_names(model.arm)[2:], bounds)))


def independent_logits(model, values):
    return tuple(math.fsum([row[0], *(t * ((x - mu) / scale)
        for t, x, mu, scale in zip(row[1:], values, model.means, f.SCALES))])
        for row in model.theta)


def integral(model, values, b, derivative=None, refined=True):
    """Adaptive quadrature of affine hats, NEVER the production integration kernel."""
    logits = independent_logits(model, values)
    totals, errors = [], []
    for k in range(4):
        left, right = model.domain_kg*k/4, model.domain_kg*(k+1)/4
        lo, hi = max(sum(values[:2]), left), min(b, right)
        if lo >= hi:
            continue
        cuts = (lo, lo+(hi-lo)/2, hi) if refined else (lo, hi)
        for start, end in zip(cuts, cuts[1:]):
            def fun(t):
                alpha = (start+(end-start)*t-left)/(right-left)
                c = expit((1-alpha)*logits[k] + alpha*logits[k+1])
                if derivative is not None:
                    col = derivative+3
                    beta = ((1-alpha)*model.theta[k][col]+alpha*model.theta[k+1][col])/.1
                    c *= (1-c)*beta
                return (end-start)*c
            value, error = quad(fun, 0., 1., epsabs=1e-16, epsrel=3e-14, limit=200)
            totals.append(value)
            errors.append(error)
    return math.fsum(totals), math.fsum(errors)+2e-17


def reference_set(model, box, query, minimum_values, maximum_values):
    """Provably monotone assay fixtures: enumerate residual stationary cuts.

    Derivative roots are independently bracketed on each original segment;
    scalar residual roots are then bracketed on every monotone piece. No grid.
    """
    a, b = query.stop_min_kg, query.stop_max_kg
    anchor = box.anchor_kg
    predicates, roots = [], []
    for name in r._LIMITS:
        limit = getattr(query, name)
        if limit is None:
            continue
        lower = '_min_' in name
        values = minimum_values if lower else maximum_values
        tds = 'tds' in name
        def residual(x, values=values, limit=limit, tds=tds):
            return integral(model, values, x)[0] - (limit/100*(x-anchor) if tds else limit)
        predicates.append((residual, lower))
        knots = [model.domain_kg*k/4 for k in range(5)]
        logits = independent_logits(model, values)
        cuts = sorted({a, b, *(v for v in knots if a < v < b)})
        if tds:
            def derivative(x):
                return expit(np.interp(x, knots, logits)) - limit/100
            extra = []
            for lo, hi in zip(cuts, cuts[1:]):
                if derivative(lo)*derivative(hi) < 0:
                    extra.append(brentq(derivative, lo, hi, xtol=1e-15))
            cuts = sorted(set(cuts+extra))
        roots.extend(x for x in cuts if residual(x) == 0.)
        for lo, hi in zip(cuts, cuts[1:]):
            if residual(lo)*residual(hi) < 0:
                roots.append(brentq(residual, lo, hi, xtol=1e-15))
    cuts = sorted({a, b, *roots})
    expected = []
    for lo, hi in zip(cuts, cuts[1:]):
        x = lo+(hi-lo)/2
        if all(fun(x) >= 0 if lower else fun(x) <= 0 for fun, lower in predicates):
            if expected and expected[-1][1] == lo:
                expected[-1] = (expected[-1][0], hi)
            else:
                expected.append((lo, hi))
    return expected


def check_partition(result):
    groups = (result.feasible_regions, result.excluded_regions, result.unresolved_regions)
    all_regions = sum(groups, ())
    q = result.query
    cuts = sorted({q.stop_min_kg, q.stop_max_kg,
                   *(v for z in all_regions for v in (z.lower_kg, z.upper_kg))})
    for x in cuts:
        assert sum(r._contains(z, x, x, True) for z in all_regions) == 1
    for lo, hi in zip(cuts, cuts[1:]):
        assert sum(r._contains(z, lo, hi, False) for z in all_regions) == 1
    assert cuts[0] == q.stop_min_kg and cuts[-1] == q.stop_max_kg
    for regions in groups:
        assert r._merge(regions) == regions
    assert r._merge((*result.feasible_regions, *result.unresolved_regions)) == result.outer_possible_feasible_regions
    use, options = result.resources, result.options
    assert (use.mass_subdivisions + use.point_inverse_mass_refinements_reserved
            <= options.max_mass_subdivisions)
    assert use.envelope_calls <= options.max_envelope_calls
    assert use.parent_delivery_evaluations <= options.max_parent_evaluations
    assert use.assay_subdivisions <= use.envelope_calls*options.max_assay_subdivisions_per_call
    assert use.tighter_envelope_calls <= use.envelope_calls
    if result.status == 'NO_ROBUST_FEASIBLE_RANGE':
        assert not result.outer_possible_feasible_regions and not result.unresolved_regions


def agrees(result, expected, qualified=True):
    check_partition(result)
    tol = 3e-12  # Independent scalar bracketing/reference allowance, not API tolerance.
    for z in result.feasible_regions:
        assert any(a-tol <= z.lower_kg <= z.upper_kg <= b+tol for a, b in expected)
    for z in result.excluded_regions:
        assert all(min(z.upper_kg, b)-max(z.lower_kg, a) <= tol for a, b in expected)
    for a, b in expected:
        assert any(z.lower_kg-tol <= a <= b <= z.upper_kg+tol
                   for z in result.outer_possible_feasible_regions)
        if a == b:
            assert not any(r._contains(z, a, a, True) for z in result.excluded_regions)
    if qualified:
        assert result.resolution_qualified, (result.status, result.unresolved_regions, result.resources)
        assert result.achieved_unresolved_neighborhood_kg <= result.options.mass_resolution_kg


def frozen_case():
    model = f.Model.load(MODELS/'C2.json')
    box = box_for(model, [(model.means[2],)*2, (.0931364597, .1830244866)])
    return model, box


def frozen_minimum(model, box, b):
    lo, hi = box.bounds[1]
    def derivative(x):
        return integral(model, (*model.means[:3], x), b, derivative=1)[0]
    if b == box.anchor_kg or derivative(lo) >= 0:
        q2 = lo
    elif derivative(hi) <= 0:
        q2 = hi
    else:
        q2 = brentq(derivative, lo, hi, xtol=5e-16)
    return integral(model, (*model.means[:3], q2), b)[0], q2


def test_frozen_c2_continuous_lower_crossing_and_empty_combined_band():
    model, box = frozen_case()
    # eta < 0 throughout box and every mass segment => strict convexity in q2.
    for q2 in box.bounds[1]:
        assert max(independent_logits(model, (*model.means[:3], q2))) < 0
    assert any(row[4] != 0 for row in model.theta)
    lower = brentq(lambda b: frozen_minimum(model, box, b)[0]-.001640,
                   box.anchor_kg, model.domain_kg, xtol=5e-16)
    _, worst = frozen_minimum(model, box, lower)
    assert lower == pytest.approx(.041841172101, abs=1e-12)
    assert worst == pytest.approx(.143279333, abs=1e-9)
    endpoints = [(*model.means[:3], v) for v in box.bounds[1]]
    corner_lower = max(brentq(lambda b: integral(model, v, b)[0]-.001640,
        box.anchor_kg, model.domain_kg, xtol=5e-16) for v in endpoints)
    corner_upper = min(brentq(lambda b: integral(model, v, b)[0]-.001670,
        box.anchor_kg, model.domain_kg, xtol=5e-16) for v in endpoints)
    assert corner_lower == pytest.approx(.040487607612, abs=1e-12)
    assert corner_upper == pytest.approx(.041142221853, abs=1e-12)
    assert corner_lower < corner_upper < lower
    # Monotonic F: below lower, minimum misses; at/above lower, this endpoint
    # violates the upper bound. This proves emptiness over the entire domain.
    value, error = integral(model, endpoints[0], lower)
    first, first_error = integral(model, endpoints[0], lower, refined=False)
    assert abs(value-first) <= error+first_error
    assert value-error > .001670
    assert value == pytest.approx(.001701503133, abs=1e-12)
    query = s.StoppingQuery(box.anchor_kg, model.domain_kg, solute_min_kg=.001640)
    result = r.solve_robust_stopping_ranges(model, box, query)
    agrees(result, [(lower, model.domain_kg)])
    assert result.feasible_regions and result.excluded_regions
    assert len(result.unresolved_regions) == 1
    assert result.unresolved_regions[0].lower_kg <= lower <= result.unresolved_regions[0].upper_kg
    combined = r.solve_robust_stopping_ranges(model, box, replace(query, solute_max_kg=.001670))
    agrees(combined, [])
    assert combined.status == 'NO_ROBUST_FEASIBLE_RANGE'
    # Deliberately insufficient comparators, never universal ground truth.
    for values in (model.means, *endpoints):
        nominal = s.solve_stopping_ranges(model.condition(f.EarlyInput('C2', values, 'SYNTHETIC')),
                                         replace(query, solute_max_kg=.001670))
        assert nominal.components


@pytest.mark.parametrize('arm', f.ARMS)
def test_collapsed_boxes_preserve_existing_point_behavior_and_budget(arm):
    model = f.Model.load(MODELS/f'{arm}.json')
    box = box_for(model)
    query = s.StoppingQuery(box.anchor_kg+.001, model.domain_kg,
                            solute_min_kg=.001, suffix_tds_max_percent=8.)
    expected = s.solve_stopping_ranges(model.condition(box.inputs(model.means[2:])), query)
    result = r.solve_robust_stopping_ranges(model, box, query)
    assert result.point_result == expected
    assert result.resources.parent_delivery_evaluations == expected.forward_evaluations
    assert result.resources.envelope_calls == 0
    agrees(result, reference_set(model, box, query, model.means, model.means))
    limited = r.solve_robust_stopping_ranges(model, box, query,
        options=r.RobustStoppingOptions(max_parent_evaluations=2))
    check_partition(limited)
    assert limited.resources.parent_delivery_evaluations == 2
    assert limited.unresolved_regions == (r.MassRegion(query.stop_min_kg, query.stop_max_kg,
        reasons=('GLOBAL_PARENT_EVALUATION_LIMIT',)),)


@pytest.mark.parametrize('arm', ('C1', 'C2'))
def test_constant_profiles_analytical_interval_empty_and_full(arm):
    model = manufactured(arm)
    dimension = len(model.means)-2
    box = box_for(model, [(.4, .6)]*dimension)
    low_c, high_c = expit(-2.-.1*dimension), expit(-2.+.1*dimension)
    query = s.StoppingQuery(.009, .08, solute_min_kg=.002, solute_max_kg=.005)
    result = r.solve_robust_stopping_ranges(model, box, query)
    agrees(result, [(box.anchor_kg+.002/low_c, box.anchor_kg+.005/high_c)])
    for limit, expected in ((100*high_c+1, [(.009, .08)]), (100*low_c-1, [])):
        result = r.solve_robust_stopping_ranges(model, box,
            s.StoppingQuery(.009, .08, suffix_tds_max_percent=limit))
        agrees(result, expected)


def test_genuinely_two_dimensional_box_and_constraint_nesting():
    columns = [(1., 2., .5, 3., 1.), (2., 1., 3., .5, 2.)]
    model = manufactured(columns=columns, intercepts=(-3., -1., -4., -2., -5.))
    assert np.linalg.matrix_rank(np.array(columns)) == 2
    assert all(min(c) > 0 for c in columns)  # Strict assay monotonicity proves extrema.
    box = box_for(model, [(.3, .7), (.2, .6)])
    query = s.StoppingQuery(.009, .08, solute_min_kg=.002, suffix_tds_max_percent=16.)
    expected = reference_set(model, box, query, (*model.means[:2], .3, .2),
                              (*model.means[:2], .7, .6))
    assert expected
    result = r.solve_robust_stopping_ranges(model, box, query)
    agrees(result, expected)
    wide = box_for(model, [(.2, .8), (.1, .7)])
    strict = replace(query, solute_min_kg=.0021, suffix_tds_max_percent=15.5)
    for b, q in ((wide, query), (box, strict)):
        actual = r.solve_robust_stopping_ranges(model, b, q)
        truth = reference_set(model, b, q, (*model.means[:2], *(x for x, _ in b.bounds)),
                               (*model.means[:2], *(y for _, y in b.bounds)))
        agrees(actual, truth)
        assert all(any(x-1e-12 <= lo <= hi <= y+1e-12 for x, y in expected) for lo, hi in truth)
    conflict = r.solve_robust_stopping_ranges(model, box,
        s.StoppingQuery(.009, .08, solute_max_kg=.00001, suffix_tds_min_percent=30.))
    agrees(conflict, [])


def test_nonmonotone_tds_has_disconnected_robust_regions():
    model = manufactured('C1', intercepts=(-5., -1., -4., 0., -5.), columns=[(.2,)*5])
    box = box_for(model, [(.3, .7)])
    query = s.StoppingQuery(.009, .08, suffix_tds_max_percent=12.)
    expected = reference_set(model, box, query, (*model.means[:2], .3), (*model.means[:2], .7))
    assert len(expected) >= 2
    result = r.solve_robust_stopping_ranges(model, box, query)
    agrees(result, expected)
    assert len(result.feasible_regions) == len(expected)


def test_point_mass_budget_is_reserved_before_delegation(monkeypatch):
    model = manufactured('C1', intercepts=(-5., -1., -4., 0., -5.))
    box = box_for(model)
    query = s.StoppingQuery(.009, .08, solute_min_kg=.001,
        suffix_tds_min_percent=12., suffix_tds_max_percent=13.)
    calls = []
    original = s.solve_stopping_ranges
    def audited(*args):
        calls.append(args)
        return original(*args)
    monkeypatch.setattr(s, 'solve_stopping_ranges', audited)
    # Four original pieces, four possible stationary guards for each TDS
    # boundary: (4 + 8 + 8)*128 = 2560, beyond the hard mass budget.
    result = r.solve_robust_stopping_ranges(model, box, query)
    check_partition(result)
    assert not calls and result.resources.parent_delivery_evaluations == 0
    assert result.resources.point_inverse_calls == 0
    assert result.unresolved_regions == (r.MassRegion(.009, .08,
        reasons=('POINT_INVERSE_MASS_BUDGET_RESERVATION_UNAVAILABLE',)),)
    # A single boundary fits. Reject it before delegation if its reservation
    # cannot be made, even though the delivery budget remains ample.
    query = replace(query, suffix_tds_min_percent=None, suffix_tds_max_percent=None)
    denied = r.solve_robust_stopping_ranges(model, box, query,
        options=r.RobustStoppingOptions(max_mass_subdivisions=511))
    assert not calls and denied.status == 'NUMERICALLY_UNRESOLVED'
    accepted = r.solve_robust_stopping_ranges(model, box, query,
        options=r.RobustStoppingOptions(max_mass_subdivisions=512))
    check_partition(accepted)
    assert len(calls) == 1
    assert accepted.resources.point_inverse_mass_refinements_reserved == 512
    assert accepted.point_result == original(model.condition(box.inputs((.5,))), query)


def test_noncollapsed_narrow_component_knot_equality_and_point_queries():
    model = manufactured('C1')
    box = box_for(model, [(.4, .6)])
    c0, c1 = expit(-2.1), expit(-1.9)
    lo, hi = .035, .035003
    query = s.StoppingQuery(.009, .08, solute_min_kg=(lo-box.anchor_kg)*c0,
                            solute_max_kg=(hi-box.anchor_kg)*c1)
    result = r.solve_robust_stopping_ranges(model, box, query)
    agrees(result, [(lo, hi)])
    assert len(result.feasible_regions) == 1 and len(result.unresolved_regions) == 2
    equality = s.StoppingQuery(.009, .08, solute_min_kg=.003, solute_max_kg=.003)
    agrees(r.solve_robust_stopping_ranges(model, box, equality), [])
    knot = s.StoppingQuery(.009, .08, solute_min_kg=(.04-box.anchor_kg)*c0)
    agrees(r.solve_robust_stopping_ranges(model, box, knot), [(.04, .08)])
    for target, expected in ((10., [(.04, .04)]), (20., [])):
        point = s.StoppingQuery(.04, .04, suffix_tds_min_percent=target)
        agrees(r.solve_robust_stopping_ranges(model, box, point), expected)
    nearly_equal = replace(model, theta=tuple((a+k*1e-14, *rest)
        for k, (a, *rest) in enumerate(model.theta)))
    result = r.solve_robust_stopping_ranges(nearly_equal, box, knot)
    agrees(result, reference_set(nearly_equal, box, knot,
        (*model.means[:2], .4), (*model.means[:2], .6)))


def test_late_envelope_failure_preserves_classified_and_all_pending_cells(monkeypatch):
    model = manufactured('C1')
    box = box_for(model, [(.4, .6)])
    query = s.StoppingQuery(.009, .08, solute_min_kg=.002)
    original = e.bound_interval_delivery
    calls = []
    def fail(*args):
        calls.append(args[2])
        if len(calls) == 8:
            raise ValueError('PRIVATE_CANARY')
        return original(*args)
    monkeypatch.setattr(e, 'bound_interval_delivery', fail)
    result = r.solve_robust_stopping_ranges(model, box, query)
    agrees(result, [(box.anchor_kg+.002/expit(-2.1), .08)], qualified=False)
    assert result.feasible_regions and result.excluded_regions and result.unresolved_regions
    assert result.resources.envelope_calls == 8
    assert 'PRIVATE_CANARY' not in result.to_json()


def test_remaining_global_budget_is_passed_to_every_envelope_including_repeats(monkeypatch):
    model = manufactured('C1')
    box = box_for(model, [(.4, .6)])
    query = s.StoppingQuery(.009, .08, solute_min_kg=.002)
    original = e.bound_interval_delivery
    budget, used, tighter = 145, 0, []
    def audited(model, box, q):
        nonlocal used
        assert q.max_point_evaluations == min(16384, budget-used)
        before = model._account.points
        result = original(model, box, q)
        used += model._account.points-before
        if q.absolute_gap_kg == 1e-9:
            tighter.append(q)
        return result
    monkeypatch.setattr(e, 'bound_interval_delivery', audited)
    result = r.solve_robust_stopping_ranges(model, box, query,
        options=r.RobustStoppingOptions(max_parent_evaluations=budget))
    check_partition(result)
    assert tighter and used == result.resources.parent_delivery_evaluations == budget
    assert result.status == 'NUMERICALLY_UNRESOLVED'


def test_anchor_domain_knots_zero_width_equalities_and_flat_prefix():
    model = manufactured('C1', intercepts=(0.,)*5, columns=[(0.,)*5])
    model = replace(model, domain_kg=.125, means=(.00390625, .00390625, .5))
    box = box_for(model)
    for stop in (box.anchor_kg, .03125, .0625, .125):
        target = (stop-box.anchor_kg)/2
        query = s.StoppingQuery(box.anchor_kg, .125, solute_min_kg=target, solute_max_kg=target)
        result = r.solve_robust_stopping_ranges(model, box, query)
        agrees(result, [(stop, stop)])
        assert result.point_result.components[0].isolated
        assert result.feasible_regions == (r.MassRegion(stop, stop,
            reasons=('POINT_INVERSE_QUALIFIED_INTERIOR_OR_EXACT_POINT',)),)
    noncollapsed = box_for(model, [(.4, .6)])
    for constraint in ({'solute_min_kg': 0}, {'solute_max_kg': 0}):
        query = s.StoppingQuery(box.anchor_kg, box.anchor_kg, **constraint)
        result = r.solve_robust_stopping_ranges(model, noncollapsed, query)
        agrees(result, [(box.anchor_kg, box.anchor_kg)])
    half = r.solve_robust_stopping_ranges(model, box,
        s.StoppingQuery(.01, .125, suffix_tds_min_percent=50, suffix_tds_max_percent=50))
    agrees(half, [(.01, .125)])
    prefix = replace(model, theta=((0., 0., 0., 0.),)*3+((-2., 0., 0., 0.),)*2)
    result = r.solve_robust_stopping_ranges(prefix, box,
        s.StoppingQuery(.01, .125, suffix_tds_min_percent=50, suffix_tds_max_percent=50))
    agrees(result, [(.01, .0625)])


def test_tangency_narrow_component_and_unrepresentable_interiors():
    model = manufactured('C1', intercepts=(-5., -1., -4., 0., -5.), columns=[(0.,)*5])
    box = box_for(model)
    def g(x):
        return expit(np.interp(x, np.linspace(0, .08, 5), independent_logits(model, model.means))) * (
            x-box.anchor_kg)-integral(model, model.means, x)[0]
    peak = brentq(g, .06, .08, xtol=1e-15)
    threshold = 100*integral(model, model.means, peak)[0]/(peak-box.anchor_kg)
    tangent = s.StoppingQuery(.055, .08, suffix_tds_min_percent=threshold)
    result = r.solve_robust_stopping_ranges(model, box, tangent)
    check_partition(result)
    assert result.status == 'NUMERICALLY_UNRESOLVED'
    assert any(z.lower_kg <= peak <= z.upper_kg for z in result.unresolved_regions)
    query = replace(tangent, suffix_tds_min_percent=threshold-1e-7)
    result = r.solve_robust_stopping_ranges(model, box, query)
    truth = reference_set(model, box, query, model.means, model.means)
    agrees(result, truth)
    assert len(truth) == 1 and truth[0][1]-truth[0][0] < .0001
    half = manufactured('C0', intercepts=(0.,)*5)
    query = s.StoppingQuery(.02, math.nextafter(.02, math.inf), solute_min_kg=.006, solute_max_kg=.006)
    result = r.solve_robust_stopping_ranges(half, box_for(half), query)
    check_partition(result)
    assert result.status == 'NUMERICALLY_UNRESOLVED'
    assert result.point_result.unresolved_regions


@pytest.mark.parametrize('sign', (-1, 1))
def test_saturation_underflow_and_nearly_flat_residuals(sign):
    model = manufactured()
    model = replace(model, domain_kg=2., theta=((0., sign*20., 0., .1, -.2),)*5)
    box = e.AssayBox('C2', 1., .004, q1=(.4, .6), q2=(.4, .6), input_class='SYNTHETIC')
    query = s.StoppingQuery(1.1, 2., solute_min_kg=1e-100 if sign < 0 else .1)
    result = r.solve_robust_stopping_ranges(model, box, query,
        options=r.RobustStoppingOptions(max_envelope_calls=30))
    check_partition(result)
    if sign < 0:
        assert result.status == 'NUMERICALLY_UNRESOLVED' and not result.feasible_regions
    else:
        agrees(result, [(1.104, 2.)], qualified=False)
    model = manufactured('C1', intercepts=(-2.,)*5, columns=[(0.,)*5])
    query = s.StoppingQuery(.01, .08, suffix_tds_min_percent=100*expit(-2),
                            suffix_tds_max_percent=100*expit(-2))
    result = r.solve_robust_stopping_ranges(model, box_for(model, [(.4, .6)]), query,
        options=r.RobustStoppingOptions(max_envelope_calls=12))
    check_partition(result)
    assert not result.resolution_qualified and not result.feasible_regions


@pytest.mark.parametrize('limits', [
    {'max_mass_subdivisions': 0}, {'max_envelope_calls': 0}, {'max_envelope_calls': 3},
    {'max_parent_evaluations': 0}, {'max_parent_evaluations': 7},
    {'max_parent_evaluations_per_envelope': 2}, {'max_assay_subdivisions_per_call': 0},
])
def test_exhausted_global_and_nested_budgets_retain_every_mass(limits):
    model, box = frozen_case()
    query = s.StoppingQuery(box.anchor_kg, model.domain_kg, solute_min_kg=.001640)
    result = r.solve_robust_stopping_ranges(model, box, query, options=r.RobustStoppingOptions(**limits))
    check_partition(result)
    assert result.status == 'NUMERICALLY_UNRESOLVED' and result.unresolved_regions
    assert all(z.reasons for z in result.unresolved_regions)


@pytest.mark.parametrize('failure', ('exception', 'warning', 'allowance', 'nonfinite', 'envelope', 'quadrature'))
def test_parent_and_envelope_failures_account_actual_calls_and_sanitize(monkeypatch, failure):
    model, box = frozen_case()
    query = s.StoppingQuery(box.anchor_kg, model.domain_kg, solute_min_kg=.001640)
    calls = []
    original = f.predict_intervals
    def observe(state, starts, ends, **kw):
        calls.append(1)
        if len(calls) == 3:
            if failure == 'exception':
                raise ValueError('PRIVATE_CANARY')
            if failure == 'warning':
                warnings.warn('PRIVATE_CANARY', IntegrationWarning)
            if failure in ('allowance', 'nonfinite'):
                p = original(state, starts, ends, **kw)[0]
                return (replace(p, allowance_kg=2e-9 if failure == 'allowance' else math.nan),)
        return original(state, starts, ends, **kw)
    monkeypatch.setattr(f, 'predict_intervals', observe)
    if failure == 'envelope':
        original_envelope = e.bound_interval_delivery
        def broken(*args):
            original_envelope(*args)  # Actual delegated work still counted if return is lost.
            raise RuntimeError('PRIVATE_CANARY')
        monkeypatch.setattr(e, 'bound_interval_delivery', broken)
    if failure == 'quadrature':
        monkeypatch.setattr(e, 'quad', lambda *a, **kw: (math.nan, 0.))
    result = r.solve_robust_stopping_ranges(model, box, query)
    check_partition(result)
    assert result.status == 'NUMERICALLY_UNRESOLVED' and not result.feasible_regions
    assert result.resources.parent_delivery_evaluations == len(calls)
    assert 'PRIVATE_CANARY' not in result.to_json()
    if failure == 'envelope':
        assert not result.resources.nested_accounting_complete
    else:
        assert result.resources.nested_accounting_complete
    assert result.resources.failed_envelope_calls == 1


def test_point_failure_and_global_guard_never_overruns(monkeypatch):
    model = manufactured('C0')
    box = box_for(model)
    query = s.StoppingQuery(.01, .08, solute_min_kg=.001)
    calls = []
    original = f.remaining_solute
    def fail(state, b, **kw):
        calls.append(1)
        if len(calls) == 2:
            raise ValueError('PRIVATE_CANARY')
        return original(state, b, **kw)
    monkeypatch.setattr(f, 'remaining_solute', fail)
    result = r.solve_robust_stopping_ranges(model, box, query,
        options=r.RobustStoppingOptions(max_parent_evaluations=3))
    check_partition(result)
    assert result.resources.parent_delivery_evaluations == len(calls) <= 3
    assert result.resources.failed_parent_evaluations == 1
    assert result.status == 'NUMERICALLY_UNRESOLVED'
    assert 'PRIVATE_CANARY' not in result.to_json()


def test_finite_extreme_mass_arithmetic_failure_still_has_strict_json():
    model = manufactured('C1')
    model = replace(model, means=(1e306, 1e306, .5),
        minima=(1e306, 1e306, 0.), maxima=(1e306, 1e306, 1.), domain_kg=3e306,
        theta=((0., 20., -20., .1),)*5)
    box = box_for(model, [(.4, .6)])
    query = s.StoppingQuery(box.anchor_kg, model.domain_kg, solute_min_kg=.001)
    result = r.solve_robust_stopping_ranges(model, box, query)
    assert result.status == 'NUMERICALLY_UNRESOLVED'
    check_partition(result)
    assert f.strict_json(result.to_json())['unresolved_regions']
    assert result.resources.parent_delivery_evaluations == 0


@pytest.mark.parametrize('changes', [
    {'mass_resolution_kg': 0}, {'mass_resolution_kg': True}, {'mass_resolution_kg': math.nan},
    {'mass_resolution_kg': 10**1000}, {'envelope_absolute_gap_kg': 1e-6},
    {'tighter_envelope_absolute_gap_kg': 1e-6}, {'max_mass_subdivisions': 2049},
    {'max_envelope_calls': 513}, {'max_parent_evaluations': 65537},
    {'max_assay_subdivisions_per_call': 4097}, {'max_parent_evaluations_per_envelope': 16385},
    {'max_mass_subdivisions': False}, {'max_envelope_calls': -1}, {'max_parent_evaluations': 3.5},
])
def test_options_reject_malformed_inputs(changes):
    with pytest.raises(ValueError):
        r.RobustStoppingOptions(**changes)


def test_contracts_serialization_immutability_identity_and_independent_queries(monkeypatch):
    model = manufactured('C1')
    box = box_for(model, [(.4, .6)])
    query = s.StoppingQuery(.01, .08, solute_min_kg=.002)
    result = r.solve_robust_stopping_ranges(model, box, query)
    check_partition(result)
    options = r.RobustStoppingOptions()
    assert options == r.RobustStoppingOptions.from_dict(f.strict_json(f.canonical(options.to_dict())))
    for data in ({}, options.to_dict() | {'future_assay': 1}):
        with pytest.raises(ValueError):
            r.RobustStoppingOptions.from_dict(data)
    for text in ('{"x":NaN}', '{"x":1,"x":1}'):
        with pytest.raises(ValueError):
            f.strict_json(text)
    for obj, key in ((result, 'status'), (result.feasible_regions[0], 'lower_kg'), (options, 'max_envelope_calls')):
        with pytest.raises(FrozenInstanceError):
            setattr(obj, key, 0)
    assert result.model_sha256 == model.sha256 and result.rights == model.rights
    assert result.box_sha256 == f.identity(box.to_dict())
    assert result.query_sha256 == f.identity(query.to_dict())
    assert result.options_sha256 == f.identity(options.to_dict())
    assert result.to_dict()['numerical_settings']['mass_cell_width_target_kg'] == 2.5e-7
    assert set(f.CLAIMS) <= set(result.claims)
    assert result.physical_validation == 'NOT_ESTABLISHED' and not result.production_adoption_authorized
    copied = result.to_dict()
    copied['box']['q1'][0] = 0
    copied['feasible_regions'].clear()
    assert copied != result.to_dict()
    for q in (replace(query, stop_min_kg=.001), replace(query, stop_max_kg=.09),
              s.StoppingQuery(box.anchor_kg, .08, suffix_tds_max_percent=20)):
        with pytest.raises(ValueError):
            r.solve_robust_stopping_ranges(model, box, q)
    with pytest.raises(TypeError):
        r.solve_robust_stopping_ranges(model, box, query.to_dict())
    with pytest.raises(ValueError):
        r.solve_robust_stopping_ranges(f.synthetic_model('C0'), box, query)
    for kwargs in ({'mass_unit': 'g'}, {'concentration_unit': 'percent'}, {'q2': (.1, .2)}):
        with pytest.raises(ValueError):
            e.AssayBox('C1', .004, .004, q1=(.4, .6), **kwargs)
    for kwargs in ({'solute_unit': 'mg'}, {'tds_unit': 'kg/kg'}, {'basis': 'VOLUME'},
                   {'solute_min_kg': math.nan}, {'solute_min_kg': True}, {'stop_max_kg': .001}):
        with pytest.raises(ValueError):
            s.StoppingQuery(**(query.to_dict() | kwargs))
    extrapolated = replace(model, maxima=(.008, .008, .55))
    other = r.solve_robust_stopping_ranges(extrapolated, box, query)
    assert other.feature_extrapolation == ('q1',)
    def forbidden(*args, **kwargs):
        pytest.fail('query accessed files or model fitting')
    monkeypatch.setattr(Path, 'open', forbidden)
    import scipy.optimize
    monkeypatch.setattr(scipy.optimize, 'least_squares', forbidden)
    assert r.solve_robust_stopping_ranges(model, box, query).to_json() == result.to_json()


def test_cli_synthetic_private_exclusive_and_sanitized(tmp_path):
    cmd = [sys.executable, '-m', 'puckworks.analysis.conditional_tail_robust_stopping']
    unknown = subprocess.run([*cmd, '--synthetic', '--PRIVATE_CANARY', 'SECRET_VALUE'],
                             capture_output=True, text=True)
    assert unknown.returncode != 0 and not unknown.stdout
    assert 'PRIVATE_CANARY' not in unknown.stderr and 'SECRET_VALUE' not in unknown.stderr
    demo = subprocess.run([*cmd, '--synthetic'], capture_output=True, text=True)
    assert demo.returncode == 0, demo.stderr
    assert json.loads(demo.stdout)['box']['input_class'] == 'SYNTHETIC'
    model = manufactured('C1')
    box = box_for(model, [(.4, .6)])
    query = s.StoppingQuery(.01, .08, solute_min_kg=.002)
    paths = [tmp_path/f'{name}.json' for name in ('model', 'box', 'query', 'options', 'output')]
    for path, obj in zip(paths, (model, box, query, r.RobustStoppingOptions())):
        path.write_text(f.canonical(obj.to_dict()))
    args = [*cmd, *(v for flag, path in zip(('--model', '--box', '--query', '--options', '--output'), paths)
                   for v in (flag, str(path)))]
    saved = subprocess.run(args, capture_output=True, text=True)
    assert saved.returncode == 0 and not saved.stdout and not saved.stderr
    before = paths[-1].read_bytes()
    assert paths[-1].stat().st_mode & 0o777 == 0o600
    assert subprocess.run(args, capture_output=True).returncode != 0
    assert paths[-1].read_bytes() == before
    paths[1].write_text('{"PRIVATE_CANARY":NaN}')
    invalid = subprocess.run(args, capture_output=True, text=True)
    assert invalid.returncode != 0 and not invalid.stdout
    assert 'PRIVATE_CANARY' not in invalid.stderr and 'Traceback' not in invalid.stderr
    paths[1].unlink()
    paths[1].symlink_to(paths[1])
    invalid = subprocess.run(args, capture_output=True, text=True)
    assert invalid.returncode != 0 and not invalid.stdout and 'Traceback' not in invalid.stderr
    paths[1].unlink()
    paths[1].write_text(f.canonical(box.to_dict()))
    (tmp_path/'.git').mkdir()
    assert subprocess.run(args, capture_output=True).returncode != 0
