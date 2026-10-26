"""Load-bearing source, interpolation, extrema and graphical-contract checks."""
import copy
import hashlib
import json

import pytest

from puckworks.analysis import moroney2015_fixed_flow_pressure as m

SOURCE = json.loads((m.BUNDLE/'source_objects.json').read_text())


def row(x, y, i, component='1', dx=0, dy=0):
    x, y, dx, dy = map(m.q, (x, y, dx, dy))
    return dict(id=str(i), x=x, y=y, component=component, x_lower=x-dx, x_upper=x+dx,
                native_y_lower=y-dy, native_y_upper=y+dy)


def test_complete_objects_legend_subpaths_and_lineage():
    rr = SOURCE['legacy_rows']
    assert len(rr) == len({r['source_id'] for r in rr}) == 94
    assert [r['legacy_row_number'] for r in rr] == list(range(1, 95))
    assert [r['legacy_row_number'] for r in rr if r['disposition']=='legend_sample'] == [7, 32, 54, 79]
    for drawing, n in [(437, 2), (439, 6), (456, 8)]:
        assert len([r for r in rr if r['drawing_index']==drawing]) == n
    assert len(SOURCE['lineage']) == len({r['figure3_row_id'] for r in SOURCE['lineage']}) == 44
    assert max(abs(r['delta_mass_g']) for r in SOURCE['lineage']) < .1
    assert max(abs(r['delta_concentration_mg_g']) for r in SOURCE['lineage']) < .1
    assert all(r['stroke_width_pt']==0 for r in rr)
    from puckworks.data import moroney2015_data
    assert len(moroney2015_data()['fig12_pressure']) == 94


def test_tick_direction_calibration_padding_signed_tails_and_raw_preservation():
    obs = m.qualify(SOURCE)
    for panel in ['a', 'b']:
        cal = SOURCE['calibration'][panel]
        assert len(cal['ticks']['x']) == 6 and len(cal['ticks']['y']) == 5
        assert len(cal['all_tick_checks']) == 94
        a, b, vmax, pad = m.axis(cal, 'y')
        assert a > b and vmax == 200 and pad > m.q('.4')
        assert cal['frame']['bbox_pt'][3] > float(a)  # bottom is NOT zero
    assert min(o['y'] for o in obs) < 0
    assert len(obs) == 90
    identities = json.loads((m.ROOT/'docs/analysis/sci_md_moroney_transfer_001/identities.json').read_text())
    for path, digest in identities['source_files'].items():
        assert hashlib.sha256((m.ROOT/path).read_bytes()).hexdigest() == digest
    low = [r for r in obs if r['panel']=='a' and r['series']=='L']
    assert low[0]['x'] != m.q(low[0]['legacy_mass_g'])  # no legacy substitution


def test_unequal_grids_exact_knots_brackets_and_no_extrapolation():
    ll = [row(0, 0, 'l0'), row(2, 4, 'l1'), row(4, 0, 'l2')]
    hh = [row(1, 3, 'h0'), row(3, 1, 'h1')]
    assert m.evaluate(ll, m.q(2)) == dict(value=m.q(4), ids=['l1'], weights=[m.q(1)])
    v = m.evaluate(hh, m.q(2))
    assert v['ids']==['h0','h1'] and v['weights']==[m.q('.5')]*2 and v['value']==2
    assert m.evaluate(hh, m.q(0)) is None
    kk = m.union_knots(m.common_components(ll, hh))
    assert [k['mass_g'] for k in kk] == [1,2,3]
    assert [k['delta'] for k in kk] == [1,-2,-1]


def test_crossings_ties_constants_and_gap_extrema():
    ll = [row(0, 0, 'l0'), row(1, 0, 'l1'), row(2, 0, 'l2'), row(3, 0, 'l3')]
    hh = [row(0, -2, 'h0'), row(1, 2, 'h1'), row(2, 2, 'h2'), row(3,-2,'h3')]
    k = m.union_knots(m.common_components(ll,hh))
    e=m.extrema(k)
    assert len(e['minimum']['attaining_knots'])==2
    assert len(e['maximum_absolute']['attaining_knots'])==4
    assert e['maximum']['attaining_intervals'][0]['mass_g']==[1,2]
    # A sign-crossing segment's endpoints are not a constant absolute-max interval.
    assert len(e['maximum_absolute']['attaining_intervals'])==1
    ll = [row(0,0,'a'), row(1,0,'b'), row(3,0,'c','2'), row(4,0,'d','2')]
    hh = [row(0,1,'e'), row(4,1,'f')]
    common=m.common_components(ll,hh)
    assert len(common)==2
    ext=m.extrema(m.union_knots(common))
    assert len(ext['maximum']['attaining_intervals'])==2
    assert not any(c['start']<=2<=c['end'] for c in common)
    with pytest.raises(ValueError, match='Duplicate x'):
        m.common_components([row(1,2,'a'),row(1,3,'b')],hh)


def test_source_ambiguity_splits_components_but_legend_does_not():
    d=copy.deepcopy(SOURCE)
    d['legacy_rows'][4]['disposition']='ambiguous'
    obs=m.qualify(d)
    low=[r for r in obs if r['panel']=='a' and r['series']=='L']
    assert len(m.components(low))==2
    assert len(m.components([r for r in m.qualify(SOURCE) if r['panel']=='a' and r['series']=='L']))==1


def test_horizontal_only_vertical_only_and_convex_weights():
    rr=[row(0,0,'a',dx='.2'),row(2,2,'b',dx='.2')]
    s=m.sensitivity_series(rr,m.q(1))
    assert s['native_ordinate_bounds']==[m.q('.8'),m.q('1.2')]
    rr=[row(0,0,'a',dy='.2'),row(2,2,'b',dy='.2')]
    assert m.sensitivity_series(rr,m.q(1))['native_ordinate_bounds']==[m.q('.8'),m.q('1.2')]
    for b in s['possible_brackets']:
        assert 0<=b['weight_bounds'][0]<=b['weight_bounds'][1]<=1


def test_alternate_brackets_universal_support_and_order_refusal():
    rr=[row(0,0,'a',dx='.2'),row(1,10,'b',dx='.2'),row(2,0,'c',dx='.2')]
    s=m.sensitivity_series(rr,m.q(1))
    assert len(s['possible_brackets'])==2
    assert s['native_ordinate_bounds']==[m.q(8),m.q(10)]
    # A possible first bracket alone cannot certify universal coverage at 0.1.
    s=m.sensitivity_series(rr,m.q('.1'))
    assert s['status']=='UNSUPPORTED' and 'Universal' in s['reason']
    assert m.sensitivity_series(rr,m.q('.2'))['status']=='SUPPORTED'
    rr=[row(0,0,'a',dx=1),row(1,2,'b',dx=1)]
    assert 'ordering' in m.sensitivity_series(rr,m.q('.5'))['reason']


def test_zero_inclusion_and_outward_exact_rounding():
    assert m.sign([m.q(0),m.q(1)])=='SIGN_UNRESOLVED'
    assert m.sign([m.q(-1),m.q(0)])=='SIGN_UNRESOLVED'
    assert m.sign([m.q('1e-30'),m.q(1)])=='POSITIVE'
    assert m.outward([m.q('-0.0000001'),m.q('0.0010001')],3)==['-0.001','0.002']


def test_shared_vertical_offset_cancels_and_no_double_calibration():
    obs=m.qualify(SOURCE)
    rr=m.analyze(obs,SOURCE)
    shifted=copy.deepcopy(SOURCE)
    for c in shifted['calibration'].values():
        for t in c['ticks']['y']:
            t['coordinate_pt']=str(m.q(t['coordinate_pt'])+100)
        for t in c['all_tick_checks']:
            if t['axis']=='y':t['coordinate_pt']=str(m.q(t['coordinate_pt'])+100)
    for o in shifted['legacy_rows']:
        o['center_pt'][1]=str(m.q(o['center_pt'][1])+100)
        for c in o['center_candidates_pt']:c[1]=str(m.q(c[1])+100)
    r2=m.analyze(m.qualify(shifted),shifted)
    for a,b in zip(rr['contrasts'],r2['contrasts']):
        assert a['delta']==b['delta'] and a['delta_bounds']==b['delta_bounds']
    # y marginals include calibration; contrast deliberately consumes native bounds.
    for o in obs:o['y_lower'],o['y_upper']=m.q(-100000),m.q(100000)
    r3=m.analyze(obs,SOURCE)
    assert [r['delta_bounds'] for r in rr['contrasts']]==[r['delta_bounds'] for r in r3['contrasts']]


def test_all_fourteen_nominal_inclusion_optional_refusal_and_roundtrip(tmp_path):
    result=m.produce(tmp_path,make_figure=False)
    assert len(result['contrasts'])==14
    assert [(r['panel'],int(r['mass_g'])) for r in result['contrasts']]==[(p,g) for p in 'ab' for g in m.GRID]
    for r in result['contrasts']:
        assert r['central_support_status']==r['sensitivity_support_status']=='SUPPORTED'
        assert r['delta_bounds'][0]<=r['delta']<=r['delta_bounds'][1]
        assert r['delta_S_mg'] is None and r['solute_mass_status']=='UNSUPPORTED'
        assert r['relative_contrast'] is None
        for key in ['L_bracket','H_bracket']:
            assert sum(r[key]['weights'])==1
    assert [(r['panel'],r['mass_g']) for r in result['contrasts'] if r['sensitivity_sign']=='NEGATIVE']==[('a',800)]
    assert len(m.load_qualified(tmp_path))==90
    rebuilt=m.analyze(m.load_qualified(tmp_path),SOURCE)
    assert rebuilt==result
    for name in ['qualified_observations.csv','contrasts.csv','union_knots.csv','results.json','RESULT.md']:
        assert (tmp_path/name).read_bytes()==(m.BUNDLE/name).read_bytes()


def test_central_survives_unsupported_sensitivity_and_missing_slot():
    cal=SOURCE['calibration']['a']
    ll=[row(0,0,'a',dx='.2'),row(2,0,'b',dx='.2')]
    hh=[row(0,1,'c',dx='.2'),row(2,1,'d',dx='.2')]
    common=m.common_components(ll,hh)
    r=m.contrast_slot('a',m.q('.1'),common,cal)
    assert r['central_support_status']=='SUPPORTED' and r['delta']==1
    assert r['sensitivity_support_status']=='UNSUPPORTED' and r['delta_bounds'] is None
    r=m.contrast_slot('a',m.q(3),common,cal)
    assert r['central_support_status']=='UNSUPPORTED' and r['delta'] is None
    assert r['central_reason']


def test_explicit_pdf_identity_refusal(tmp_path):
    from tools.extract_moroney2015_fixed_flow_pressure import extract
    p=tmp_path/'not-source.pdf'
    p.write_bytes(b'not the accepted PDF')
    with pytest.raises(ValueError,match='identity mismatch'):
        extract(p)
