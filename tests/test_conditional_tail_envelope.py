"""Manufactured model queries and independent integrals; no empirical outcomes."""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
from itertools import product
import json
import math
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest
from scipy.integrate import IntegrationWarning, quad
from scipy.optimize import brentq
from scipy.special import expit

from puckworks.analysis import conditional_tail_delivery as parent
from puckworks.analysis import conditional_tail_envelope as e

MODELS = Path(__file__).resolve().parents[1] / 'docs/analysis/sci_md_mass_delivery_006/models'


def box_for(model, intervals=None):
    intervals = intervals if intervals is not None else [(q, q) for q in model.means[2:]]
    return e.AssayBox(model.arm, *model.means[:2], input_class='SYNTHETIC',
                      **dict(zip(parent.feature_names(model.arm)[2:], intervals)))


def manufactured(arm='C2', intercepts=(-2.,) * 5, columns=None):
    model = parent.synthetic_model(arm)
    n = len(model.means) - 2
    columns = columns if columns is not None else [(1.,) * 5] * n
    return replace(model, means=(.004, .004, .5, .5)[:n + 2],
                   minima=(.002, .002, 0., 0.)[:n + 2],
                   maxima=(.008, .008, 1., 1.)[:n + 2],
                   theta=tuple((a, 0., 0., *(col[k] * .1 for col in columns))
                               for k, a in enumerate(intercepts)))


def reference(model, values, query, *, derivative=None, refined=False):
    """Direct affine hats, fsum conditioning, adaptive integration, no parent kernel."""
    knots = [model.domain_kg * k / 4 for k in range(5)]
    logits = [math.fsum([row[0], *(t * ((x - mu) / scale) for t, x, mu, scale
                   in zip(row[1:], values, model.means, parent.SCALES))]) for row in model.theta]
    values_out, errors = [], []
    for k, (left, right) in enumerate(zip(knots, knots[1:])):
        a, b = max(left, query.start_kg), min(right, query.end_kg)
        if a >= b:
            continue
        cuts = (a, a + (b - a) / 2, b) if refined else (a, b)
        for lo, hi in zip(cuts, cuts[1:]):
            def integrand(t):
                f = (lo + (hi - lo) * t - left) / (right - left)
                eta = (1 - f) * logits[k] + f * logits[k + 1]
                c = expit(eta)
                if derivative is not None:
                    col = derivative + 3
                    beta = ((1 - f) * model.theta[k][col] + f * model.theta[k + 1][col]) / .1
                    c = c * (1 - c) * beta
                return (hi - lo) * c
            value, err = quad(integrand, 0, 1, epsabs=1e-16, epsrel=3e-14, limit=200)
            values_out.append(value)
            errors.append(err)
    return math.fsum(values_out), math.fsum(errors) + 2e-17


def assert_witnesses(model, box, query, result):
    for extremum in (result.minimum, result.maximum):
        w = extremum.witness
        assert w is not None
        assert w.inputs.values[:2] == (box.m1_kg, box.m2_kg)
        assert all(a <= q <= b for q, (a, b) in zip(w.inputs.values[2:], box.bounds))
        state = model.condition(w.inputs)
        p = state.predict_intervals([query.start_kg], [query.end_kg])[0]
        assert w.prediction == p
        assert w.state_sha256 == parent.identity(state.to_dict())
        direct, error = reference(model, w.inputs.values, query)
        refined, refined_error = reference(model, w.inputs.values, query, refined=True)
        assert abs(direct - refined) <= error + refined_error
        assert abs(refined - p.solute_kg) <= refined_error + p.allowance_kg


def assert_extrema(model, box, query, minimum, maximum):
    result = e.bound_interval_delivery(model, box, query)
    assert result.status == 'ENVELOPE_QUALIFIED', result.termination_reason
    for bound, expected in ((result.minimum, minimum), (result.maximum, maximum)):
        value, error = expected
        assert bound.lower_kg - error <= value <= bound.upper_kg + error
        assert 0 <= bound.gap_kg <= query.absolute_gap_kg
        if query.end_kg > query.start_kg:
            width = Fraction(query.end_kg-query.start_kg)
            assert Fraction(bound.tds_percent_bounds[0]) <= 100*Fraction(bound.lower_kg)/width
            assert Fraction(bound.tds_percent_bounds[1]) >= 100*Fraction(bound.upper_kg)/width
    assert result.delivery_outer_kg == (result.minimum.lower_kg, result.maximum.upper_kg)
    assert result.resources.subdivisions <= query.max_subdivisions
    assert result.resources.parent_point_evaluations <= query.max_point_evaluations
    assert result.resources.failed_parent_evaluations == result.resources.failed_bound_evaluations == 0
    assert_witnesses(model, box, query, result)
    return result


@pytest.mark.parametrize('arm', parent.ARMS)
@pytest.mark.parametrize('window', [(None, .041), (.02, .06), (.06971540000000001,) * 2])
def test_frozen_c0_and_collapsed_boxes_reduce_to_parent(arm, window):
    model = parent.Model.load(MODELS / f'{arm}.json')
    box = box_for(model)
    query = e.EnvelopeQuery(box.anchor_kg if window[0] is None else window[0], window[1])
    state = model.condition(box.inputs(tuple(model.means[2:])))
    p = state.predict_intervals([query.start_kg], [query.end_kg])[0]
    expected = reference(model, state.inputs.values, query)
    r = assert_extrema(model, box, query, expected, expected)
    assert r.resources.parent_point_evaluations == 1 and r.resources.subdivisions == 0
    assert r.minimum.witness.prediction == r.maximum.witness.prediction == p
    assert r.numerical_allowances.maximum_parent_kg == p.allowance_kg
    assert r.numerical_allowances.maximum_envelope_integration_kg == 0
    assert r.delivery_outer_kg[1] - r.delivery_outer_kg[0] <= 2 * p.allowance_kg + 4e-18
    if query.start_kg == query.end_kg:
        assert r.delivery_outer_kg == (0., 0.) and r.tds_outer_percent is None


@pytest.mark.parametrize('arm', ('C1', 'C2'))
@pytest.mark.parametrize('logit', (-20., -2., 0., 20.))
def test_constant_profiles_have_analytical_corner_extrema(arm, logit):
    columns = [(2.,) * 5] if arm == 'C1' else [(2.,) * 5, (-3.,) * 5]
    model = manufactured(arm, (logit,) * 5, columns)
    box = box_for(model, [(.4, .6)] * len(columns))
    q = e.EnvelopeQuery(.008, .08)
    excursion = .1 * sum(abs(c[0]) for c in columns)
    minimum = (.072 * expit(logit - excursion), 2e-17)
    maximum = (.072 * expit(logit + excursion), 2e-17)
    r = assert_extrema(model, box, q, minimum, maximum)
    assert r.resources.subdivisions == 0
    assert r.minimum.witness.inputs.values[2] == .4
    if arm == 'C2':
        assert r.minimum.witness.inputs.values[3] == .6


def test_nonconstant_monotone_assays_and_partial_knot_crossing_queries():
    model = manufactured(columns=[(1., 2., .5, 3., 1.), (-2., -1., -.5, -1., -3.)],
                         intercepts=(-3., -1., -4., -2., -5.))
    box = box_for(model, [(.2, .7), (.1, .6)])
    for start, end in ((.008, .08), (.02, .04), (.017, .063), (.04, .04)):
        q = e.EnvelopeQuery(start, end)
        r = assert_extrema(model, box, q,
            reference(model, (*model.means[:2], .2, .6), q),
            reference(model, (*model.means[:2], .7, .1), q))
        assert r.resources.subdivisions == 0
        if end > start:
            assert r.tds_outer_percent[0] <= 100 * r.minimum.witness.prediction.solute_kg / (end - start)
            assert r.tds_outer_percent[1] >= 100 * r.maximum.witness.prediction.solute_kg / (end - start)


def interior_fixture(dimension=2, sign=-1):
    # On [.02,.06], hat integrals weight columns by (1/2,1,1/2).
    # Both weighted means are zero, and the columns span R^2. At the center
    # eta is constant; gradient = sigmoid'(eta) * integral beta = 0.
    # eta stays negative (positive for sign=+1), proving strict convexity
    # (concavity) and a unique interior minimum (maximum).
    columns = [(0., -1., 1., -1., 0.)]
    if dimension == 2:
        columns.append((0., -1., -1., 3., 0.))
    model = manufactured('C1' if dimension == 1 else 'C2', (sign * 2.,) * 5, columns)
    return model, box_for(model, [(.4, .6)] * dimension), e.EnvelopeQuery(.02, .06)


@pytest.mark.parametrize('dimension,sign', [(1, -1), (2, -1), (2, 1)])
def test_manufactured_interior_extrema_with_convexity_proof(dimension, sign):
    model, box, query = interior_fixture(dimension, sign)
    beta = np.asarray(model.theta)[1:4, 3:] / .1
    assert np.linalg.matrix_rank(beta) == dimension
    assert np.allclose((beta[0] / 2 + beta[1] + beta[2] / 2) * .02, 0., atol=1e-17)
    for values in product(*box.bounds):
        logits = model.condition(box.inputs(values)).logits
        assert all(v * sign > 0 for v in logits)
    for j in range(dimension):
        derivative, error = reference(model, model.means, query, derivative=j, refined=True)
        assert abs(derivative) <= error
    center = (.04 * expit(sign * 2), 2e-17)
    corners = [reference(model, (*model.means[:2], *v), query, refined=True)
               for v in product(*box.bounds)]
    lower, upper = (center, max(corners)) if sign < 0 else (min(corners), center)
    r = assert_extrema(model, box, query, lower, upper)
    w = r.minimum.witness if sign < 0 else r.maximum.witness
    assert w.inputs.values[2:] == (.5,) * dimension
    assert r.resources.subdivisions > 0
    if dimension == 2:
        assert all(a < b for a, b in box.bounds)  # Both coordinates actually vary.


def frozen_counterexample():
    model = parent.Model.load(MODELS / 'C2.json')  # Never transcribe coefficients.
    m1, m2, q1, _ = model.means
    box = e.AssayBox('C2', m1, m2, q1=(q1, q1), q2=(.0931364597, .1830244866),
                      input_class='SYNTHETIC')
    return model, box, e.EnvelopeQuery(box.anchor_kg, .04104270828628944)


def test_mandatory_frozen_c2_interior_minimum_and_endpoint_counterexample():
    model, box, query = frozen_counterexample()
    lo, hi = box.bounds[1]
    def derivative(q2):
        return reference(model, (*model.means[:3], q2), query, derivative=1, refined=True)[0]
    # All knot logits are negative at both q2 endpoints, hence everywhere
    # in the box. S'' = integral beta^2*c*(1-c)*(1-2*c) > 0 since beta != 0.
    for q2 in (lo, hi):
        assert max(model.condition(box.inputs((model.means[2], q2))).logits) < 0
    assert any(row[4] != 0 for row in model.theta)
    assert derivative(lo) < 0 < derivative(hi)
    root = brentq(derivative, lo, hi, xtol=5e-16)
    assert root == pytest.approx(.138198104, abs=1e-9)
    minimum = reference(model, (*model.means[:3], root), query, refined=True)
    ends = [reference(model, (*model.means[:3], q2), query, refined=True) for q2 in (lo, hi)]
    r = assert_extrema(model, box, query, minimum, max(ends))
    assert [v for v, _ in ends] == pytest.approx([.00166547050466296, .00166107295676568], abs=1e-16)
    assert minimum[0] == pytest.approx(.00161806873904614, abs=1e-16)
    assert all(v - err > .001640 for v, err in ends)
    assert r.minimum.witness.prediction.solute_kg + r.minimum.witness.prediction.allowance_kg < .001640
    assert r.minimum.lower_kg < .001640 < r.maximum.upper_kg
    assert e.bound_remaining_solute(model, box, query.end_kg) == r
    tighter = replace(query, absolute_gap_kg=1e-9)
    assert_extrema(model, box, tighter, minimum, max(ends))


def test_sign_crossings_and_rounded_crossing_chords_are_outer():
    model, box, query = interior_fixture()
    # Force crossing inside a segment and away from binary-exact midpoints.
    model = replace(model, theta=tuple((a, b, c, d, f * .7) for a, b, c, d, f in model.theta))
    engine = e._Engine(model, box, query)
    root = engine.node(box.bounds, 0, engine.leaves[0])
    # Independent feasible inputs probe the added envelope integration, without
    # using those probes as an oracle for the global extrema.
    for values in product((.4, .5, .6), repeat=2):
        value, error = reference(model, (*model.means[:2], *values), query, refined=True)
        assert root.lower - error <= value <= root.upper + error
    # A looser chord remains conservative even without any sign-crossing cuts.
    # Concavity/convexity of pointwise min/max proves this; this checks arithmetic.
    a, b = .020000000000000004, .039999999999999994
    beta_a, beta_b = -1., 2.
    for t in (.13, .51, .91):
        beta = (1-t)*beta_a+t*beta_b
        lower_chord = (1-t)*(-abs(beta_a)) + t*(-abs(beta_b))
        upper_chord = -lower_chord
        assert lower_chord <= -abs(beta) <= abs(beta) <= upper_chord
    assert a < b and engine.quads > 0


@pytest.mark.parametrize('sign', (-1, 1))
def test_saturation_underflow_and_near_equal_logits(sign):
    model = manufactured(intercepts=tuple(-2. + k * 1e-14 for k in range(5)))
    box = box_for(model, [(.499999999, .500000001)] * 2)
    q = e.EnvelopeQuery(.019, .077)
    assert_extrema(model, box, q,
        reference(model, (*model.means[:2], .499999999, .499999999), q),
        reference(model, (*model.means[:2], .500000001, .500000001), q))
    # Extreme logits obtained through the unchanged conditioning transform,
    # with legal coefficients (no enlarged coefficient domain).
    model = replace(model, domain_kg=2., theta=((0., sign * 20., 0., .1, -.2),) * 5)
    box = e.AssayBox('C2', 1., .004, q1=(.4, .6), q2=(.4, .6), input_class='SYNTHETIC')
    q = e.EnvelopeQuery(1.1, 2.)
    vals = [reference(model, (1., .004, *v), q) for v in product(*box.bounds)]
    assert_extrema(model, box, q, min(vals), max(vals))


def test_widening_enclosure_relation_and_independent_queries(monkeypatch):
    model, box, query = interior_fixture()
    r = e.bound_interval_delivery(model, box, query)
    wide = e.AssayBox.from_dict(box.to_dict() | {'q1': [.3, .7], 'q2': [.3, .7]})
    larger = e.bound_interval_delivery(model, wide, query)
    assert larger.status == 'ENVELOPE_QUALIFIED'
    # Different finite stopping gaps need not yield nested *reported* outer
    # intervals. Their extremum enclosures must respect true-range inclusion.
    assert larger.minimum.lower_kg <= r.minimum.upper_kg
    assert larger.maximum.upper_kg >= r.maximum.lower_kg
    assert larger.minimum.lower_kg <= r.minimum.lower_kg + r.minimum.gap_kg
    assert larger.maximum.upper_kg >= r.maximum.upper_kg - r.maximum.gap_kg
    partial = replace(query, start_kg=.03, end_kg=.05)
    e.bound_interval_delivery(model, wide, partial)
    def forbidden(*args, **kwargs):
        pytest.fail('query accessed a file or fitted a model')
    monkeypatch.setattr(Path, 'open', forbidden)
    import scipy.optimize
    monkeypatch.setattr(scipy.optimize, 'least_squares', forbidden)
    assert e.bound_interval_delivery(model, box, query).to_json() == r.to_json()


@pytest.mark.parametrize('limits,reason', [
    ({'max_subdivisions': 0}, 'SUBDIVISION_LIMIT'),
    ({'max_point_evaluations': 0}, 'PARENT_POINT_EVALUATION_LIMIT'),
    ({'max_point_evaluations': 4}, 'PARENT_POINT_EVALUATION_LIMIT'),
    ({'max_point_evaluations': 6}, 'PARENT_POINT_EVALUATION_LIMIT'),
    ({'max_subdivisions': 3, 'absolute_gap_kg': 1e-16}, 'SUBDIVISION_LIMIT'),
])
def test_budget_exhaustion_keeps_complete_partition(limits, reason):
    model, box, query = interior_fixture()
    query = replace(query, **limits)
    r = e.bound_interval_delivery(model, box, query)
    assert r.status == 'NUMERICALLY_UNRESOLVED' and r.termination_reason == reason
    assert r.resources.parent_point_evaluations <= query.max_point_evaluations
    assert r.resources.subdivisions <= query.max_subdivisions
    assert r.resources.retained_partition_boxes >= 1
    if query.max_point_evaluations == 6:
        assert r.resources.subdivisions == 1 and r.resources.retained_partition_boxes == 1
    minimum = .04 * expit(-2.)
    assert r.minimum.lower_kg <= minimum <= r.minimum.upper_kg
    for v in product(*box.bounds):
        actual, err = reference(model, (*model.means[:2], *v), query)
        assert r.delivery_outer_kg[0] - err <= actual <= r.delivery_outer_kg[1] + err


@pytest.mark.parametrize('failure', ('exception', 'allowance', 'nonfinite', 'warning'))
def test_injected_parent_failures_remain_unresolved(monkeypatch, failure):
    model, box, query = interior_fixture()
    original = parent.predict_intervals
    calls = []
    def fail(state, starts, ends, **kwargs):
        calls.append(state.inputs.values)
        if len(calls) == 3:
            if failure == 'exception':
                raise ValueError('PRIVATE_CANARY_DO_NOT_EXPORT')
            if failure == 'warning':
                import warnings
                warnings.warn('PRIVATE_CANARY_DO_NOT_EXPORT', IntegrationWarning)
            p = original(state, starts, ends, **kwargs)[0]
            return (replace(p, allowance_kg=2e-9 if failure == 'allowance' else math.nan),)
        return original(state, starts, ends, **kwargs)
    monkeypatch.setattr(parent, 'predict_intervals', fail)
    r = e.bound_interval_delivery(model, box, query)
    assert r.status == 'NUMERICALLY_UNRESOLVED'
    assert r.resources.parent_point_evaluations == 3 and r.resources.failed_parent_evaluations == 1
    assert r.delivery_outer_kg == (0., query.end_kg-query.start_kg)
    assert r.minimum.witness is not None and r.maximum.witness is not None
    assert 'PRIVATE_CANARY' not in r.to_json()


def test_added_integration_failure_and_unrepresentable_split(monkeypatch):
    model, box, query = interior_fixture()
    original = e.quad
    def failed(*args, **kwargs):
        return math.nan, 0.
    monkeypatch.setattr(e, 'quad', failed)
    r = e.bound_interval_delivery(model, box, query)
    assert r.status == 'NUMERICALLY_UNRESOLVED'
    assert r.resources.failed_bound_evaluations == 1 and r.resources.retained_partition_boxes == 1
    monkeypatch.setattr(e, 'quad', original)
    narrow = box_for(model, [(.5, math.nextafter(.5, 1.))] * 2)
    r = e.bound_interval_delivery(model, narrow, replace(query, absolute_gap_kg=1e-25))
    assert r.status == 'NUMERICALLY_UNRESOLVED'
    assert r.termination_reason == 'NO_REPRESENTABLE_OR_INFLUENTIAL_ASSAY_SPLIT'
    collapsed = box_for(model)
    r = e.bound_interval_delivery(model, collapsed, replace(query, absolute_gap_kg=1e-25))
    assert r.termination_reason == 'PARENT_ALLOWANCE_RESOLUTION_LIMIT'
    adjacent = replace(query, end_kg=math.nextafter(query.start_kg, math.inf))
    r = e.bound_interval_delivery(model, box, adjacent)
    assert r.status == 'ENVELOPE_QUALIFIED'
    assert r.maximum.upper_kg <= adjacent.end_kg-adjacent.start_kg


@pytest.mark.parametrize('assay', [(True, .5), (np.bool_(False), .5), ('0.1', .5),
    (math.nan, .5), (0., math.inf), (.6, .4), (-.01, .4), (.2, 1.01), None, (.1,),
    (0., 10**1000)])
def test_invalid_assay_intervals(assay):
    with pytest.raises(ValueError):
        e.AssayBox('C1', .004, .004, q1=assay)


@pytest.mark.parametrize('changes', [
    {'m1_kg': 0}, {'m2_kg': True}, {'m1_kg': '0.004'}, {'m1_kg': math.inf},
    {'mass_unit': 'g'}, {'concentration_unit': 'percent'}, {'basis': 'VOLUME'},
    {'input_class': 'FUTURE_CHEMISTRY'}, {'q2': None}, {'flavor': (0., 1.)},
])
def test_invalid_box_contract(changes):
    with pytest.raises((ValueError, TypeError)):
        e.AssayBox(**(dict(arm='C1', m1_kg=.004, m2_kg=.004, q1=(.1, .2)) | changes))


@pytest.mark.parametrize('changes', [
    {'start_kg': True}, {'end_kg': math.nan}, {'start_kg': -.1}, {'end_kg': .005},
    {'absolute_gap_kg': 0}, {'absolute_gap_kg': 1e-6}, {'absolute_gap_kg': True},
    {'max_subdivisions': 4097}, {'max_point_evaluations': 16385},
    {'max_subdivisions': False}, {'max_point_evaluations': -1},
    {'max_point_evaluations': 3.5}, {'mass_unit': 'g'}, {'basis': 'VOLUME'},
])
def test_invalid_query_contract(changes):
    with pytest.raises(ValueError):
        e.EnvelopeQuery(**(dict(start_kg=.008, end_kg=.08) | changes))


def test_strict_fields_domains_json_immutability_identity_and_rights():
    model, box, query = frozen_counterexample()
    r = e.bound_interval_delivery(model, box, query)
    for bad in ({}, {'q1': (.1, .2)}, {'q1': (.1, .2), 'q2': (.1, .2), 'q3': (.1, .2)}):
        with pytest.raises(ValueError):
            e.AssayBox('C2', .004, .004, **bad)
    with pytest.raises(ValueError):
        e.AssayBox('C0', .004, .004, q1=None)
    for q in (replace(query, start_kg=box.anchor_kg-.0001), replace(query, end_kg=.08)):
        with pytest.raises(ValueError, match='DOMAIN'):
            e.bound_interval_delivery(model, box, q)
    with pytest.raises(ValueError, match='MISMATCH'):
        e.bound_interval_delivery(parent.synthetic_model('C0'), box, query)
    with pytest.raises(TypeError):
        e.bound_interval_delivery(model, box, query.to_dict())
    for obj, loader in ((box, e.AssayBox.from_dict), (query, e.EnvelopeQuery.from_dict)):
        assert loader(parent.strict_json(parent.canonical(obj.to_dict()))) == obj
        with pytest.raises(ValueError):
            loader(obj.to_dict() | {'future_chemistry': .2})
        data = obj.to_dict()
        del data['basis']
        with pytest.raises(ValueError):
            loader(data)
        for text in ('{"basis":"MASS","basis":"MASS"}', '{"x":NaN}'):
            with pytest.raises(ValueError):
                loader(parent.strict_json(text))
    for obj, name in ((box, 'm1_kg'), (query, 'start_kg'), (r.minimum, 'lower_kg')):
        with pytest.raises(FrozenInstanceError):
            setattr(obj, name, 0)
    assert r.model_sha256 == model.sha256 and r.rights == model.rights
    assert 'CC-BY-NC-3.0' in r.rights
    assert set(parent.CLAIMS) <= set(r.claims)
    assert r.box_sha256 == parent.identity(box.to_dict())
    assert r.query_sha256 == parent.identity(query.to_dict())
    copy = r.to_dict()
    copy['box']['q2'][0] = 0
    copy['minimum']['witness']['inputs']['values']['q1'] = 0
    assert copy != r.to_dict()
    outside = e.AssayBox.from_dict(box.to_dict() | {'q1': [0., .5]})
    extra = e.bound_interval_delivery(model, outside, replace(query, max_subdivisions=0))
    assert extra.feature_extrapolation == ('q1',)
    assert r.feature_extrapolation == ()


def test_cli_synthetic_and_quiet_private_exclusive_output(tmp_path):
    cmd = [sys.executable, '-m', 'puckworks.analysis.conditional_tail_envelope']
    demo = subprocess.run([*cmd, '--synthetic'], capture_output=True, text=True)
    assert demo.returncode == 0, demo.stderr
    assert json.loads(demo.stdout)['box']['input_class'] == 'SYNTHETIC'
    model = parent.synthetic_model()
    box = e.AssayBox('C2', .004, .004, q1=(.14, .16), q2=(.09, .11),
                      input_class='SOURCE_EARLY_INPUT')
    query = e.EnvelopeQuery(.008, .04)
    model_file, box_file, query_file, output = [tmp_path / f'{n}.json' for n in ('model', 'box', 'query', 'out')]
    model.save(model_file)
    box_file.write_text(parent.canonical(box.to_dict()))
    query_file.write_text(parent.canonical(query.to_dict()))
    args = [*cmd, '--model', str(model_file), '--box', str(box_file),
            '--query', str(query_file), '--output', str(output)]
    done = subprocess.run(args, capture_output=True, text=True)
    assert done.returncode == 0 and not done.stdout and not done.stderr
    before = output.read_bytes()
    assert json.loads(before)['box']['input_class'] == 'SOURCE_EARLY_INPUT'
    assert output.stat().st_mode & 0o777 == 0o600
    assert subprocess.run(args, capture_output=True).returncode != 0
    assert output.read_bytes() == before
    for invalid in ('{"PRIVATE_CANARY":NaN}', '{"arm":"C2","arm":"C2"}'):
        box_file.write_text(invalid)
        bad = subprocess.run(args, capture_output=True, text=True)
        assert bad.returncode != 0 and not bad.stdout
        assert 'PRIVATE_CANARY' not in bad.stderr
    box_file.write_text(parent.canonical(box.to_dict()))
    loop = tmp_path / 'private-symlink-loop'
    loop.symlink_to(loop)
    bad = subprocess.run([*cmd, '--model', str(model_file), '--box', str(loop),
                          '--query', str(query_file), '--output', str(output)],
                         capture_output=True, text=True)
    assert bad.returncode != 0 and not bad.stdout
    assert 'private-symlink-loop' not in bad.stderr and 'Traceback' not in bad.stderr
    (tmp_path / '.git').mkdir()
    assert subprocess.run(args, capture_output=True).returncode != 0
