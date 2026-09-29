"""Source-free numerical and strict-contract verification, not physical validation."""
from dataclasses import FrozenInstanceError, replace
from decimal import Decimal, localcontext
import subprocess
import sys

import numpy as np
import pytest
from scipy.special import logit

from puckworks.analysis import assay_conditioned_5cqa_delivery as m
from puckworks.analysis import conditional_5cqa_delivery as old


def synthetic_model(arm='L1', q=.001):
    return m.Model(arm, [[float(logit(q)), 0., 0., 0.]]*5 if arm == 'L1' else (),
                   (.004, .006, .001), (.002, .003, 0.), (.009, .01, .005),
                   m.HARD_UPPER_KG, .01 if arm == 'L1' else None,
                   m.canonical({'scope': 'SYNTHETIC_NOT_FITTED', 'species': '5CQA'}),
                   'SYNTHETIC_FIRST_PARTY')


def state(arm='L1', q1=.001):
    return synthetic_model(arm).condition(m.EarlyInput(.004, .006, q1, 'SYNTHETIC'))


def test_strict_species_and_si_conversions():
    assert m.first_assay_from_mg_g(2.5) == .0025
    for unit in ('percent', '%', 'mg/L', 'kg/kg'):
        with pytest.raises(ValueError): m.first_assay_from_mg_g(2.5, unit=unit)
    for species in ('5-CQA', 'CQA_sum', 'CGA', '3CQA', 'caffeine', 'TDS'):
        with pytest.raises(ValueError): m.first_assay_from_mg_g(2.5, species=species)
        with pytest.raises(ValueError): m.EarlyInput(.004, .006, .0025, species=species)
    p = state().remaining_5cqa(.06)
    assert p.five_cqa_mg == 1e6*p.five_cqa_kg
    assert p.five_cqa_mg_g == 1000*p.five_cqa_kg/(p.end_kg-p.start_kg)
    assert p.species == '5CQA' and p.rights == 'SYNTHETIC_FIRST_PARTY'
    assert p.hard_domain_supported and dict(p.units)['concentration_display'] == 'mg/g'
    assert 'FIRST_FRACTION_FIVE_CQA_ASSAY_REQUIRED' in p.claims
    assert 'NO_QUERY_TIME_CHEMICAL_ASSAY' not in p.claims


@pytest.mark.parametrize('q', [None, '', True, -1e-9, 1.01, float('nan'), float('inf')])
def test_invalid_assay_is_not_zero(q):
    with pytest.raises((ValueError, TypeError)): m.EarlyInput(.004, .006, q)


def test_valid_zero_a1_and_unphysical_amplitude_rejection():
    p = state('A1', 0).remaining_5cqa(.06)
    assert p.five_cqa_kg == 0 and p.five_cqa_mg_g == 0 and p.numerical_qualified
    with pytest.raises(ValueError, match='AMPLITUDE'): state('A1', 1.)
    assert state('L1', 0).remaining_5cqa(.06).numerical_qualified


def test_extra_features_and_ambiguous_units_rejected():
    d = m.EarlyInput(.004, .006, .001).to_dict()
    for name in ('q2', 'q2_kg_kg', 'TDS', 'caffeine', 'recipe', 'condition', 'shot', 'temperature', 'flow'):
        with pytest.raises(ValueError): m.EarlyInput.from_dict(dict(d, **{name: 1}))
    for key, value in [('mass_unit', 'g'), ('concentration_unit', 'mg/g'), ('basis', 'VOLUME')]:
        with pytest.raises(ValueError): m.EarlyInput.from_dict(dict(d, **{key: value}))
    with pytest.raises(TypeError): state().predict_intervals([.02], [.03], q2=.1)
    with pytest.raises(TypeError): m.EarlyInput(.004, .006, .001, TDS=.1)


def test_a1_unique_interval_average_normalization():
    early = m.EarlyInput(.007, .003, .003)
    s = synthetic_model('A1').condition(early)
    tau = 0.02319173692244203
    expected = early.q1_kg_kg*early.m1_kg/(tau*(-np.expm1(-early.m1_kg/tau)))
    assert s.amplitude == pytest.approx(expected, rel=3e-16)
    prefix = old.exponential_integrals([0.], [early.m1_kg], s.amplitude, tau)[0]
    assert prefix == pytest.approx(early.q1_kg_kg*early.m1_kg, rel=3e-16)
    point_amplitude = early.q1_kg_kg*np.exp(early.m1_kg/2/tau)
    assert abs(s.amplitude-point_amplitude) > 1e-6
    p = s.predict_intervals([.02], [.05])[0]
    exact = early.q1_kg_kg*early.m1_kg*np.exp(-.02/tau)*(-np.expm1(-.03/tau))/(-np.expm1(-early.m1_kg/tau))
    assert abs(p.five_cqa_kg-exact) <= p.allowance_kg
    saved = s.model.to_dict()
    for key, value in [('fixed_decay_kg', .024), ('E0_semantic_sha256', '0'*64), ('regularization', .01)]:
        with pytest.raises(ValueError): m.Model.from_dict(dict(saved, **{key: value}))
    assert saved['theta'] == [] and m.TAU_KG == tau


@pytest.mark.parametrize('a,b', [(.025, np.nextafter(.025, 1.)), (.01, .06), (.02, .02)])
def test_a1_expm1_against_independent_decimal(a,b):
    s = state('A1', .003)
    p = s.predict_intervals([a], [b])[0]
    with localcontext() as ctx:
        ctx.prec = 90
        q, mass, tau, lo, hi = map(Decimal.from_float, (.003, .004, m.TAU_KG, a, b))
        ref = float(q*mass*((-lo/tau).exp()-(-hi/tau).exp())/(1-(-mass/tau).exp()))
    assert abs(p.five_cqa_kg-ref) <= p.allowance_kg
    assert p.five_cqa_kg == pytest.approx(ref, rel=3e-14, abs=1e-35)
    assert p.numerical_qualified


@pytest.mark.parametrize('arm',m.ARMS)
def test_additivity_zero_width_hard_domains_and_extrapolation(arm):
    s = state(arm)
    whole = s.remaining_5cqa(.06)
    parts = s.predict_intervals([.01,.02,.037], [.02,.037,.06])
    assert abs(sum(p.five_cqa_kg for p in parts)-whole.five_cqa_kg) <= whole.allowance_kg+sum(p.allowance_kg for p in parts)
    zero = s.predict_intervals([.02],[.02])[0]
    assert zero.five_cqa_kg == 0 and zero.five_cqa_mg_g is None
    for starts,ends in [([np.nextafter(.01,0.)],[.02]),([.02],[.01]),([.02],[.07]),
                        ([.02],[]),([float('nan')],[.03]),([.02],[float('inf')])]:
        with pytest.raises(ValueError): s.predict_intervals(starts,ends)
    with pytest.raises(ValueError): s.predict_intervals([.02],[.03],mass_unit='g')
    with pytest.raises(ValueError): replace(s.model,domain_kg=.07)
    with pytest.raises(ValueError): s.model.condition(m.EarlyInput(.06,.02,.001))
    ex = s.model.condition(m.EarlyInput(.001,.012,.006))
    p = ex.remaining_5cqa(.06)
    assert p.feature_extrapolation == m.FEATURES and p.hard_domain_supported
    assert p.support == 'FEATURE_EXTRAPOLATION_DIAGNOSTIC'
    assert p.numerical_qualified and 0 <= p.five_cqa_kg <= .047


def test_constant_curve_and_d0_reduction():
    s = state()
    p = s.remaining_5cqa(.06)
    assert p.five_cqa_kg == pytest.approx(.001*.05, abs=1e-18)
    theta = np.array([[-5.-j*.4, .1*j, -.1*j] for j in range(5)])
    d0 = old.Model('D0',theta,s.model.means[:2],s.model.minima[:2],s.model.maxima[:2],
                   s.model.domain_kg,.01,None,None,old.canonical({'scope':'SYNTHETIC'}),'SYNTHETIC')
    l1 = replace(s.model,theta=np.c_[theta,np.zeros(5)])
    for q1 in (0.,.002,1.):
        a = l1.condition(m.EarlyInput(.004,.006,q1)).remaining_5cqa(.06)
        b = d0.condition(old.EarlyInput('D0',(.004,.006))).remaining_5cqa(.06)
        assert abs(a.five_cqa_kg-b.five_cqa_kg) <= a.allowance_kg+b.allowance_kg


@pytest.mark.parametrize('arm',m.ARMS)
def test_immutable_strict_roundtrip_and_tampering(tmp_path,arm):
    model=synthetic_model(arm);path=tmp_path/(arm+'.json');model.save(path)
    assert m.Model.load(path)==model
    with pytest.raises(FileExistsError): model.save(path)
    with pytest.raises(FrozenInstanceError): model.theta=()
    s=state(arm)
    with pytest.raises(FrozenInstanceError): s.inputs.q1_kg_kg=.2
    with pytest.raises(FrozenInstanceError): s.b_anchor=0
    assert m.State.from_dict(s.to_dict())==s
    for key,value in [('species','CQA_sum'),('version','old/1'),('extra',1),
                      ('units',dict(model.to_dict()['units'],concentration='percent'))]:
        with pytest.raises(ValueError): m.Model.from_dict(dict(model.to_dict(),**{key:value}))
    for key,value in [('b_anchor',.02),('model_sha256','0'*64),('amplitude',.5)]:
        with pytest.raises(ValueError): m.State.from_dict(dict(s.to_dict(),**{key:value}))
    data=m.strict_json(path.read_text());data['model_sha256']='0'*64
    path.write_text(m.canonical(data))
    with pytest.raises(ValueError,match='HASH'): m.Model.load(path)
    with pytest.raises(ValueError,match='DUPLICATE'): m.strict_json('{"x":1,"x":2}')
    with pytest.raises(ValueError): m.strict_json('{"x":NaN}')


def test_runtime_requires_no_training_source_or_optimizer(tmp_path):
    path=tmp_path/'model.json';synthetic_model().save(path)
    code='''
import importlib.abc, sys, socket, scipy.optimize
from pathlib import Path
def forbidden(*args, **kwargs): raise RuntimeError('forbidden runtime effect')
scipy.optimize.least_squares=forbidden
scipy.optimize.minimize=forbidden
socket.create_connection=forbidden
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, *args):
        if 'training' in fullname or 'pannusch_' in fullname or fullname.startswith('openpyxl'):
            raise RuntimeError('forbidden inference dependency: '+fullname)
sys.meta_path.insert(0,Block())
from puckworks.analysis.assay_conditioned_5cqa_delivery import Model, EarlyInput
model=Model.load(sys.argv[1])
assert model.condition(EarlyInput(.004,.006,.001)).remaining_5cqa(.06).numerical_qualified
'''
    subprocess.run([sys.executable,'-c',code,str(path)],check=True)


def test_extreme_l1_coefficients_retain_numerical_failure():
    model=replace(synthetic_model(),theta=[[20*(-1)**j,-20*(-1)**j,20*(-1)**j,20*(-1)**j] for j in range(5)])
    s=model.condition(m.EarlyInput(.0001,.0199,.5))
    p=s.predict_intervals([.0213],[.0651])[0]
    assert p.feature_extrapolation and 0<=p.five_cqa_kg<=.0438
    assert p.numerical_qualified == (p.allowance_kg<=1e-9)
    assert p.difference_adaptive_kg<=p.allowance_kg
