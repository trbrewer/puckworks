"""Source-independent checks of the bounded MASS addendum."""
import copy
import json
import math

import pytest

from puckworks.analysis import mass_decision_resolution as m


def metric(r=1., b=.1, ur=.01, ub=.02):
    return {'R_pp': r, 'B_pp': b, 'abs_B_pp': abs(b), 'R_allowance_pp': ur, 'B_allowance_pp': ub,
            'max_interval_allowance_kg': 1e-12}


def shots(case='003'):
    result = {}
    cs = m.PRIMARY + m.TEMP + m.FLOW if case == '001' else m.PRIMARY
    for a, arm in enumerate(m.ARMS[case]):
        rows = []
        for i, (s, c) in enumerate(m.members(cs).items()):
            n = 5 if case == '003' else 6
            rows.append({'shot': s, 'condition': c, 'expected_assays': n, 'valid_assays': n,
                         'supported_assays': n, 'out_of_domain_fractions': [],
                         'collection_intervals': 11, 'numerically_qualified': True, 'full_support': True,
                         'assayed_mass_kg': .03, 'complete_collected_mass_kg': .06,
                         'metrics': metric(.6 + i * .02 + a * .03, (-1)**i * .2, .001 * (i+1), .0001),
                         'supported_only_diagnostic': None})
        result[arm] = rows
    return result


def test_nested_after_deletion_differs_from_pooling():
    ss = shots()
    a = m.CANDIDATE['003']
    ss[a][0]['metrics']['R_pp'] = 3
    baseline = m.scenario('003', ss, m.PRIMARY)
    omitted = ss[a][0]['shot']
    s = m.scenario('003', ss, m.PRIMARY, omitted)
    expected = sum(sum(r['metrics']['R_pp'] for r in ss[a] if r['condition'] == c and r['shot'] != omitted) /
                   (2 if c == 'PRED-C01' else 3) for c in m.PRIMARY) / 4
    assert s['arms'][a]['metrics']['R_pp'] == pytest.approx(expected)
    pooled = sum(r['metrics']['R_pp'] for r in ss[a] if r['shot'] != omitted) / 11
    assert abs(expected - pooled) > .001
    assert baseline['arms'][a]['metrics']['abs_B_pp'] == pytest.approx(.2)
    assert baseline['arms'][a]['metrics']['B_pp'] == pytest.approx(0.)


@pytest.mark.parametrize('case,n', [('001', 66), ('002', 66), ('003', 55)])
def test_whole_shot_paired_omission_and_allowances(case, n):
    ss = shots(case)
    base = m.scenario(case, ss, m.PRIMARY)
    s = m.scenario(case, ss, m.PRIMARY, 'PRED-E01-R1')
    assert s['physical_shots'] == 11 and s['intervals_per_arm'] == n
    for a in m.ARMS[case]:
        assert sum(r['shots'] for r in s['conditions'][a]) == 11
        assert s['arms'][a]['metrics']['R_allowance_pp'] != base['arms'][a]['metrics']['R_allowance_pp']
    _, records = m.analyze(case, ss)
    assert len(records) == 13


def test_temperature_no_primary_requirements():
    p, records = m.analyze('001', shots('001'), m.TEMP)
    assert len(records) == 7
    assert p['deleted_scenario_shots'] == 5 and p['deleted_scenario_intervals_per_arm'] == 30
    assert all(not r['requirement_relation_counts'] for r in p['pairs'].values())


@pytest.mark.parametrize('field,value', [('expected_assays', 6), ('valid_assays', 6), ('collection_intervals', 10), ('shot', 'wrong')])
def test_exact_suffix_and_member_accounting(field, value):
    ss = shots()
    ss[m.ARMS['003'][0]][0][field] = value
    with pytest.raises(ValueError):
        m.validate_shots('003', ss)


def test_duplicate_physical_member_rejected():
    ss = shots()
    ss[m.ARMS['003'][0]][1] = copy.deepcopy(ss[m.ARMS['003'][0]][0])
    with pytest.raises(ValueError):
        m.validate_shots('003', ss)


def test_affine_twenty_percent_not_fifteen():
    p = m.contrast({'metrics': metric(.83, .1, 0, 0)}, {'metrics': metric(1, .1, 0, 0)})
    assert p['headroom']['absolute_gain']['relation'] == 'PASS'
    assert p['headroom']['relative_20_percent']['relation'] == 'FAIL'
    assert p['values']['relative_gain'] == pytest.approx(.17)


@pytest.mark.parametrize('v,u,limit,expected', [(1,0,1,'PASS'), (1,.1,1,'NUMERICALLY_UNRESOLVED'), (1.1,0,1,'FAIL')])
def test_original_upper_boundaries(v, u, limit, expected):
    assert m.original.threshold(v,u,limit) == expected


def test_strict_condition_win_boundaries():
    ss = shots('002')
    for a, rows in ss.items():
        for r in rows:
            r['metrics'] = metric(.5 if a == 'MTF' else .75, 0, .125, 0)
    s = m.scenario('002', ss, m.PRIMARY)
    assert s['pairs']['M0']['definite_wins'] == 0
    assert s['pairs']['M0']['possible_wins'] == 4
    for r in ss['MTF']:
        r['metrics']['R_pp'] = 1.
    s = m.scenario('002', ss, m.PRIMARY)
    assert s['pairs']['M0']['possible_wins'] == 0
    assert s['pairs']['M0']['headroom']['condition_wins']['relation'] == 'FAIL'


def test_nonpositive_reference_ratio_undefined():
    p = m.contrast({'metrics': metric(0,0,0,0)}, {'metrics': metric(0,0,0,0)})
    assert p['values']['relative_gain'] is None
    assert p['bounds']['relative_gain'] is None


def test_incomplete_flow_preserves_fail_witness():
    ss = shots('001')
    for rows in ss.values():
        for r in rows:
            if r['condition'] == 'PRED-C07':
                r['metrics'] = None
                r['full_support'] = False
            if r['condition'] == 'PRED-C08':
                r['metrics']['R_pp'] = 2.
    cc = m.original.condition_metrics(ss['MASS'])
    result = m.original.aggregate(cc, m.FLOW)
    assert result['metrics'] is None and result['adequacy_status'] == 'FAIL'
    assert next(c for c in cc if c['condition'] == 'PRED-C07')['adequacy'] == 'UNSUPPORTED_OR_UNQUALIFIED'


def test_decomposition_opposing_terms_and_no_net_percentages():
    d = m.decomposition(metric(1, .8, 0, 0), metric(1.2, .2, 0, 0))
    v = d['values']
    assert v['delta_B2_pp2'] == pytest.approx(-.60)
    assert v['delta_V_pp2'] == pytest.approx(1.04)
    assert v['bias_contribution_pp'] == pytest.approx(-.6/2.2)
    assert v['variation_contribution_pp'] == pytest.approx(1.04/2.2)
    assert v['bias_contribution_pp'] + v['variation_contribution_pp'] == pytest.approx(.2)
    assert v['variation_contribution_pp'] > .2


def test_mse_is_mean_squared_shot_R_not_squared_mean_R():
    rows = [m.decomposition(metric(1,0,0,0), metric(r,0,0,0))['values'] for r in (1,3)]
    mse = sum(r['MSE_gain_pp2'] for r in rows) / 2
    assert mse == 4
    assert mse != ((1+3)/2)**2 - 1


def test_signed_square_zero_crossing():
    assert m.algebra.square([-.3,.2])[0] == 0
    assert m.algebra.square([-.3,.2])[1] >= .09


def test_zero_denominator_cases():
    z = metric(0,0,0,0)
    d = m.decomposition(z,z)
    assert d['values']['bias_contribution_pp'] == 0
    assert d['bounds']['bias_contribution_pp'] == [0,0]
    uncertain = m.decomposition(metric(0,0,.1,.1), z)
    assert uncertain['bounds']['bias_contribution_pp'] is None


def test_negative_point_variation_not_excused_by_allowance():
    with pytest.raises(ValueError, match='NEGATIVE_POINT'):
        m.shot_components(metric(1,1.01,10,10))


def test_narrow_roundoff_counted():
    d = m.decomposition(metric(1,math.nextafter(1,math.inf),0,0), metric(1,0,0,0))
    assert d['negative_roundoff_corrections'] == 1


def test_own_endpoint_envelope():
    records = [(1.,.1),(2.,.01),(.5,.4)]
    s = m.family_summary(records, lambda r:r[0], lambda r:[r[0]-r[1],r[0]+r[1]])
    assert s['deletion_only_range'] == [.5,2]
    assert s['deletion_only_numerical_envelope'] == pytest.approx([.1,2.01])


@pytest.mark.parametrize('which', ['anchor','scored','unassayed','shared'])
def test_primitive_mass_dependencies(which):
    masses = [1.,2.,3.,4.,5.]
    f = (2,3,5)
    before = m.primitive_mass_map(masses,f)
    after_mass = masses.copy()
    idx = {'anchor':0,'scored':1,'unassayed':3}.get(which)
    if idx is not None: after_mass[idx] += .25
    else: after_mass = [2*v for v in masses]
    after = m.primitive_mass_map(after_mass,f)
    if which == 'anchor':
        assert after['anchor_width'] != before['anchor_width']
        assert after['weights'] == before['weights'] and after['widths'] == before['widths']
        assert all(a == pytest.approx([b[0]+.25,b[1]+.25]) for a,b in zip(after['windows'],before['windows']))
    elif which == 'scored':
        assert after['anchor_width'] == before['anchor_width']
        assert all(a != b for a,b in zip(after['weights'],before['weights']))
        assert after['windows'][0][0] == before['windows'][0][0]
        assert after['windows'][1][0] == before['windows'][1][0]+.25
    elif which == 'unassayed':
        assert after['weights'] == before['weights'] and after['widths'] == before['widths']
        assert after['windows'][:2] == before['windows'][:2]
        assert after['windows'][2] == pytest.approx([before['windows'][2][0]+.25,before['windows'][2][1]+.25])
    else:
        assert after['weights'] == before['weights']
        assert after['anchor_width'] == 2*before['anchor_width']
        assert after['widths'] == [2*v for v in before['widths']]


def test_anchor_and_shared_calibration_derivatives():
    q,g,y,delta = 4.,.3,2.,.01
    assert ((q+delta)*g-q*g)/delta == pytest.approx(g)
    assert (((q+delta)*g-(y+delta))-(q*g-y))/delta == pytest.approx(g-1)


def test_public_projection_excludes_reconstructive_outputs():
    public, private = m.analyze('003',shots())
    text = json.dumps(public)
    assert not any(s in text for s in m.members(m.PRIMARY))
    assert 'omitted' not in text and 'shots"' not in json.dumps(public['pairs'])
    assert 'scenarios' not in text and 'errors_pp' not in text
    assert 'condition_requirement_relation_counts' in text
    assert len(private) == 13 and private[1]['omitted']
    for a in public['arms'].values():
        assert all(set(v) <= {'R_pp','abs_B_pp'} for v in a['condition_requirement_relation_counts'].values())


def test_case003_original_conjunction_precedence_preserved():
    assert m.anchored.conjunction(['FAIL','NUMERICALLY_UNRESOLVED']) == 'NUMERICALLY_UNRESOLVED'


def test_private_output_exclusive_and_source_protection(tmp_path):
    path = tmp_path/'new'
    m.private_output(path)
    with pytest.raises(FileExistsError): m.private_output(path)
    with pytest.raises(ValueError): m.private_output(path/'child',[path])


def test_direct_fraction_check_retains_unsupported_unqualified_slot():
    # The historical out-of-domain slot has no qualified numerical prediction;
    # it stays unsupported rather than invalidating other retained calculations.
    obs = [dict(shot='s', condition='c', fraction=f, campaign='PREDICTION_2022_03',
                b0=f-1., b1=float(f), mass_kg=1., eligible=True, solute_kg=.01,
                collection_mass_kg=2., collection_count=2, source_rounding_allowance_kg=0.) for f in (1,2)]
    pp = [dict(o, in_domain=o['fraction']==1, numerical_qualified=o['fraction']==1,
               predicted_solute_kg=.02 if o['fraction']==1 else None,
               integration_allowance_kg=0. if o['fraction']==1 else None) for o in obs]
    ss = m.original.shot_metrics(obs,pp)
    data = {'predictions.json':{a:copy.deepcopy(pp) for a in m.ARMS['001']}}
    result, _ = m.direct_check('001',data,{a:copy.deepcopy(ss) for a in m.ARMS['001']},obs)
    assert result['pass']


def test_optional_observations_without_predictions():
    import csv
    import io
    ss = shots('003')
    coords, rows = [], []
    for shot,c in m.members(m.PRIMARY).items():
        for f in (2,3,5,7,10):
            coords.append(dict(shot=shot, condition=c, fraction=f, campaign='PREDICTION_2022_03',
                b0=(f-1)*.001, b1=f*.001, mass_kg=.001, source_id='source', mass_basis='MEASURED_MASS_G',
                mass_prefix='SOURCE_SHOT_mE_cum_ALL_INTERVENING_VIALS'))
            rows.append(dict(shot_id=shot, condition_id=c, fraction_id=f, campaign_id='PREDICTION_2022_03',
                source_id='source', analyte='TDS', concentration_unit='percent', validity='VALID',
                fraction_liquid_g_or_ml='1', measured_concentration='1', derived_analyte_mass_mg='10'))
    text = io.StringIO()
    writer = csv.DictWriter(text, list(rows[0])); writer.writeheader(); writer.writerows(rows)
    chosen = m.observation_coordinates('003', {'coordinates.json':coords}, {'coordinates.json':'AUTHENTICATED'})
    obs, duplicates = m.observations('003', chosen, ss, text.getvalue().encode())
    summary, _ = m.variability(obs)
    assert len(obs) == 60 and duplicates == 0
    assert summary['physical_shots'] == 12 and summary['cells'] == 20
    assert summary['TDS_sample_SD_pp_across_cells'] == [0,0]


def test_present_coordinate_mismatch_never_uses_prediction_fallback():
    data = {'predictions.json':{'M0':['fallback']}}
    assert m.observation_coordinates('002',data,{'coordinates.json':'UNAVAILABLE'}) == ['fallback']
    assert m.observation_coordinates('002',data,{'coordinates.json':'HASH_MISMATCH_DEPENDENT_COMPONENT_BLOCKED'}) is None
