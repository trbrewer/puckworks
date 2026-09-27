"""Synthetic mathematical and serialization qualification for task 008."""
from dataclasses import FrozenInstanceError, asdict, replace
import json
import math

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.special import expit

from puckworks.analysis import conditional_tail_delivery as md
from puckworks.analysis import source_calibrated_tail_delivery as s


def record(arm='C2', shot=1, delta=-.7):
    model = md.synthetic_model(arm)
    early = md.EarlyInput(arm, model.means, 'SYNTHETIC')
    parent = model.condition(early)
    starts, ends = [.008, .02, .04], [.02, .04, .06]
    values = s.shifted_integrals(parent, delta, starts, ends)
    obs = tuple(s.Observation(shot, k+1, b-a, a, b, float(v/(b-a))) for k, (a, b, v) in enumerate(zip(starts, ends, values)))
    return model, s.CalibrationRecord('a'*64, shot, early, obs)


@pytest.mark.parametrize('arm', ['C0', 'C2'])
def test_one_scalar_recovers_aggregate_and_parent_bytes(arm):
    model, rec = record(arm); before = md.canonical(model.to_dict())
    artifact = s.calibrate_source(model, rec)
    assert artifact.status == 'QUALIFIED'
    assert abs(artifact.delta+.7) < 2e-12
    assert artifact.enclosure[0] < -.7 < artifact.enclosure[1]
    assert md.canonical(model.to_dict()) == before
    cert = json.loads(artifact.certificate_json)
    assert cert['left_mass_bounds_kg'][1] < cert['observed_mass_bounds_kg'][0]
    assert cert['right_mass_bounds_kg'][0] > cert['observed_mass_bounds_kg'][1]
    assert cert['radius'] in s.RADII


def test_serialization_immutability_identities_and_fields(tmp_path):
    model, rec = record(); artifact = s.calibrate_source(model, rec)
    state = artifact.condition(rec.early); path = tmp_path/'cal.json'; artifact.save(path)
    assert s.OffsetCalibration.load(path, parent_sha256=model.sha256, calibrator=1, source_sha256='a'*64) == artifact
    assert s.OffsetState.from_dict(state.to_dict()) == state
    assert s.CalibrationRecord.from_dict(rec.to_dict()) == rec
    with pytest.raises(FrozenInstanceError):
        artifact.delta = 1
    with pytest.raises(FileExistsError):
        artifact.save(path)
    for expected in ({'parent_sha256': 'b'*64}, {'calibrator': 2}, {'source_sha256': 'b'*64}):
        with pytest.raises(ValueError, match='WRONG_PARENT'):
            s.OffsetCalibration.load(path, **expected)
    data = artifact.to_dict(); data['unexpected'] = 1
    with pytest.raises(ValueError, match='STRICT_FIELDS'):
        s.OffsetCalibration.from_dict(data)
    data = state.to_dict(); data['parent_state']['logits'][0] += .1
    with pytest.raises(ValueError, match='DERIVED'):
        s.OffsetState.from_dict(data)
    data = rec.to_dict(); data['units']['beverage'] = 'g'
    with pytest.raises(ValueError, match='UNITS'):
        s.CalibrationRecord.from_dict(data)
    path.write_text('{"version":1,"version":2}')
    with pytest.raises(ValueError, match='DUPLICATE'):
        s.OffsetCalibration.load(path)


def test_range_and_enclosure_failures_are_artifacts(monkeypatch):
    model, rec = record()
    zero = replace(rec, windows=tuple(replace(w, q=0.) for w in rec.windows))
    bad = s.calibrate_source(model, zero)
    assert bad.status == 'CALIBRATION_RANGE_FAILURE' and bad.delta is None
    with pytest.raises(ValueError, match='CALIBRATION_RANGE_FAILURE'):
        bad.condition(rec.early)
    monkeypatch.setattr(s, 'mass_bounds', lambda *args: (-1., 1.))
    unresolved = s.calibrate_source(model, rec)
    assert unresolved.status == 'NUMERICAL_ENCLOSURE_UNRESOLVED'


def test_no_missing_chemistry_or_extra_shot_silently_trains():
    model, rec = record()
    bad = replace(rec, windows=(replace(rec.windows[0], q=None), *rec.windows[1:]))
    assert s.calibrate_source(model, bad).status == 'CALIBRATION_SUPPORT_FAILURE'
    with pytest.raises(ValueError, match='ONE_SHOT'):
        replace(rec, windows=(*rec.windows, replace(rec.windows[0], shot=2)))


@pytest.mark.parametrize('logit,offset', [(-20., -20.), (20., 20.), (0., 0.), (-20., 20.), (20., -20.)])
def test_equal_extreme_logits_zero_delegation_and_mass_bounds(logit, offset):
    model, rec = record()
    model = replace(model, theta=tuple((logit, 0., 0., 0., 0.) for _ in range(5)))
    artifact = s.OffsetCalibration(model, 'a'*64, 1, rec.sha256, offset, (offset, offset), 'QUALIFIED', '{}')
    state = artifact.condition(rec.early)
    p = state.predict_intervals([.008], [.079])[0]
    assert abs(p.solute_kg-(.079-.008)*expit(logit+offset)) <= p.allowance_kg
    assert p.numerical_qualified and 0 <= p.solute_kg <= .071+p.allowance_kg
    if offset == 0:
        assert p == state.parent_state.predict_intervals([.008], [.079])[0]


def test_knots_additivity_order_and_independent_quadrature():
    model, rec = record(); artifact = s.calibrate_source(model, rec); state = artifact.condition(rec.early)
    a, mid, b = .009, .032, .078
    ps = state.predict_intervals([a, mid, a, mid], [mid, b, b, mid])
    assert abs(ps[0].solute_kg+ps[1].solute_kg-ps[2].solute_kg) <= sum(p.allowance_kg for p in ps)
    assert ps[3].solute_kg == 0 and ps[3].tds_percent is None and ps[3].allowance_kg == 0
    logits = np.array(state.parent_state.logits)+artifact.delta
    reference = quad(lambda x: expit(np.interp(x, np.linspace(0, model.domain_kg, 5), logits)),
                     a, b, points=[.02, .04, .06], epsabs=1e-14)[0]
    assert abs(reference-ps[2].solute_kg) <= ps[2].allowance_kg
    assert state.predict_intervals([mid, a], [b, mid]) == (ps[1], ps[0])
    assert state.predict_intervals([a], [b])[0] == ps[2]
    assert state.remaining_solute(.06) == state.predict_intervals([state.b_anchor], [.06])[0]


def test_query_and_information_rejections():
    model, rec = record('C0'); state = s.calibrate_source(model, rec).condition(rec.early)
    for a, b in [(.007, .02), (.02, .081), (.03, .02), (.02, math.inf), (math.nan, .04)]:
        with pytest.raises(ValueError):
            state.predict_intervals([a], [b])
    with pytest.raises(ValueError, match='KG'):
        state.predict_intervals([.01], [.02], mass_unit='g')
    with pytest.raises(ValueError):
        state.calibration.condition(md.EarlyInput('C2', (.004, .004, .2, .1)))
    with pytest.raises(ValueError):
        md.early_input('C0', m1_kg=.004, m2_kg=.004, q1=.1)
    with pytest.raises(ValueError, match='ANCHOR'):
        state.calibration.condition(md.EarlyInput('C0', (.1, .1)))
    with pytest.raises(ValueError, match='TYPED'):
        state.calibration.condition(asdict(rec.windows[0]))


def test_mass_si_time_invariance_bounds_and_serialization():
    cal = s.MassCalibration('a'*64, 1, 'b'*64, (.2, 0., .04, .7), .08, (.01, .05), 'QUALIFIED')
    state = cal.condition(md.EarlyInput('C0', (.004, .004), 'SYNTHETIC'))
    ps = state.predict_intervals([.008, .025, .008, .01], [.025, .065, .065, .01])
    assert abs(ps[0].solute_kg+ps[1].solute_kg-ps[2].solute_kg) <= sum(p.allowance_kg for p in ps)
    ref = quad(lambda b: .2*math.exp(-(.04*1000*b)**.7), .008, .065, epsabs=1e-14)[0]
    assert abs(ps[2].solute_kg-ref) < ps[2].allowance_kg <= 1e-9
    assert ps[3].solute_kg == 0 and ps[3].tds_percent is None
    rows = s.gram_rows([.008], [.065]); expected = s.gc.deliver(rows, cal.theta)
    rows[0].update(t_start_s=1000., t_end_s=2000.)
    assert np.array_equal(s.gc.deliver(rows, cal.theta), expected)
    assert s.MassState.from_dict(state.to_dict()) == state
    assert s.MassCalibration.from_dict(cal.to_dict()) == cal
    with pytest.raises(ValueError, match='ABSENT_TIME'):
        replace(cal, theta=(.2, 1e-16, .04, .7))
    with pytest.raises(ValueError, match='MASS_ONLY'):
        cal.condition(md.EarlyInput('C2', (.004, .004, .1, .1)))
    with pytest.raises(ValueError):
        state.predict_intervals([.007], [.02])
    with pytest.raises(ValueError):
        state.predict_intervals([.01], [.081])


def test_numerical_allowance_enclosure_derivative_bound():
    model, rec = record(); art = s.calibrate_source(model, rec)
    a, b = .009, .079; state = art.condition(rec.early); p = state.predict_intervals([a], [b])[0]
    for delta in art.enclosure:
        edge = s.shifted_integrals(state.parent_state, delta, [a], [b])[0]
        assert abs(edge-p.solute_kg) <= p.allowance_kg
