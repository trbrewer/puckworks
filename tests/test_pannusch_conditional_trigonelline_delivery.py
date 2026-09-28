"""Synthetic verification only; no experimental rows enter these tests."""
import copy

import pytest

from puckworks.analysis import pannusch_conditional_trigonelline_delivery as p


def synthetic_row(campaign='FIT_2021_12'):
    label = 'FIT' if campaign == 'FIT_2021_12' else 'PRED'
    coordinate = dict(campaign=campaign, condition=label+'-C01', shot=label+'-E01-R1',
                      fraction=3, b0=.01, b1=.015, mass_kg=.005, coordinate_status='QUALIFIED')
    row = dict(campaign_id=campaign, shot_id=coordinate['shot'], fraction_id='3',
               analyte='trigonelline', concentration_unit='mg/g', validity='VALID',
               source_id='SYNTHETIC', concentration_value='0.5', measured_concentration='0.5')
    return coordinate, row


def test_trigonelline_source_identity_and_units():
    c, r = synthetic_row()
    value, = p.target_slots([c], [r], campaign=c['campaign'], include_values=True)
    assert value['q'] == .0005
    assert value['analyte'] == 'trigonelline'
    assert value['source_field'] == 'ExperimentalData(1).run(1).cAlcaloids(3,2)'
    assert value['shot'] == c['shot'] and value['fraction'] == 3
    bad = dict(r, concentration_unit='mg/L')
    with pytest.raises(ValueError, match='UNIT'):
        p.target_slots([c], [bad], campaign=c['campaign'], include_values=True)
    caffeine = dict(r, analyte='caffeine')
    absent, = p.target_slots([c], [caffeine], campaign=c['campaign'])
    assert not absent['analyte_eligible']


def test_projection_preserves_trigonelline_exclusions_without_filling():
    c, r = synthetic_row()
    bad = dict(r, validity='INVALID', exclusion_reason='SYNTHETIC_SPILL')
    projected, = p.target_slots([c], [bad], campaign=c['campaign'], include_values=True)
    assert projected['q'] is None and projected['source_reason'] == 'SYNTHETIC_SPILL'
    with pytest.raises(ValueError, match='DUPLICATE'):
        p.target_slots([c], [r, r], campaign=c['campaign'])
    with pytest.raises(ValueError):
        p.target_slots([c], [dict(r, concentration_value='nan')], campaign=c['campaign'])


def test_pred_projection_is_coordinate_and_validity_only():
    c, r = synthetic_row('PREDICTION_2022_03')
    before = copy.deepcopy(r)
    projected, = p.target_slots([c], [r], campaign=c['campaign'])
    assert 'q' not in projected and 'measured_concentration' not in projected
    assert r == before
    with pytest.raises(ValueError, match='SINGLE_APPROVED'):
        p.target_slots([c], [r], campaign=c['campaign'], include_values=True)


def test_early_projection_reads_only_original_vial_mass():
    c, _ = synthetic_row()
    first = dict(c, fraction=1, b0=0., b1=.004, mass_kg=.004, TDS='forbidden')
    second = dict(c, fraction=2, b0=.004, b1=.01, mass_kg=.006, trigonelline='forbidden')
    assert p.mass_projection([first, second]) == {c['shot']: [.004, .006]}
    with pytest.raises(ValueError, match='QUALIFIED'):
        p.mass_projection([first, dict(second, coordinate_status='UNAVAILABLE')])


def test_inherited_anchor_rule_remains_explicit_and_bounded():
    import numpy as np
    state = type('SyntheticAnchor', (), {'b_anchor': .01})()
    a = np.nextafter(.01, 0.)
    start, allowance = p.source_geometry.source_query_start({'fraction': 3, 'b0': a}, state)
    assert start == .01 and allowance == 2*abs(.01-a)
    with pytest.raises(ValueError, match='ANCHOR_MISMATCH'):
        p.source_geometry.source_query_start({'fraction': 3, 'b0': .009}, state)
    assert p.source_geometry.source_query_start({'fraction': 5, 'b0': a}, state) == (a, 0.)
