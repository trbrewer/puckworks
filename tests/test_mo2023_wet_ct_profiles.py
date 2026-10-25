"""Scientific risks in the bounded Mo graphical analysis, with synthetic oracles."""
from fractions import Fraction
import json
import os
import subprocess
import sys

import numpy as np
import pytest

from puckworks.analysis import mo2023_wet_ct_profiles as m


@pytest.fixture(scope='module')
def calculated():
    return m.analyze()


def cal():
    return dict(x12=12.,x22=22.,z0=0.,z04=.4,alpha=1.,beta=0.,gamma=1.,delta=0.,anchor_allowance_pt=.01)


def simple(x=(10.,23.), z=(.1,.1)):
    return m.Curve(x,z)


def test_counts_identity_and_support(calculated):
    meta,rows,curves=m.load()
    req,means,summary=calculated
    assert len(meta['panels'])==4 and len(curves)==24 and len(req)==48
    assert len({r['request_id'] for r in req})==48
    assert len({v['history'] for v in meta['profiles'].values()})==2
    for panel in meta['panels']:
        assert sorted(v['radius_mm'] for v in meta['profiles'].values() if v['panel']==panel)==list(m.RADII)
    assert sum(len(r) for r in rows.values())==12494
    assert len(means)==60
    missing=[r for r in req if r['sign']=='UNSUPPORTED']
    assert len(missing)==1 and missing[0]['request_id']=='post_late_14b_r0.92'
    assert missing[0]['nominal_estimate'] is None and missing[0]['qualified_lower'] is None
    assert 'LEGEND_OCCLUDED' in missing[0]['support_reason']
    assert 'AXIS_CLIPPED' in missing[0]['support_reason']
    assert len(curves['14b_r0.92'])==4  # gaps retained, never sorted into one curve
    assert all(r['qualified_lower'] <= r['nominal_estimate'] <= r['qualified_upper']
               for r in req if r['support_status']=='COMPLETE')


@pytest.mark.parametrize('slope',[-.3,0.,.2])
def test_constant_and_linear_contrasts(slope):
    c=simple(z=(slope*10+5,slope*23+5))
    assert m.nominal_contrast(c,cal(),[(1,m.LOWER),(-1,m.UPPER)])==pytest.approx(-5*slope,abs=1e-13)
    assert m.nominal_contrast(c,cal(),[(1,m.LOWER),(-1,m.LATE)])==pytest.approx(-7*slope,abs=1e-13)


def test_partial_segment_integration():
    # Integral of x on [.3,1.7] = 1.4, straddling a non-boundary vertex.
    x=np.array([0.,1.,2.]);w=m.integral_weights(x,.3,1.7)
    assert w.sum()==pytest.approx(1.4)
    assert w@x==pytest.approx(1.4)
    # Kink independent antiderivative: [0.5,1] ascending, [1,1.5] descending.
    assert w.shape==x.shape
    assert m.integral_weights(x,.5,1.5)@np.array([0.,2.,0.])==pytest.approx(1.5)
    with pytest.raises(ValueError):m.integral_weights(x,-.1,1.)


def test_affine_reparameterization_with_jacobian():
    c=m.Curve([10,12.3,13.6,17.4,19.2,23],[.2,.3,.1,.04,.2,.1])
    ca=cal();terms=[(1,m.LOWER),(-1,m.UPPER)]
    v=m.nominal_contrast(c,ca,terms)
    # Native x'=7x+350, z'=3z-25; same physical curve/calibration.
    changed=m.Curve(7*c.x+350,3*c.z-25)
    cb={**ca,'x12':7*12+350,'x22':7*22+350,'gamma':1/3,'delta':25/3}
    assert m.nominal_contrast(changed,cb,terms)==pytest.approx(v,abs=1e-12)


def test_offset_and_reused_coefficients_cancel():
    c=simple(z=(2.,7.));terms=[(1,m.LOWER),(-1,m.UPPER)]
    weights=m.source_coefficients(c,cal(),terms)
    assert abs(weights.sum())<1e-14
    assert m.nominal_contrast(m.Curve(c.x,c.z+300),cal(),terms)==pytest.approx(m.nominal_contrast(c,cal(),terms),abs=1e-12)
    repeated=[(1,m.LOWER),(-1,m.LOWER)]
    assert m.band_terms(repeated)==[]
    assert m.local_box_radius(m.source_coefficients(c,cal(),repeated),.8)==0
    assert m.certified_contrast(c,cal(),repeated,.01)==(0.,0.)
    assert m.local_box_radius(np.array([2.,-3.,0.]),np.array([.1,.2,999.]))==pytest.approx(.8)


def test_kink_responds_to_horizontal_calibration_and_enclosed():
    c=m.Curve([10,13,14,18,19,23],[0,0,1,0,0,0]);ca=cal()
    terms=[(1,m.LOWER),(-1,m.UPPER)]
    values=[]
    for a in np.linspace(11.99,12.01,5):
        for b in np.linspace(21.99,22.01,5):
            values.append(m.nominal_contrast(c,{**ca,'x12':a,'x22':b},terms))
    assert max(values)-min(values)>1e-3
    lo,hi=m.certified_contrast(c,ca,terms,.001,integration_cells=64)
    assert lo<min(values)<max(values)<hi


def mask_fixture():
    c=simple(x=(10,23),z=(0,0))
    info={'local_allowance_pt':.001,'effective_clip_pdf_pt':[0,-10,30,10]}
    panel={'calibration':cal(),'opaque_mask_pdf_pt':[14.005,-1,15,1]}
    return c,info,panel


def test_calibration_shift_into_mask_prevents_qualified_support():
    c,info,panel=mask_fixture()
    assert m.support([c],info,panel,[m.LOWER],False)[0]
    ok,reason,_=m.support([c],info,panel,[m.LOWER],True)
    assert not ok and 'LEGEND_OCCLUDED' in reason


def test_finite_alternatives_require_every_complete_member():
    c,info,panel=mask_fixture()
    good_panel={**panel,'opaque_mask_pdf_pt':[25,-1,26,1]}
    check=lambda alt:m.support([alt],info,good_panel,[m.LOWER],True)[0]
    assert m.membership_support([c,simple(z=(.1,.1))],check)==(True,'FINITE_ALTERNATIVES_ENCLOSED')
    assert not m.membership_support([c,simple(x=(13,23))],check)[0]
    assert m.membership_support([],check)==(False,'UNAUTHENTICATED')


def test_zero_touch_and_delta_interpretation():
    assert m.classify(0.,.1,'post_primary')[0]=='SIGN_UNRESOLVED'
    assert m.classify(-.1,0.,'post_late')[0]=='SIGN_UNRESOLVED'
    assert m.classify(.1,.2,'delta')==('POSITIVE','CONTRAST_INCREASED')
    assert m.classify(-.2,-.1,'delta')==('NEGATIVE','CONTRAST_DECREASED')
    assert m.classify(.1,.2,'post_primary')[1]=='LOWER_INTERIOR_HIGHER'
    assert m.classify(None,None,'delta')[0]=='UNSUPPORTED'
    assert m.classify(.1,.2,'delta',qualified=False)[0]=='NUMERICALLY_UNRESOLVED'
    assert m.classify(None,None,'delta',qualified=False)[0]=='NUMERICALLY_UNRESOLVED'


def test_positive_contrast_does_not_prove_monotonicity():
    c=m.Curve([10,12,13,14,17,18,19,23],[0,2,3,2,0,1,0,4])
    assert m.nominal_contrast(c,cal(),[(1,m.LOWER),(-1,m.UPPER)])>0
    assert np.any(np.diff(c.z)>0) and np.any(np.diff(c.z)<0)


def test_exact_observation_map_witness():
    cases=m.witness()
    assert [Fraction(v['porosity_contrast']) for v in cases]==[Fraction(2,25),0,Fraction(-2,25)]
    for case in cases:
        phi=list(map(Fraction,case['phi']));sat=list(map(Fraction,case['saturation']))
        assert all(0<=v<=1 for v in phi+sat)
        assert [p*(1-s) for p,s in zip(phi,sat)]==[Fraction(3,25),Fraction(2,25)]


def test_continuous_box_affine_oracle():
    # Exact affine A under inverse calibration; include continuous horizontal
    # pointwise departures and vertical box. The analytic extreme must be inside.
    ca=cal();ca['anchor_allowance_pt']=.02
    c=simple(z=(.01*10,.01*23));terms=[(1,m.LOWER),(-1,m.UPPER)]
    h=.003
    lo,hi=m.certified_contrast(c,ca,terms,h,integration_cells=32)
    aa=[11.98,12.02];bb=[21.98,22.02]
    gg=[.4/(.4+.04),.4/(.4-.04)]
    values=[g*(-.005*(b-a)+local) for a in aa for b in bb for g in gg
            for local in [-2*h*(1+.01),2*h*(1+.01)]]
    assert lo<=min(values) and hi>=max(values)


def test_reduction_preserves_small_terms_without_blas(monkeypatch):
    # A cancellation-sensitive sum must retain the small term. CPU-specific
    # BLAS reductions previously changed committed nominal values' last bits.
    def forbidden(*args,**kwargs):
        raise AssertionError('BLAS reduction is not a reproducible serialization contract')
    monkeypatch.setattr(np,'dot',forbidden)
    assert m.deterministic_dot([1e16,1.,-1e16],[1.,1.,1.])==1.
    curve=m.Curve([10.,15.,20.,22.],[1.,1.5,2.,2.2])
    cal={'x12':12.,'x22':22.,'gamma':1.}
    assert m.nominal_contrast(curve,cal,[(1.,m.LOWER),(-1.,m.UPPER)])==pytest.approx(-.5)
    assert m.local_box_radius([1.,-2.],[.1,.2])==pytest.approx(.5)


def test_offline_regeneration_in_fresh_process(tmp_path,calculated):
    # A fresh interpreter denies network and PDF parser imports; canonical bytes
    # and scientific artifacts must still reproduce exactly.
    script='''
import builtins, socket
from pathlib import Path
real_import=builtins.__import__
def guarded(name,*args,**kwargs):
    if name.split('.')[0] in {'pymupdf','fitz','requests','urllib3'}:
        raise AssertionError('Forbidden offline dependency: '+name)
    return real_import(name,*args,**kwargs)
builtins.__import__=guarded
def denied(*args,**kwargs):raise AssertionError('Network forbidden')
socket.create_connection=denied
from puckworks.analysis.mo2023_wet_ct_profiles import generate
generate(Path(OUTPUT))
'''.replace('OUTPUT',repr(str(tmp_path)))
    subprocess.run([sys.executable,'-c',script],cwd=m.ROOT,check=True,
                   env={**os.environ,'PYTHONHASHSEED':'7','OPENBLAS_CORETYPE':'Nehalem'})
    for name in ['contrasts.csv','contrasts.json','band_means.json','summary.json','RESULT.md']:
        assert (tmp_path/name).read_bytes()==(m.BUNDLE/name).read_bytes(),name


def test_source_comparison_and_visibility_audit():
    g=json.loads((m.BUNDLE/'source_geometry_comparison.json').read_text())
    assert len(g['profiles'])==24
    assert all(p['same_operators_and_topology'] for p in g['profiles'])
    assert max(p['max_abs_y_mm_after_tick_scaling'] for p in g['profiles'])<1e-4
    assert max(p['max_abs_signal_after_tick_scaling'] for p in g['profiles'])<5e-6
    meta,rows,_=m.load()
    center=rows['14b_r0.92']
    statuses={s for r in center for _,_,s in json.loads(r['visibility_parts'])}
    assert statuses=={'VISIBLE','AXIS_CLIPPED','LEGEND_OCCLUDED'}
    assert all(r['operator']=='l' for rr in rows.values() for r in rr)


def test_discovery_preserves_signal_ceiling():
    from puckworks.insights.corpus_map import build
    from tools.build_available_data_register import build as register
    dataset='mo2023/fig14_fig16_segmented_profiles'
    state=build()
    edges=[r for r in state['relations'] if r['source']=='dataset:'+dataset]
    assert any(r['type']=='DERIVED_FROM' for r in edges)
    assert not any(r['type']=='MEASURES' and r['target'] in
                   {'observable:porosity','observable:permeability'} for r in edges)
    data=register()
    families=data['families']
    mo=next(f for f in families if f['family_id']=='MO2023')
    assert set(mo['manifest_dataset_ids'])=={'mo2023/forchheimer','mo2023/fig8a',dataset}
    assert mo['dataset_scopes'][dataset]['PHYSICAL_VALIDATION']=='NOT_ESTABLISHED'
