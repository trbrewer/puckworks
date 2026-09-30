"""Synthetic numerical verification only; no experimental records or fitting."""
from dataclasses import FrozenInstanceError, replace
from itertools import product
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import expit

from puckworks.analysis import conditional_tail_delivery as parent
from puckworks.analysis.conditional_tail_stopping import (
    MASS_RESOLUTION_KG, StoppingQuery, solve_stopping_ranges,
)

MODELS = Path(__file__).resolve().parents[1] / 'docs/analysis/sci_md_mass_delivery_006/models'


def state(logits=(-2.,) * 5, arm='C2'):
    model = parent.synthetic_model(arm)
    model = replace(model, theta=tuple((v,) + (0.,) * len(model.means) for v in logits))
    return model.condition(parent.EarlyInput(arm, model.means, 'SYNTHETIC'))


def reference(s, b, refined=False):
    """Independent adaptive quadrature of affine eta, never the forward kernel."""
    knots = np.linspace(0, s.model.domain_kg, 5)
    values, errors = [], []
    for l, r, u, v in zip(knots, knots[1:], s.logits, s.logits[1:]):
        start, end = max(l, s.b_anchor), min(r, b)
        if start >= end:
            continue
        points = (start, (start + end) / 2, end) if refined else (start, end)
        for a, c in zip(points, points[1:]):
            def integrand(x):
                mass = a + (c - a) * x
                f = (mass - l) / (r - l)
                return (c - a) * expit((1 - f) * u + f * v)
            value, error = quad(integrand, 0., 1., epsabs=1e-16, epsrel=3e-14, limit=200)
            values.append(value)
            errors.append(error)
    return sum(values), sum(errors)


def reference_components(s, q):
    """Root topology from derivative bracketing + quadrature, not a dense grid.

    Manufactured tests below also supply known topology analytically. This
    reference uses numerical derivative roots, independently of analytic logit cuts.
    """
    a, b = q.stop_min_kg, q.stop_max_kg
    knots = np.linspace(0., s.model.domain_kg, 5)
    roots = []
    bounds = [(False, q.solute_min_kg), (False, q.solute_max_kg),
              (True, q.suffix_tds_min_percent), (True, q.suffix_tds_max_percent)]
    for tds, value in bounds:
        if value is None:
            continue
        def residual(x):
            f = reference(s, x, True)[0]
            return f - (value / 100 * (x - s.b_anchor) if tds else value)
        cuts = [a, b, *(float(k) for k in knots if a < k < b)]
        if tds:
            def derivative(x):
                return expit(np.interp(x, knots, s.logits)) - value / 100
            for left, right in zip(sorted(cuts), sorted(cuts)[1:]):
                if derivative(left) * derivative(right) < 0:
                    cuts.append(brentq(derivative, left, right, xtol=1e-15))
        cuts = sorted(set(cuts))
        roots.extend(x for x in cuts if residual(x) == 0.)
        for left, right in zip(cuts, cuts[1:]):
            if residual(left) * residual(right) < 0:
                roots.append(brentq(residual, left, right, xtol=1e-15))
    cuts = sorted(set([a, b, *roots]))
    out = []
    for left, right in zip(cuts, cuts[1:]):
        mass = (left + right) / 2
        f = reference(s, mass, True)[0]
        t = 100 * f / (mass - s.b_anchor)
        yes = all(limit is None or (actual >= limit if lower else actual <= limit)
                  for actual, limit, lower in ((f, q.solute_min_kg, True),
                  (f, q.solute_max_kg, False), (t, q.suffix_tds_min_percent, True),
                  (t, q.suffix_tds_max_percent, False)))
        if yes:
            if out and out[-1][1] == left:
                out[-1] = (out[-1][0], right)
            else:
                out.append((left, right))
    return out


def assert_encloses(endpoint, expected):
    assert endpoint.lower_kg - 3e-15 <= expected <= endpoint.upper_kg + 3e-15
    assert endpoint.upper_kg - endpoint.lower_kg <= MASS_RESOLUTION_KG


def assert_reference(s, q):
    expected = reference_components(s, q)
    result = solve_stopping_ranges(s, q)
    assert result.status == ('FEASIBLE_RANGES' if expected else 'NO_FEASIBLE_RANGE')
    assert not result.unresolved_regions
    assert len(result.components) == len(expected)
    assert result.maximum_forward_allowance_kg <= 1e-9
    assert result.maximum_refinement_iterations <= 128
    for c, (lo, hi) in zip(result.components, expected):
        assert_encloses(c.lower, lo)
        assert_encloses(c.upper, hi)
        x = (c.interior_min_kg + c.interior_max_kg) / 2
        # Independent adaptive refinement AND unchanged-parent round trip.
        first, e1 = reference(s, x)
        second, e2 = reference(s, x, True)
        p = s.remaining_solute(x)
        assert abs(first - second) <= e1 + e2 + 1e-17
        assert abs(second - p.solute_kg) <= e2 + p.allowance_kg
        assert q.solute_min_kg is None or p.solute_kg >= q.solute_min_kg
        assert q.solute_max_kg is None or p.solute_kg <= q.solute_max_kg
        assert q.suffix_tds_min_percent is None or p.tds_percent >= q.suffix_tds_min_percent
        assert q.suffix_tds_max_percent is None or p.tds_percent <= q.suffix_tds_max_percent
        for endpoint in (c.lower, c.upper):
            if endpoint.qualification not in ('QUALIFIED_CROSSING_BRACKET', 'EXACT_STRUCTURAL_ROOT'):
                continue
            mass = (endpoint.lower_kg + endpoint.upper_kg) / 2
            predicted = s.remaining_solute(mass)
            for name in endpoint.constraints:
                limit = getattr(q, name)
                target = limit if name.startswith('solute') else limit / 100 * (mass - s.b_anchor)
                assert abs(predicted.solute_kg - target) <= (
                    endpoint.residual_allowance_kg + endpoint.bracket_effect_kg)
                if name.startswith('suffix_tds'):
                    assert abs(predicted.tds_percent - limit) <= (
                        endpoint.tds_residual_allowance_percent + endpoint.tds_bracket_effect_percent)
    return result


@pytest.mark.parametrize('logit', [-4., -2., 0., 2., 8.])
def test_analytical_constant_solute_and_tds(logit):
    s = state((logit,) * 5)
    q = expit(logit)
    query = StoppingQuery(.009, .079, solute_min_kg=q * .012, solute_max_kg=q * .043)
    result = assert_reference(s, query)
    assert len(result.components) == 1
    assert_encloses(result.components[0].lower, s.b_anchor + .012)
    assert_encloses(result.components[0].upper, s.b_anchor + .043)
    assert_reference(s, StoppingQuery(.009, .079, suffix_tds_max_percent=min(100, 100 * q + 1)))
    assert_reference(s, StoppingQuery(.009, .079, suffix_tds_min_percent=100 * q + .01))


@pytest.mark.parametrize('logits', [(-5., -4., -3., -2., -1.), (-1., -2., -3., -4., -5.),
                                  (-5., -1., -4., 0., -5.), (-2., -2.+1e-14, -2., -2., -2.)])
def test_rising_falling_and_multiple_knot_profiles(logits):
    s = state(logits)
    for q in (StoppingQuery(.009, .08, suffix_tds_max_percent=12),
              StoppingQuery(.009, .08, solute_min_kg=.002, suffix_tds_max_percent=15),
              StoppingQuery(.009, .08, solute_max_kg=.00001, suffix_tds_min_percent=30)):
        assert_reference(s, q)


def frozen_c2():
    model = parent.Model.load(MODELS / 'C2.json')
    return model.condition(parent.EarlyInput('C2', (
        .0030670000000000003, .0032029999999999997, .2974564005, .0931364597), 'SYNTHETIC'))


def test_mandatory_frozen_c2_two_components():
    s = frozen_c2()
    assert not s.feature_extrapolation  # marginal bounds, NOT joint experimental support
    q = StoppingQuery(.007, .06971540000000001, suffix_tds_max_percent=4.9)
    r = assert_reference(s, q)
    assert len(r.components) == 2
    independently_computed = reference_components(s, q)
    assert independently_computed[0][1] == pytest.approx(.04618171404338526, abs=2e-14)
    assert independently_computed[1][0] == pytest.approx(.06408384803290236, abs=2e-14)
    tighter = replace(q, solute_min_kg=.0015, solute_max_kg=.0032,
                      suffix_tds_min_percent=4.5)
    narrow = assert_reference(s, tighter)
    for c in narrow.components:
        assert any(p.lower.lower_kg <= c.interior_min_kg <= c.interior_max_kg <= p.upper.upper_kg
                   for p in r.components)
    points = solve_stopping_ranges(s, replace(q, suffix_tds_min_percent=4.9))
    assert points.status == 'FEASIBLE_RANGES' and len(points.components) == 2
    assert all(c.isolated for c in points.components)
    for c, x in zip(points.components, (independently_computed[0][1], independently_computed[1][0])):
        assert_encloses(c.lower, x)
    too_narrow = solve_stopping_ranges(s, replace(q, suffix_tds_min_percent=4.9 - 1e-12))
    assert too_narrow.status == 'NUMERICALLY_UNRESOLVED'
    assert too_narrow.unresolved_regions


FROZEN_INPUTS = [(arm, values) for arm in parent.ARMS for model in [parent.Model.load(MODELS / f'{arm}.json')]
                 for values in [model.means, *product(*zip(model.minima, model.maxima))]]


@pytest.mark.parametrize('arm,values', FROZEN_INPUTS)
def test_all_frozen_arms_synthetic_means_and_marginal_corners(arm, values):
    model = parent.Model.load(MODELS / f'{arm}.json')
    s = model.condition(parent.EarlyInput(arm, values, 'SYNTHETIC'))
    lo, hi = s.b_anchor + .001, model.domain_kg
    for q in (StoppingQuery(lo, hi, suffix_tds_max_percent=5),
              StoppingQuery(lo, hi, solute_min_kg=.001, solute_max_kg=.003),
              StoppingQuery(lo, hi, solute_min_kg=.001, suffix_tds_max_percent=8)):
        r = assert_reference(s, q)
        assert r.model_sha256 == model.sha256 and r.arm == arm
        assert r.input_class == 'SYNTHETIC' and r.rights == model.rights
        assert r.feature_extrapolation == s.feature_extrapolation


def test_anchor_zero_full_empty_points_and_exact_flat_threshold():
    s = state((0.,) * 5)
    a = s.b_anchor
    r = solve_stopping_ranges(s, StoppingQuery(a, .08, solute_max_kg=0))
    assert r.status == 'FEASIBLE_RANGES' and len(r.components) == 1
    assert r.components[0].isolated and r.components[0].lower.lower_kg == a
    r = solve_stopping_ranges(s, StoppingQuery(a, .08, solute_min_kg=0))
    assert len(r.components) == 1 and r.components[0].upper.upper_kg == .08
    assert solve_stopping_ranges(s, StoppingQuery(a, .08, solute_min_kg=.1)).status == 'NO_FEASIBLE_RANGE'
    for b in (a, .02):
        r = solve_stopping_ranges(s, StoppingQuery(b, b, solute_min_kg=0))
        assert r.status == 'FEASIBLE_RANGES' and r.components[0].isolated
    r = solve_stopping_ranges(s, StoppingQuery(.01, .08, suffix_tds_min_percent=50,
                                              suffix_tds_max_percent=50))
    assert r.status == 'FEASIBLE_RANGES' and len(r.components) == 1
    assert r.components[0].lower.lower_kg == .01 and r.components[0].upper.upper_kg == .08
    assert solve_stopping_ranges(s, StoppingQuery(.02, .02, suffix_tds_max_percent=50)).status == 'FEASIBLE_RANGES'
    for constraint in ({'suffix_tds_max_percent': 0}, {'suffix_tds_min_percent': 100}):
        assert solve_stopping_ranges(s, StoppingQuery(.01, .08, **constraint)).status == 'NO_FEASIBLE_RANGE'


def test_structural_roots_at_endpoints_and_knots():
    # Binary-exact anchor/targets permit exact singleton and clipped endpoint assertions.
    model = replace(parent.synthetic_model(), domain_kg=.125,
                    theta=((0.,) * 5,) * 5)
    s = model.condition(parent.EarlyInput('C2', (.00390625, .00390625, .15, .1), 'SYNTHETIC'))
    for stop in (s.b_anchor, .03125, .0625, .125):
        target = (stop - s.b_anchor) / 2
        q = StoppingQuery(s.b_anchor, .125, solute_min_kg=target, solute_max_kg=target)
        r = solve_stopping_ranges(s, q)
        assert r.status == 'FEASIBLE_RANGES' and len(r.components) == 1
        assert r.components[0].isolated
        assert_encloses(r.components[0].lower, stop)


def test_nonconstant_knot_roots_equality_and_ambiguous_query_endpoints():
    s = state((-3., -1., -4., 0., -5.))
    target = reference(s, .04, True)[0]
    for q in (StoppingQuery(.01, .08, solute_min_kg=target),
              StoppingQuery(.01, .08, suffix_tds_max_percent=100 * target / (.04 - s.b_anchor))):
        r = assert_reference(s, q)
        assert any(e.lower_kg <= .04 <= e.upper_kg for c in r.components for e in (c.lower, c.upper))
    r = solve_stopping_ranges(s, StoppingQuery(.01, .08, solute_min_kg=target, solute_max_kg=target))
    assert r.status == 'FEASIBLE_RANGES' and len(r.components) == 1
    assert r.components[0].isolated
    assert_encloses(r.components[0].lower, .04)
    # Rounded nonstructural equality at a clipped query endpoint may be on either side.
    r = solve_stopping_ranges(s, StoppingQuery(.04, .08, solute_min_kg=target))
    assert r.status == 'NUMERICALLY_UNRESOLVED' and r.components
    assert r.unresolved_regions[0].lower_kg == .04
    q = StoppingQuery(.01, .08, solute_min_kg=target,
                      suffix_tds_max_percent=100 * target / (.04 - s.b_anchor))
    r = solve_stopping_ranges(s, q)
    assert r.status == 'NUMERICALLY_UNRESOLVED'
    assert any(u.reason == 'OVERLAPPING_CONSTRAINT_BOUNDARIES' for u in r.unresolved_regions)


def peak(s):
    knots = np.linspace(0, s.model.domain_kg, 5)
    def derivative_numerator(b):
        return expit(np.interp(b, knots, s.logits)) * (b - s.b_anchor) - reference(s, b, True)[0]
    return brentq(derivative_numerator, .045, .065, xtol=1e-15)


def test_tangency_narrow_components_and_partial_unresolved():
    s = frozen_c2()
    x = peak(s)
    threshold = 100 * reference(s, x, True)[0] / (x - s.b_anchor)
    tangent = StoppingQuery(.04, .069, suffix_tds_min_percent=threshold)
    r = solve_stopping_ranges(s, tangent)
    assert r.status == 'NUMERICALLY_UNRESOLVED' and r.unresolved_regions
    assert any(z.lower_kg <= x <= z.upper_kg for z in r.unresolved_regions)
    # A small but numerically distinguishable island near the maximum.
    island = replace(tangent, suffix_tds_min_percent=threshold - 1e-7)
    r = assert_reference(s, island)
    assert len(r.components) == 1
    assert r.components[0].upper.upper_kg - r.components[0].lower.lower_kg < .0001
    partial = solve_stopping_ranges(s, StoppingQuery(.007, .069, suffix_tds_max_percent=threshold))
    assert partial.status == 'NUMERICALLY_UNRESOLVED'
    assert partial.components and all(c.partial for c in partial.components)


def test_nonstructural_flat_and_ill_conditioned_cases_are_unresolved():
    s = state()
    r = solve_stopping_ranges(s, StoppingQuery(.01, .08, suffix_tds_min_percent=100 * expit(-2),
                                              suffix_tds_max_percent=100 * expit(-2)))
    assert r.status == 'NUMERICALLY_UNRESOLVED' and not r.components
    s = state((-20.,) * 5)
    r = solve_stopping_ranges(s, StoppingQuery(.01, .08, solute_min_kg=.03 * expit(-20)))
    assert r.status == 'NUMERICALLY_UNRESOLVED'
    assert r.components and r.components[0].partial
    for sign in (-1, 1):
        model = replace(parent.synthetic_model('C0'), domain_kg=2.,
                        theta=((0., sign * 20., 0.),) * 5)
        s = model.condition(parent.EarlyInput('C0', (1., .004), 'SYNTHETIC'))
        q = StoppingQuery(1.1, 2., solute_min_kg=1e-100 if sign < 0 else .1)
        r = solve_stopping_ranges(s, q)
        if sign < 0:
            assert r.status == 'NUMERICALLY_UNRESOLVED'
        assert r.feature_extrapolation == s.feature_extrapolation
        assert r.maximum_forward_allowance_kg <= 1e-9


def test_exact_flat_prefix_is_a_component_of_a_nonconstant_profile():
    s = state((0., 0., 0., -2., -3.))
    r = solve_stopping_ranges(s, StoppingQuery(.009, .08, suffix_tds_min_percent=50,
                                              suffix_tds_max_percent=50))
    assert r.status == 'FEASIBLE_RANGES' and len(r.components) == 1
    assert r.components[0].lower.lower_kg == .009
    assert r.components[0].upper.upper_kg == .04


def test_unrepresentable_interior_cannot_turn_a_point_into_a_feasible_interval():
    s = state((0.,) * 5)
    q = StoppingQuery(.02, float(np.nextafter(.02, np.inf)),
                      solute_min_kg=.006, solute_max_kg=.006)
    r = solve_stopping_ranges(s, q)
    assert r.status == 'NUMERICALLY_UNRESOLVED'
    assert any(u.reason == 'NO_REPRESENTABLE_INTERIOR_MASS' for u in r.unresolved_regions)
    assert len(r.components) == 1 and r.components[0].lower.lower_kg == .02
    assert all(c.interior_min_kg is None and c.interior_max_kg is None for c in r.components)
    assert all(c.partial and not c.isolated for c in r.components)


@pytest.mark.parametrize('changes', [
    {'stop_min_kg': True}, {'solute_min_kg': False}, {'stop_min_kg': '0.01'},
    {'stop_min_kg': None}, {'stop_max_kg': np.inf}, {'solute_min_kg': np.nan},
    {'stop_max_kg': 10**1000}, {'solute_min_kg': np.bool_(True)},
    {'suffix_tds_min_percent': -1}, {'suffix_tds_max_percent': 101}, {'solute_max_kg': -1},
    {'stop_min_kg': .1}, {'solute_min_kg': .002, 'solute_max_kg': .001},
    {'suffix_tds_min_percent': 6, 'suffix_tds_max_percent': 5},
    {'mass_unit': 'g'}, {'solute_unit': 'mg'}, {'tds_unit': 'kg/kg'}, {'basis': 'VOLUME'},
])
def test_invalid_numbers_units_and_order(changes):
    with pytest.raises(ValueError):
        StoppingQuery(**(dict(stop_min_kg=.01, stop_max_kg=.08, solute_min_kg=0) | changes))


def test_invalid_domain_fields_and_zero_suffix_tds():
    s = state()
    for lo, hi in ((.007, .08), (.01, .081)):
        with pytest.raises(ValueError, match='DOMAIN'):
            solve_stopping_ranges(s, StoppingQuery(lo, hi, solute_min_kg=0))
    with pytest.raises(ValueError, match='CONSTRAINT'):
        StoppingQuery(.01, .08)
    for hi in (s.b_anchor, .08):
        with pytest.raises(ValueError, match='POSITIVE_SUFFIX'):
            solve_stopping_ranges(s, StoppingQuery(s.b_anchor, hi, suffix_tds_max_percent=10))
    q = StoppingQuery(.01, .08, solute_min_kg=0)
    with pytest.raises(TypeError):
        StoppingQuery(.01, .08, flavor=1)
    with pytest.raises(ValueError):
        StoppingQuery.from_dict(q.to_dict() | {'extra': 1})
    d = q.to_dict()
    del d['basis']
    with pytest.raises(ValueError):
        StoppingQuery.from_dict(d)
    with pytest.raises(TypeError):
        solve_stopping_ranges(s, q.to_dict())


def test_immutable_serialization_order_and_independent_queries(monkeypatch):
    s = frozen_c2()
    q = StoppingQuery(.007, s.model.domain_kg, suffix_tds_max_percent=4.9)
    r = solve_stopping_ranges(s, q)
    saved = parent.canonical(r.to_dict())
    with pytest.raises(FrozenInstanceError):
        q.stop_min_kg = .02
    with pytest.raises(FrozenInstanceError):
        r.components[0].upper.lower_kg = .03
    assert StoppingQuery.from_dict(json.loads(parent.canonical(q.to_dict()))) == q
    loaded = parent.State.from_dict(json.loads(parent.canonical(s.to_dict())))
    assert loaded == s
    assert r.claims == parent.CLAIMS and r.state_sha256 == parent.identity(s.to_dict())
    result_copy = r.to_dict()
    result_copy['components'].clear()
    result_copy['query']['stop_min_kg'] = .04
    assert parent.canonical(r.to_dict()) == saved
    solve_stopping_ranges(s, StoppingQuery(.02, .03, solute_min_kg=.01))
    def forbidden(*args, **kwargs):
        pytest.fail('inverse accessed a file or fitting routine')
    monkeypatch.setattr(Path, 'open', forbidden)
    import scipy.optimize
    monkeypatch.setattr(scipy.optimize, 'least_squares', forbidden)
    assert parent.canonical(solve_stopping_ranges(loaded, q).to_dict()) == saved
    assert r.components[0].upper.upper_kg < r.components[1].lower.lower_kg


def test_forward_failure_is_unresolved_not_infeasible(monkeypatch):
    s = state()
    original = parent.remaining_solute
    def failed(state, stop):
        return replace(original(state, stop), allowance_kg=2e-9, numerical_qualified=False)
    monkeypatch.setattr(parent, 'remaining_solute', failed)
    r = solve_stopping_ranges(s, StoppingQuery(.01, .08, solute_min_kg=.001))
    assert r.status == 'NUMERICALLY_UNRESOLVED' and not r.components
    assert 'PARENT_FORWARD_ALLOWANCE_NOT_QUALIFIED' in r.reasons
    assert r.maximum_forward_allowance_kg == 2e-9


def test_zero_logit_endpoint_failure_and_runtime_exception_remain_unresolved(monkeypatch):
    s = state((0.,) * 5)
    original = parent.remaining_solute
    def failed(state, stop):
        if stop == .08:
            raise ValueError('LOGIT_RANGE_OVERFLOW')
        return original(state, stop)
    monkeypatch.setattr(parent, 'remaining_solute', failed)
    r = solve_stopping_ranges(s, StoppingQuery(.01, .08, suffix_tds_max_percent=50))
    assert r.status == 'NUMERICALLY_UNRESOLVED' and not r.components
    assert 'PARENT_FORWARD_NUMERICAL_FAILURE' in r.reasons


def test_cli_source_free_strict_private_files_and_exclusive_output(tmp_path):
    cmd = [sys.executable, '-m', 'puckworks.analysis.conditional_tail_stopping']
    demo = subprocess.run([*cmd, '--synthetic'], capture_output=True, text=True)
    assert demo.returncode == 0, demo.stderr
    assert json.loads(demo.stdout)['input_class'] == 'SYNTHETIC'
    s = state()
    # Saved mode remains quiet even when a state is explicitly source-labelled.
    s = s.model.condition(replace(s.inputs, input_class='SOURCE_EARLY_INPUT'))
    state_file, query_file, output = [tmp_path / name for name in ('state.json', 'query.json', 'out.json')]
    state_file.write_text(parent.canonical(s.to_dict()))
    q = StoppingQuery(.01, .08, solute_min_kg=.001)
    query_file.write_text(parent.canonical(q.to_dict()))
    args = [*cmd, '--state', str(state_file), '--query', str(query_file), '--output', str(output)]
    done = subprocess.run(args, capture_output=True, text=True)
    assert done.returncode == 0 and not done.stdout and not done.stderr
    before = output.read_bytes()
    assert json.loads(before)['input_class'] == 'SOURCE_EARLY_INPUT'
    assert subprocess.run(args, capture_output=True).returncode != 0
    assert output.read_bytes() == before
    query_file.write_text('{"private-canary": NaN}')
    bad = subprocess.run(args, capture_output=True, text=True)
    assert bad.returncode != 0 and 'private-canary' not in bad.stdout + bad.stderr
    assert not bad.stdout
    query_file.write_text(parent.canonical(q.to_dict()).replace('"basis":"MASS"', '"basis":"MASS","basis":"MASS"'))
    assert subprocess.run(args, capture_output=True).returncode != 0
    query_file.write_text(parent.canonical(q.to_dict()))
    (tmp_path / '.git').mkdir()
    assert subprocess.run(args, capture_output=True).returncode != 0
