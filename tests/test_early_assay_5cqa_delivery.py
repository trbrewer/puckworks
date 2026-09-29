"""Source-free exact arm contracts and independent numerical qualification."""
from dataclasses import FrozenInstanceError, replace
import subprocess
import sys

import numpy as np
import pytest
from scipy.special import logit

from puckworks.analysis import early_assay_5cqa_delivery as m


def synthetic_model(arm='L1M', q=.001):
    n=len(m.feature_names(arm))
    return m.Model(arm, [[float(logit(q))]+[0.]*n]*5,
        (.004,.006,.001,.002)[:n], (.002,.003,0.,0.)[:n], (.009,.01,.005,.005)[:n],
        m.HARD_UPPER_KG,.01,m.canonical({'scope':'SYNTHETIC_NOT_FITTED','species':'5CQA'}),
        'SYNTHETIC_FIRST_PARTY')


def inputs(arm='L1M', m1=.004, m2=.006, q1=.001, q2=.002):
    return {'L1M':lambda:m.L1MInput(m1,m2,q1,input_class='SYNTHETIC'),
            'L2M':lambda:m.L2MInput(m1,m2,q2,input_class='SYNTHETIC'),
            'L12':lambda:m.L12Input(m1,m2,q1,q2,input_class='SYNTHETIC')}[arm]()


@pytest.mark.parametrize('arm',m.ARMS)
def test_exact_species_si_conversions_schemas_and_forbidden_inputs(arm):
    assert m.assay_from_mg_g(2.5)==.0025
    for unit in ('percent','%','mg/L','kg/kg'):
        with pytest.raises(ValueError): m.assay_from_mg_g(2.5,unit=unit)
    for species in ('5-CQA','CQA_sum','CGA','3CQA','caffeine','TDS'):
        with pytest.raises(ValueError): m.assay_from_mg_g(2.5,species=species)
        with pytest.raises(ValueError): replace(inputs(arm),species=species)
    d=inputs(arm).to_dict()
    forbidden=['TDS','recipe','shot','flow','temperature','caffeine','q1','q2']
    forbidden += list(set(m.FEATURES)-set(m.feature_names(arm)))
    for name in forbidden:
        with pytest.raises(ValueError): m.EarlyInput.from_dict(dict(d,**{name:1}))
    with pytest.raises(TypeError): type(inputs(arm))(**dict(d,TDS=.1))
    for key,value in [('mass_unit','g'),('concentration_unit','mg/g'),('basis','VOLUME')]:
        with pytest.raises(ValueError): m.EarlyInput.from_dict(dict(d,**{key:value}))
    model=synthetic_model(arm)
    p=model.condition(inputs(arm)).remaining_5cqa(.06)
    assert p.five_cqa_mg==1e6*p.five_cqa_kg
    assert p.five_cqa_mg_g==1000*p.five_cqa_kg/(p.end_kg-p.start_kg)
    assert p.species=='5CQA' and p.hard_domain_supported
    assert 'ARM_SPECIFIC_EARLY_FIVE_CQA_ASSAY_REQUIRED' in p.claims
    assert m.EarlyInput.from_dict(d)==inputs(arm)
    with pytest.raises(ValueError): m.EarlyInput(.004,.006)
    for other in set(m.ARMS)-{arm}:
        with pytest.raises(ValueError): model.condition(inputs(other))


@pytest.mark.parametrize('q',[None,'',True,-1e-9,1.01,float('nan'),float('inf')])
def test_invalid_spill_is_not_valid_zero(q):
    for schema in (m.L1MInput,m.L2MInput):
        with pytest.raises((ValueError,TypeError)): schema(.004,.006,q)
    for arm in m.ARMS:
        assert synthetic_model(arm).condition(inputs(arm,q1=0.,q2=0.)).remaining_5cqa(.06).numerical_qualified


@pytest.mark.parametrize('arm',m.ARMS)
def test_additivity_zero_width_hard_domain_and_feature_extrapolation(arm):
    s=synthetic_model(arm).condition(inputs(arm))
    whole=s.remaining_5cqa(.06)
    parts=s.predict_intervals([.01,.02,.037],[.02,.037,.06])
    assert abs(sum(p.five_cqa_kg for p in parts)-whole.five_cqa_kg)<=whole.allowance_kg+sum(p.allowance_kg for p in parts)
    assert whole.five_cqa_kg==pytest.approx(.001*.05,abs=1e-18)
    zero=s.predict_intervals([.02],[.02])[0]
    assert zero.five_cqa_kg==0 and zero.five_cqa_mg_g is None
    for starts,ends in [([np.nextafter(.01,0.)],[.02]),([.02],[.01]),([.02],[.07]),
                        ([.02],[]),([float('nan')],[.03]),([.02],[float('inf')])]:
        with pytest.raises(ValueError): s.predict_intervals(starts,ends)
    with pytest.raises(ValueError): s.predict_intervals([.02],[.03],mass_unit='g')
    with pytest.raises(TypeError): s.predict_intervals([.02],[.03],q2=.2)
    with pytest.raises(ValueError): replace(s.model,domain_kg=.07)
    with pytest.raises(ValueError): s.model.condition(inputs(arm,m1=.06,m2=.02))
    p=s.model.condition(inputs(arm,m1=.001,m2=.012,q1=.006,q2=.006)).remaining_5cqa(.06)
    assert p.feature_extrapolation==m.feature_names(arm)
    assert p.support=='FEATURE_EXTRAPOLATION_DIAGNOSTIC' and 0<=p.five_cqa_kg<=.047


@pytest.mark.parametrize('arm',m.ARMS)
def test_knot_splitting_adaptive_comparison_and_extreme_bounds(arm):
    base=synthetic_model(arm);n=1+len(m.feature_names(arm))
    theta=np.zeros((5,n));theta[:,0]=[-4.,-7.,-3.,-9.,-5.]
    s=replace(base,theta=theta).condition(inputs(arm))
    p=s.predict_intervals([.0123],[.066])[0]
    knots=[x for x in np.linspace(0,base.domain_kg,5) if .0123<x<.066]
    edges=[.0123,*knots,.066]
    parts=s.predict_intervals(edges[:-1],edges[1:])
    ref,err=m._reference(s,.0123,.066)
    assert abs(p.five_cqa_kg-ref)+err<=p.allowance_kg
    assert abs(p.five_cqa_kg-sum(q.five_cqa_kg for q in parts))<=p.allowance_kg+sum(q.allowance_kg for q in parts)
    extreme=replace(base,theta=[[20*(-1)**j]*n for j in range(5)])
    p=extreme.condition(inputs(arm,m1=.0001,m2=.0199,q1=.5,q2=.5)).predict_intervals([.0213],[.0651])[0]
    assert 0<=p.five_cqa_kg<=.0438 and p.feature_extrapolation
    assert p.numerical_qualified==(p.allowance_kg<=1e-9)


@pytest.mark.parametrize('arm',m.ARMS)
def test_immutable_strict_serialization_and_deterministic_replay(tmp_path,arm):
    model=synthetic_model(arm);path=tmp_path/(arm+'.json');model.save(path)
    assert m.Model.load(path)==model
    assert sum(len(row) for row in model.theta)==(25 if arm=='L12' else 20)
    with pytest.raises(FileExistsError): model.save(path)
    with pytest.raises(FrozenInstanceError): model.theta=()
    s=model.condition(inputs(arm))
    with pytest.raises(FrozenInstanceError): s.inputs.m1_kg=.2
    with pytest.raises(FrozenInstanceError): s.b_anchor=0
    restored=m.State.from_dict(s.to_dict())
    assert restored==s and restored.remaining_5cqa(.06)==s.remaining_5cqa(.06)
    for key,value in [('species','CQA_sum'),('version','old/1'),('extra',1),
        ('theta',[[0]*3]*5),('units',dict(model.to_dict()['units'],concentration='percent'))]:
        with pytest.raises(ValueError): m.Model.from_dict(dict(model.to_dict(),**{key:value}))
    for key,value in [('b_anchor',.02),('model_sha256','0'*64),('logits',[0]*5)]:
        with pytest.raises(ValueError): m.State.from_dict(dict(s.to_dict(),**{key:value}))
    data=m.strict_json(path.read_text());data['model_sha256']='0'*64;path.write_text(m.canonical(data))
    with pytest.raises(ValueError,match='HASH'): m.Model.load(path)
    with pytest.raises(ValueError,match='DUPLICATE'): m.strict_json('{"x":1,"x":2}')


def test_inference_without_sources_network_training_or_optimizer(tmp_path):
    for arm in m.ARMS: synthetic_model(arm).save(tmp_path/(arm+'.json'))
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
from puckworks.analysis.early_assay_5cqa_delivery import Model, L1MInput, L2MInput, L12Input
for arm, early in [('L1M',L1MInput(.004,.006,.001)),('L2M',L2MInput(.004,.006,.002)),('L12',L12Input(.004,.006,.001,.002))]:
    model=Model.load(Path(sys.argv[1])/(arm+'.json'))
    assert model.condition(early).remaining_5cqa(.06).numerical_qualified
'''
    subprocess.run([sys.executable,'-c',code,str(tmp_path)],check=True)
