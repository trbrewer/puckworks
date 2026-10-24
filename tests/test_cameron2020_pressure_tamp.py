"""Material arithmetic, dependency, missingness and extraction-contract checks."""
import copy
from fractions import Fraction as Q
import json

from puckworks.analysis import cameron2020_pressure_tamp as m


def data():
    return json.loads(m.DATA.read_text())


def test_design_and_native_source_accounting():
    d=data()
    obs=d['observations']
    assert len(obs)==len({o['observation_id'] for o in obs})==16
    assert {(o['pressure_label_bar'],o['grind_label'],o['force_group']) for o in obs} == {
        (p,g,f) for p in [6,9] for g in ['1.3','1.5'] for f in ['F1','F2','F3','F4']}
    assert all(o['nominal_force_N'] is None and o['replicate_n'] is None for o in obs)
    for o in obs:
        assert o['marker_shape']==('triangle' if o['pressure_label_bar']==9 else 'circle')
        for xy in o['anchor_candidates']:
            assert all(a<=v<=b for (a,b),v in zip(o['central_xy_enclosure_pt'],xy['xy_pt']))
    groups=d['force_groups']
    assert all(g['common_x_intersection_pt'][0]<=g['common_x_intersection_pt'][1] for g in groups)
    assert all(a['plotted_force_union_N'][1]<b['plotted_force_union_N'][0] for a,b in zip(groups,groups[1:]))
    acct=d['source_object_accounting']
    ids=[acct['frame']]+sum((acct[k] for k in ['tick_paths','connector_paths','marker_paths','bar_segment_paths']),[])
    assert len(ids)==len(set(ids))==71
    assert set(ids)==set(range(84,155))
    # The short solid dashes terminate away from the marker. Do not treat those
    # interior ends as central-summary anchors (a demonstrated extraction risk).
    fine9=next(o for o in obs if o['observation_id']=='S2-P9-G1.3-F2')
    assert fine9['nominal_xy_pt'][0]>179.9
    assert fine9['nominal_xy_pt'][1]==483.7791442871094


def test_bar_missingness_is_not_zero_variability():
    d=data()
    missing={o['observation_id'] for o in d['observations'] if o['bar_y_endpoints_pt'] is None}
    assert missing=={'S2-P6-G1.3-F2','S2-P9-G1.5-F2','S2-P9-G1.5-F3','S2-P9-G1.5-F4'}
    for o in d['observations']:
        if o['observation_id'] in missing:
            assert o['bar_objects']==[] and o['displayed_time_endpoints_s'] is None
        else:
            assert len(o['bar_objects'])==2
            assert o['displayed_time_endpoints_s'][0]<o['displayed_time_endpoints_s'][1]
    results=m.compute(d)['contrasts']
    assert len(results)==36
    assert len({r['contrast_id'] for r in results})==18
    for r in results:
        expected=r['layer']=='B' and bool(missing.intersection(r['terms']))
        assert (r['bounds_s'] is None)==expected
        assert (r['sign']=='UNSUPPORTED/INCOMPLETE')==expected
    assert sum(r['bounds_s'] is None for r in results)==9


def test_signed_arithmetic_against_direct_source_coordinate_witnesses():
    d=data()
    result={r['contrast_id']:r for r in m.compute(d)['contrasts'] if r['layer']=='A'}
    # Independent nominal reduction of four source y coordinates for F1 I.
    scale=-30/(635.8355712890625-424.7945556640625)
    expected=(473.9888916015625-550.5636596679688-595.6668090820312+587.960693359375)*scale
    assert abs(result['I-F1']['nominal_central_contrast_s']-expected)<1e-12
    assert result['DP-G1.3-F1']['sign']=='POSITIVE'  # decreasing PDF y means longer time
    assert result['DP-G1.5-F1']['sign']=='NEGATIVE'
    for g in ['1.3','1.5']:
        j=result[f'J-G{g}']['nominal_central_contrast_s']
        dp=result[f'DP-G{g}-F4']['nominal_central_contrast_s']-result[f'DP-G{g}-F1']['nominal_central_contrast_s']
        df=result[f'DF-P9-G{g}']['nominal_central_contrast_s']-result[f'DF-P6-G{g}']['nominal_central_contrast_s']
        assert abs(j-dp)<1e-12 and abs(j-df)<1e-12
    assert all(sum(s['terms'].values())==0 for s in m.specifications())


def test_common_affine_offset_cancels_and_common_scale_is_applied_once():
    d=data(); shifted=copy.deepcopy(d)
    # Preserve exact input decimal arithmetic while applying an arbitrary shared offset.
    for t in shifted['calibration']['y_ticks']:
        t['coordinate_pt']=str(m.q(t['coordinate_pt'])+100)
    for o in shifted['observations']:
        o['nominal_xy_pt'][1]=str(m.q(o['nominal_xy_pt'][1])+100)
        o['central_xy_enclosure_pt'][1]=[str(m.q(v)+100) for v in o['central_xy_enclosure_pt'][1]]
        if o['bar_y_endpoints_pt']:
            o['bar_y_endpoints_pt']=[str(m.q(v)+100) for v in o['bar_y_endpoints_pt']]
    a=m.compute(d)['contrasts'];b=m.compute(shifted)['contrasts']
    assert [(r['exact_bounds_s'],r['nominal_central_contrast_s']) for r in a]==[(r['exact_bounds_s'],r['nominal_central_contrast_s']) for r in b]
    obs={o['observation_id']:o for o in d['observations']}
    r=a[8]  # I-F1, four original observations
    low=high=Q(0)
    for oid,c in r['terms'].items():
        ends=sorted(c*m.q(v) for v in obs[oid]['central_xy_enclosure_pt'][1])
        low+=ends[0];high+=ends[1]
    scales=list(map(m.q,d['calibration']['signed_time_scale_s_per_pt']))
    # Decimal presentation of stored scale is approximate; exact production scale
    # is computed from uncertain tick endpoints, checked here to sub-picosecond.
    oracle=sorted([low*scales[0],low*scales[1],high*scales[0],high*scales[1]])
    assert abs(float(oracle[0])-r['bounds_s'][0])<1e-12
    assert abs(float(oracle[-1])-r['bounds_s'][1])<1e-12


def test_extent_layer_does_not_add_marker_uncertainty_twice():
    d=data(); widened=copy.deepcopy(d)
    for o in widened['observations']:
        o['central_xy_enclosure_pt'][1][0]-=10
        o['central_xy_enclosure_pt'][1][1]+=10
    a=m.compute(d)['contrasts'];b=m.compute(widened)['contrasts']
    assert [r['exact_bounds_s'] for r in a[18:]]==[r['exact_bounds_s'] for r in b[18:]]
    assert a[0]['exact_bounds_s']!=b[0]['exact_bounds_s']


def test_outward_rounding_and_strict_signs():
    assert m.outward([Q('-1.001'),Q('-0.999')])==['-1.01','-0.99']
    assert m.outward([Q('0.001'),Q('1.001')])==['0.00','1.01']
    for r in m.compute(data())['contrasts']:
        if r['bounds_s'] is None:continue
        lo,hi=map(Q,r['exact_bounds_s']);rlo,rhi=map(Q,r['reported_bounds_s'])
        assert rlo<=lo<=hi<=rhi
        assert r['sign']==('POSITIVE' if lo>0 else 'NEGATIVE' if hi<0 else 'UNRESOLVED')
    # Synthetic zero-containing observation enclosure must remain unresolved.
    d=data()
    for o in d['observations']:
        o['central_xy_enclosure_pt'][1]=[500,600]
    assert all(r['sign']=='UNRESOLVED' for r in m.compute(d)['contrasts'][:18])


def test_reproduction_and_qualified_projection(tmp_path):
    d=data()
    assert m.qualify(copy.deepcopy(d))==d
    m.write(d,tmp_path)
    for name in ['contrasts.json','contrasts.csv','observations.csv','CONTRASTS.md','COMPARISON.svg']:
        assert (tmp_path/name).read_bytes()==(m.OUTPUT/name).read_bytes()
