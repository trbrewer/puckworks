"""Source defects, conservative arithmetic, support and fixed-partner regressions."""
import csv
from fractions import Fraction as F
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
import zipfile

import pytest

from puckworks.analysis import smrke2024_transient as s
from puckworks import data as d


@pytest.fixture
def contract():
    return json.loads((s.DATA/'contract.json').read_text())


def test_authenticated_native_source_and_freeze(contract):
    source = contract['source']
    p = s.DATA.parent/source['docx']
    assert s.digest(p) == source['docx_sha256']
    with zipfile.ZipFile(p) as z:
        assert hashlib.sha256(z.read(source['image_member'])).hexdigest() == source['image_sha256']
        assert '250 solid lines' in ''.join(ET.fromstring(z.read('word/document.xml')).itertext())
    freeze = json.loads((s.OUTPUT/'CONTRACT_FREEZE.json').read_text())
    for path, expected in freeze['files'].items():
        assert s.digest(s.ROOT/path) == expected
    for correction in freeze['material_corrections']:
        assert s.digest(s.ROOT/correction['file']) == correction['sha256']


def test_tick_residuals_full_zero_to_seven_scale(contract):
    c = contract['calibration']
    for x, t, residual in zip(c['x_ticks_px'], c['x_tick_values_s'], c['nominal_x_tick_residual_px']):
        assert F(x)-(78+F(t)*1469/80) == F(residual)
    for y, q, residual in zip(c['y_ticks_px'], c['y_tick_values_g_s'], c['nominal_y_tick_residual_px']):
        assert F(y)-(943-F(q)*865/7) == F(residual)
    cal = s.Calibration(contract)
    assert cal.flow(78, 78)[0] < 7 < cal.flow(78, 78)[1]
    assert cal.flow(943, 943)[0] < 0 < cal.flow(943, 943)[1]
    assert cal.time(1547, 1547)[0] < 80 < cal.time(1547, 1547)[1]


@pytest.mark.parametrize('rgb,name', [((244,167,25),'yellow'), ((212,94,126),'magenta'),
    ((116,88,139),'purple'), ((5,59,87),'blue'), ((0,0,0),None), ((245,245,245),None)])
def test_legend_colours_and_achromatic_rejection(contract, rgb, name):
    assert s.colour(rgb, contract) == name


def test_legend_rejection_not_rescaled_legacy(contract):
    # Native position independently inspected in the actual legend; never inverse
    # reconstructed from the old CSV as a replacement reading.
    assert s.excluded(1272, 104, contract) == 'legend'
    assert s.excluded(45, 450, contract) == 'outside_plot'
    rows = d.smrke2024_s1()['observations']
    assert not any(s.excluded(int(r['x_px']), int(r['y_min_px']), contract) for r in rows)
    excluded = d.smrke2024_s1()['excluded_ink']
    assert any(r['colour'] == 'yellow' and int(r['x_px']) == 1272 for r in excluded)
    # The demonstrated legacy row survives at the pinned original Git identity.
    path = 'puckworks/data/smrke2024/41598_2024_55831_MOESM1_ESM_FigS1.csv'
    raw = subprocess.check_output(['git', 'show', '52df324ee809249eacad1233e407434260e22d46:'+path], cwd=s.ROOT)
    assert hashlib.sha256(raw).hexdigest() == '829253aed8e03b93a2b02187184c448b5a5b570ed60aec82c6912e41718bbf33'
    old = list(csv.DictReader(raw.decode().splitlines()))
    assert len(old) == 18001
    assert any(r['time_s'] == '65.01' and r['flow_rate_g_per_s'] == '3.3948' for r in old)
    assert not (s.ROOT/path).exists()
    contact = [r for r in rows if r['colour'] == 'yellow' and 189 <= int(r['x_px']) <= 191
               and int(r['y_min_px']) <= 80]
    assert contact and all(r['clipping'] == '1' and not r['flow_upper_g_s'] for r in contact)


def test_membership_and_no_recovered_shot_identity():
    info = d.smrke2024_s1()
    assert info['contract']['style_rules']['solid'] == 250
    assert info['contract']['style_rules']['dashed'] == 210
    assert info['contract']['style_rules']['dotted'] == 190
    assert all(r['admissible_settings'] == '190|210|250' and r['admissible_fines_g'] == '0|1|2|4'
               for r in info['observations'])
    assert all(r['membership'] == 'DEFINITE' for r in info['regions']['retained'])
    assert info['reconstruction']['physical_shots_recovered'] == 0


def test_crossing_cannot_fabricate_rank_trajectory():
    rows = [dict(colour='blue', x_px=x, y_min_px=a, y_max_px=b)
            for x, a, b in [(0,0,1),(0,4,5),(1,1,4),(2,0,1),(2,4,5),(3,0,1),(3,4,5)]]
    s.chain_runs(rows)
    assert len({r['fragment_id'] for r in rows[:5]}) == 5
    assert rows[3]['fragment_id'] == rows[5]['fragment_id']
    assert rows[4]['fragment_id'] == rows[6]['fragment_id']


def test_bounded_gaps_and_no_arbitrary_dash_bridge():
    c = {0:(10,12,'INK','a'), 5:(16,18,'INK','b'), 11:(20,21,'INK','c')}
    result = s.bridge_columns(c)
    assert result[2][:2] == (6,22)
    assert all(x not in result for x in range(6,11))
    assert s.bridge_columns(c, max_missing=0) == c


def test_unbounded_gap_splits_identity_and_reviewed_neighbour_is_retired():
    regions = json.loads((s.DATA/'regions.json').read_text())['retained']
    correction = json.loads((s.DATA/'qualification_correction.json').read_text())
    objects, cells = s.split_support(regions, s.load_cells(), correction)
    blue = [o for o in objects if o['colour'] == 'blue']
    assert [o['support_x_px'] for o in blue] == [[F('300.5'),F('401.5')], [F('406.5'),F('478.5')]]
    assert not any(c['object_id'].startswith('B250') and c['x_upper_px'] > F('478.5') for c in cells)
    original = s.load_cells()
    assert next(c for c in original if c['cell_id'] == 'B250-U-X500')['y_lower_px'] == 685


class IdentityCalibration:
    def query(self, a, b):
        return F(a), F(b)

    def flow(self, a, b):
        return F(a), F(b)


def cell(a, b, lo, hi=None, **extra):
    return dict(cell_id=f'{a}:{b}', x_lower_px=F(a), x_upper_px=F(b),
                y_lower_px=F(lo), y_upper_px=F(lo if hi is None else hi), **extra)


def test_time_weights_unequal_density_and_partial_cells():
    cells = [cell(0,1,0), cell(1,3,3)]
    mean = s.window_mean(cells,F(1,4),F(27,10),IdentityCalibration())
    exact = F(102,49)
    assert mean['lower'] <= exact <= mean['upper']
    assert mean['lower'] > F(3,2)  # equal sample averaging would be wrong
    split = [cell(0,F(1,2),0),cell(F(1,2),1,0),cell(1,3,3)]
    same = s.window_mean(split,F(1,4),F(27,10),IdentityCalibration())
    assert (mean['lower'],mean['upper']) == (same['lower'],same['upper'])
    assert sum(w['time_s'][1]-w['time_s'][0] for w in mean['integration_cells']) == F(49,20)


def test_missing_clipped_and_boundary_support_never_renormalized():
    cal = IdentityCalibration()
    assert s.window_mean([cell(0,1,2),cell(2,3,2)],0,3,cal)['status'] == s.UNSUPPORTED
    assert s.window_mean([cell(0,3,2,unbounded=True)],0,3,cal)['status'] == s.UNSUPPORTED
    assert s.window_mean([cell(F(1,100),3,2)],0,3,cal)['status'] == s.UNSUPPORTED
    assert s.window_mean([cell(0,3,2)],0,3,cal)['lower'] == 2


@pytest.mark.parametrize('values,first,second', [((2,2,2),s.OVERLAP,s.OVERLAP),
    ((1,2,3),'RISE','RISE'), ((3,2,1),'DECLINE','DECLINE'), ((3,1,4),'DECLINE','RISE')])
def test_constant_rising_falling_recovery_histories(values,first,second):
    cells = [cell(3*i,3*i+3,q) for i,q in enumerate(values)]
    means = [s.window_mean(cells,3*i,3*i+3,IdentityCalibration()) for i in range(3)]
    bounds = [(m['lower'],m['upper']) for m in means]
    assert s.ordered_change(bounds[0],bounds[1])['status'] == first
    assert s.ordered_change(bounds[1],bounds[2])['status'] == second
    assert s.constant(bounds)['status'] == (s.OVERLAP if values[0] == values[1] == values[2] else 'EXCLUDED')
    if values == (3,1,4):
        assert bounds[1][1] < bounds[0][0] and bounds[1][1] < bounds[2][0]


def test_phase_classification_precedes_direction_and_domain_remainders(contract):
    regions = json.loads((s.DATA/'regions.json').read_text())
    terminal = next(r for r in regions['diagnostics'] if r['id']=='blue_terminal_candidate')
    assert 'tail' in terminal['reason']
    assert all(r['phase'] == 'GRAPHICAL_INTERIOR' for r in regions['retained'])
    assert 'Low or falling' not in contract['phase_rule'] or 'insufficient' in contract['phase_rule']
    assert s.windows()[-1] == (F(84),F(85),False)
    assert s.windows(F(3,2))[0] == (F(0),F(3,2),False)
    assert s.windows(F(3,2))[-1] == (F(165,2),F(85),False)
    for values in ((1,3),(3,1)):
        cells = [cell(0,1,values[0]),cell(1,3,values[1])]
        for phase in ('STARTUP_CANDIDATE','TERMINAL_CANDIDATE','TAIL_CANDIDATE','UNRESOLVED'):
            assert s.qualified_window(cells,0,3,IdentityCalibration(),phase,True)['status'] == s.UNSUPPORTED
        assert s.qualified_window(cells,0,3,IdentityCalibration(),'GRAPHICAL_INTERIOR',True)['lower'] is not None


@pytest.mark.parametrize('pairs,status', [
    ([((1,1),(2,2)),((3,3),(6,6))],s.OVERLAP),
    ([((1,1),(2,2)),((3,3),(7,7))],'EXCLUDED'),
    ([((0,2),(0,3)),((0,2),(1,4))],s.OVERLAP),
    ([((-1,2),(0,3)),((-2,1),(-1,4))],s.OVERLAP),
    ([((0,0),(1,2)),((1,2),(1,2))],'EXCLUDED'),
    ([((1,2),(0,0)),((1,2),(0,0))],'EXCLUDED'),
    ([((-2,-1),(-4,-2)),((-4,-2),(-8,-4))],s.OVERLAP),
    ([((1,2),(-2,-1)),((1,2),(-2,-1))],'EXCLUDED'),
])
def test_multiplier_signed_zero_and_positive_inequalities(pairs,status):
    assert s.multiplier(pairs)['status'] == status


def test_partner_switching_adversary_and_insufficient_windows():
    p1 = [((1,1),(1,1)),((1,1),(2,2))]
    p2 = [((1,1),(2,2)),((1,1),(1,1))]
    assert s.multiplier_alternatives([p1,p2])['status'] == 'EXCLUDED_ALL_RETAINED_PAIRINGS'
    assert s.multiplier_alternatives([p1,[((1,1),(2,2)),((1,1),(2,2))]])['status'] == s.OVERLAP
    assert s.multiplier([p1[0]])['status'] == 'UNINFORMATIVE'
    assert s.multiplier_alternatives([])['status'] == s.UNSUPPORTED


def test_shared_calibration_is_conservatively_enclosed(contract):
    cal = s.Calibration(contract)
    # A broad constant native slab provides an independent analytic mean for
    # every shared-axis corner. Horizontal uncertainty must still fit support.
    slab = [cell(180,250,270,480)]
    r = s.window_mean(slab,6,9,cal)
    for a,b in cal.ya:
        for y in (268,482):
            q = 7*(a-y)/(a-b)
            assert r['lower'] <= q <= r['upper']
    assert s.window_mean([cell(78,1547,500)],0,3,cal)['status'] == s.UNSUPPORTED
    assert s.window_mean([cell(77,1548,500)],0,3,cal)['status'] != s.UNSUPPORTED


def test_outward_rounding_and_strict_decision_before_rounding():
    bounds = (F(-1,3),F(1,3))
    lo,hi = map(F,s.outward(bounds))
    assert lo <= bounds[0] <= bounds[1] <= hi
    epsilon = F(1,10**20)
    assert s.ordered_change((F(1),F(1)),(1+epsilon,1+epsilon))['status'] == 'RISE'
    assert s.constant([(F(1),F(1)),(1+epsilon,1+epsilon)])['status'] == 'EXCLUDED'


def test_active_route_and_figure3_exact_boundary():
    figs = d.smrke2024_figures()
    assert figs['figS1_flow_profiles'] is figs['figS1_source_observations']
    p = s.DATA.parent/'41598_2024_55831_Fig3_HTML.csv'
    assert s.digest(p) == '0bad68815ece1a753dfff89cd134bc2d6b3e32962c1f086c247b6e2f954728e6'
    assert figs['fig3_ey_vs_time'] == list(csv.DictReader(p.open()))
    assert 'run_index' not in figs['figS1_flow_profiles'][0]
    full = d.smrke2024_s1()
    assert full['qualification_correction']['retire_from_temporal_support'][0]['x_lower_px'] == 479
    assert len(full['qualified_fragments']) == 4
    retired = next(c for c in full['reading_cells'] if c['cell_id'] == 'B250-U-X500')
    assert retired['temporal_status'] == 'UNSUPPORTED_IDENTITY_AND_ENCLOSURE'


def test_all_requests_coverage_and_offline_determinism(tmp_path):
    result = s.analyze(output=tmp_path/'one')
    assert result['nominal_conditions'] == 12 and result['nominal_extractions'] == 36
    assert result['recovered_physical_shots'] == 0
    coverage = json.loads((tmp_path/'one/COVERAGE.json').read_text())
    assert {(r['grinder_setting'],r['replacement_fines_g']) for r in coverage} == set(s.product(s.SETTINGS,s.LEVELS))
    comparisons = json.loads((tmp_path/'one/FINES_COMPARISONS.json').read_text())
    assert len({r['pair_id'] for r in comparisons}) == 18
    assert len(comparisons) == 18*58
    assert all(not r['condition_envelope_complete'] for r in comparisons)
    supported = [r for r in comparisons if r['comparisons']]
    assert [(r['pair_id'],r['start_s'],r['end_s']) for r in supported] == [('250:1:2','6','9')]
    assert F(supported[0]['comparisons'][0]['difference'][1]) < 0
    temporal = json.loads((tmp_path/'one/TEMPORAL_COMPARISONS.json').read_text())
    assert all(r['status'] == s.UNSUPPORTED for r in temporal['ordered'])
    s.analyze(output=tmp_path/'two')
    for path in (tmp_path/'one').iterdir():
        assert path.read_bytes() == (tmp_path/'two'/path.name).read_bytes()
        assert path.read_bytes() == (s.OUTPUT/path.name).read_bytes()
