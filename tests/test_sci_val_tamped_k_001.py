"""Synthetic qualification only; real target residuals are not a development oracle."""
from dataclasses import replace
import inspect
import json
import math

import pytest

from puckworks.analysis import sci_val_tamped_k_001 as m
from puckworks.models.wadsworth2026.permeability import k_percolation


@pytest.fixture
def inputs():
    return [m.CaseInput(g, rho, (49e-6, 50e-6, 51e-6), (.24, .25, .26),
                        (.34, .35, .36)) for g, rho in m.KEYS]


def synthetic_targets(bundle):
    return [dict(grind=r['grind'], bulk_density_kgm3=r['bulk_density_kgm3'],
                 low=r['consolidated']['central'], mean=r['consolidated']['central'],
                 high=r['consolidated']['central'], sd=1e-16) for r in bundle['cases']]


def synthetic_source():
    return dict(schema_version=1, original_denominator=12, scope='DECLARED_ADAPTER_COMPARISON',
                units=dict(d32_um='um', bulk_density_kgm3='kg/m3', epsilon_ss='1'),
                initial_packing=dict(solid_density_kgm3=1300,
                                    solid_density_rounding_half_kgm3=.5,
                                    particle_porosity=.5, particle_porosity_rounding_half=.005),
                cases=[dict(grind=g, bulk_density_kgm3=rho, d32_um=100,
                            d32_rounding_half_um=.005, epsilon_ss=.25,
                            epsilon_ss_low=.24, epsilon_ss_high=.26,
                            qualification=m.QUALIFIED) for g, rho in m.KEYS])


def test_published_units_and_initial_density(tmp_path):
    p=tmp_path/'inputs.json';p.write_bytes(m.canonical_bytes(synthetic_source()))
    rows=m.load_inputs(p)
    assert m.radius_from_um(100)==pytest.approx(50e-6, rel=1e-14)
    assert rows[0].radius_m==pytest.approx((49.9975e-6,50e-6,50.0025e-6), rel=1e-12)
    assert rows[0].initial_porosity[1]==pytest.approx(1-360/650)
    assert rows[0].initial_porosity[0] < rows[0].initial_porosity[1] < rows[0].initial_porosity[2]


@pytest.mark.parametrize('change', ['missing','duplicate','units','unsupported','target','missing_value'])
def test_loader_rejects_bad_contract(tmp_path, change):
    d=synthetic_source()
    if change=='missing':d['cases'].pop()
    if change=='duplicate':d['cases'][-1]=d['cases'][0]
    if change=='units':d['units']['d32_um']='m'
    if change=='unsupported':d['cases'][0]['qualification']='MISSING'
    if change=='target':d['cases'][0]['permeability_m2']=1e-13
    if change=='missing_value':del d['cases'][0]['epsilon_ss']
    p=tmp_path/'bad.json';p.write_bytes(m.canonical_bytes(d))
    with pytest.raises((ValueError,KeyError)):
        m.load_inputs(p)


@pytest.mark.parametrize('r,phi', [(0,.25),(-1,.25),(math.inf,.25),(math.nan,.25),
                                   (50e-6,0),(50e-6,1),(50e-6,-.1),(50e-6,math.nan)])
def test_invalid_domain_rejected(r,phi):
    with pytest.raises(ValueError):m.bounded_prediction((r,r,r),(phi,phi,phi))


def test_unordered_and_underflow_rejected():
    with pytest.raises(ValueError):m.bounded_prediction((2e-5,1e-5,3e-5),(.2,.3,.4))
    with pytest.raises(ValueError):m.bounded_prediction((1,1,1),(.2,.3,.4))


def test_imported_model_and_independent_decimal_reference():
    # Independently calculated with 70-digit Decimal exp/log arithmetic.
    reference=1.027527568416800023735770833274815428679347931609207004166699730047369e-12
    result=m.bounded_prediction((50e-6,50e-6,50e-6),(.25,.25,.25))
    assert result['central']==pytest.approx(k_percolation(50e-6,.25), rel=1e-14)
    assert result['central']==pytest.approx(reference, rel=1e-12, abs=0)


def test_porosity_monotonicity():
    for r in (1e-5,1/m.ALPHA,4e-4):
        values=[m.bounded_prediction((r,r,r),(p,p,p))['central'] for p in (.01,.1,.25,.5,.9)]
        assert all(a<b for a,b in zip(values,values[1:]))


@pytest.mark.parametrize('low,high,maximum',[(.2,.8,'right'),(1.2,2.,'left'),(.5,2.,'stationary')])
def test_radius_extrema_across_stationary_point(low,high,maximum):
    stationary=1/m.ALPHA
    rlo,rhi=low*stationary,high*stationary
    bounds=m.bounded_prediction((rlo,(rlo+rhi)/2,rhi),(.2,.25,.3))
    rmax={'right':rhi,'left':rlo,'stationary':stationary}[maximum]
    assert bounds['high']==pytest.approx(float(k_percolation(rmax,.3)),rel=1e-12,abs=0)
    assert bounds['low']==pytest.approx(min(float(k_percolation(r,.2)) for r in (rlo,rhi)),rel=1e-12,abs=0)
    for i in range(101):
        for p in (.2,.25,.3):
            value=float(k_percolation(rlo+(rhi-rlo)*i/100,p))
            assert bounds['low']*(1-1e-14)<=value<=bounds['high']*(1+1e-14)


@pytest.mark.parametrize('lo,hi,want',[(.5,2,'PASS'),(.8,1.2,'PASS'),(.1,.49,'FAIL'),
                                      (2.01,3,'FAIL'),(.49,.5,'UNRESOLVED_AT_DECLARED_INPUT_PRECISION'),
                                      (2,2.1,'UNRESOLVED_AT_DECLARED_INPUT_PRECISION'),
                                      (.4,2.1,'UNRESOLVED_AT_DECLARED_INPUT_PRECISION')])
def test_classification_boundaries(lo,hi,want):
    assert m.classify(lo,hi)==want


def test_complete_keys_deterministic_order_and_no_target_api(inputs,monkeypatch):
    assert list(inspect.signature(m.predict).parameters)==['cases']
    assert list(inspect.signature(m.bounded_prediction).parameters)==['radius_m','phi']
    monkeypatch.setattr(m,'load_targets',lambda: pytest.fail('prediction accessed targets'))
    assert m.canonical_bytes(m.predict(inputs))==m.canonical_bytes(m.predict(list(reversed(inputs))))
    with pytest.raises(ValueError):m.predict(inputs[:-1])
    with pytest.raises(ValueError):m.predict(inputs[:-1]+[inputs[0]])
    with pytest.raises(ValueError):m.predict([replace(inputs[0],grind='Z')]+inputs[1:])
    with pytest.raises(TypeError):m.predict(inputs,observed=[1]*12)


def test_score_denominator_target_bounds_and_negative_verdict(inputs):
    bundle=m.predict(inputs);targets=synthetic_targets(bundle)
    result=m.score(bundle,targets)
    assert result['counts']['PASS']==12
    assert result['coverage']==dict(intended=12,qualified=12,scored=12)
    for key in ['geometric_mean_ratio','geometric_rms_error_factor','maximum_multiplicative_error']:
        assert result['summary']['consolidated'][key]==pytest.approx(1)
    targets[0]['low']=targets[0]['mean']/10
    targets[0]['high']=targets[0]['mean']/10
    targets[0]['mean']/=10
    result=m.score(bundle,targets)
    assert result['scientific_adequacy']=='CONSOLIDATED_INPUT_PRIOR_FAILS_DECLARED_SCREEN'
    assert result['counts']['FAIL']==1
    assert result['coverage']['scored']==12
    assert result['summary']['consolidated']['geometric_mean_ratio']==pytest.approx(10**(1/12))
    assert result['summary']['consolidated']['geometric_rms_error_factor']==pytest.approx(math.exp(math.log(10)/math.sqrt(12)))
    with pytest.raises(ValueError):m.score(bundle,targets[:-1])
    targets[0]['mean']=0
    with pytest.raises(ValueError):m.score(bundle,targets)


def test_target_rounding_direction(inputs):
    bundle=m.predict(inputs);targets=synthetic_targets(bundle)
    targets[0]['low']*=.9;targets[0]['high']*=1.1
    result=m.score(bundle,targets)['cases'][0]['consolidated']
    assert result['q_low']==bundle['cases'][0]['consolidated']['low']/targets[0]['high']
    assert result['q_high']==bundle['cases'][0]['consolidated']['high']/targets[0]['low']


def test_serialization_and_result_only_regeneration(inputs,tmp_path,monkeypatch):
    bundle=m.predict(inputs);result=m.score(bundle,synthetic_targets(bundle))
    p=tmp_path/'retained.json';p.write_bytes(m.canonical_bytes(result))
    def forbidden(*args,**kwargs):pytest.fail('report recomputed science')
    for name in ['predict','score','load_inputs','load_targets','bounded_prediction']:
        monkeypatch.setattr(m,name,forbidden)
    first=m.render_report(json.loads(p.read_text()))
    assert first==m.render_report(json.loads(p.read_text()))
    assert len([line for line in first.splitlines() if line.startswith('| A-')])==3
    assert p.read_bytes()==m.canonical_bytes(result)
    with pytest.raises(ValueError):m.canonical_bytes({'invalid':math.nan})
    with pytest.raises(ValueError):m.canonical_bytes({'invalid':math.inf})
