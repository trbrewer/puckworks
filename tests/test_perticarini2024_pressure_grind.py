"""Scientific risks: joins, exact boxes, dependence, reversal and offline reproduction."""
from collections import Counter
import csv
from decimal import Decimal
from fractions import Fraction as Q
from itertools import combinations, product
import json
import random
import xml.etree.ElementTree as ET

import pytest

from puckworks.analysis import perticarini2024_pressure_grind as m


def bundle():
    observations, _ = m.load_observations()
    return observations, m.compute(observations)


def test_authenticated_support_and_schema():
    obs, result = bundle()
    assert len(obs) == len({o['source_condition_id'] for o in obs}) == 30
    assert Counter(o['dataset_id'] for o in obs) == {'perticarini2024/ey_tds_cibao': 18, 'egidi2024/table2': 12}
    assert Counter((o['coffee_id'], o['temperature_degC']) for o in obs) == {
        ('cibao', '93.4'): 12, ('cibao', '90.4'): 6, ('modoetia', '93.4'): 6, ('modoetia', '90.4'): 6}
    assert all(o['duration_statistic'] == o['duration_replicate_n'] == o['duration_uncertainty'] == 'UNKNOWN' for o in obs)
    assert {o['thesis_table'] for o in obs} == {'4.2', '4.3'}
    assert all(o['egidi_table'] == '2' for o in obs if o['coffee_id'] == 'modoetia')
    assert Counter((r['family'], r['kind']) for r in result['contrasts']) == {
        ('primary', 'duration'): 14, ('primary', 'interaction'): 19,
        ('secondary', 'duration'): 4, ('secondary', 'interaction'): 2}
    assert len({r['contrast_id'] for r in result['contrasts']}) == 39
    assert Counter(r['family'] for r in result['reversals']) == {'primary': 19, 'secondary': 2}


def test_key_joins_are_order_invariant_and_reject_bad_support(tmp_path):
    obs, expected = bundle()
    random.Random(847).shuffle(obs)
    assert m.compute(obs) == expected
    for bad in (obs[:-1], obs + [obs[0]]):
        with pytest.raises(ValueError, match='support'):
            m.compute(bad)
    for _, filename, _ in m.INPUTS:
        path = tmp_path / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((m.ROOT / 'puckworks/data' / filename).read_bytes())
    cibao = tmp_path / m.INPUTS[0][1]
    raw = cibao.read_text()
    for bad, message in [(raw.replace('tau_s', 'time'), 'schema'),
                         (raw + raw.splitlines()[1] + '\n', 'Duplicate'),
                         (raw.replace('93.4', '93.400'), 'identity'),
                         (raw.replace('Cibao Altura', 'Other'), 'coffee')]:
        cibao.write_text(bad)
        with pytest.raises(ValueError, match=message):
            m.load_observations(tmp_path)
    cibao.write_text(raw)
    assert m.load_observations(tmp_path)[0] == m.load_observations()[0]


def test_independent_decimal_reduction_from_canonical_rows():
    # Different parser/reduction: no producer observation lookup or contrast coefficients.
    direct = {}
    for filename, coffee, keys in [
        ('perticarini2024/ey_tds_cibao.csv', 'cibao', ('T_degC', 'p_bar', 'granulometry', 'tau_s')),
        ('egidi2024/table2_egidi2024_tds_ey.csv', 'modoetia', ('T [degC]', 'p [bar]', 'Granulometry', 'tau [s]'))]:
        with (m.ROOT / 'puckworks/data' / filename).open() as stream:
            for row in csv.DictReader(stream):
                t, p, g, tau = [row[k] for k in keys]
                direct[(coffee, t, g.lower(), p)] = Decimal(tau)
    _, result = bundle()
    for r in result['contrasts']:
        def d(grind):
            return direct[(r['coffee_id'], r['temperature_degC'], grind, r['pressure_to_bar'])] - direct[(r['coffee_id'], r['temperature_degC'], grind, r['pressure_from_bar'])]
        expected = d(r['grind_a']) - (d(r['grind_b']) if r['grind_b'] else 0)
        assert Q(expected) == Q(r['nominal_s'])
    expected_primary = {('cibao', '93.4'): [1, 0, -6, -5, -6],
                        ('cibao', '90.4'): [-2, -6, -5],
                        ('modoetia', '93.4'): [0, 0, -4],
                        ('modoetia', '90.4'): [1, 1, -3]}
    for stratum, expected in expected_primary.items():
        assert [Q(r['nominal_s']) for r in result['contrasts'] if r['family'] == 'primary'
                and r['kind'] == 'duration' and (r['coffee_id'], r['temperature_degC']) == stratum] == expected
    adverse = [r for r in result['contrasts'] if r['family'] == 'primary' and r['kind'] == 'interaction' and Q(r['nominal_s']) < 0]
    assert {(r['coffee_id'], r['temperature_degC'], r['grind_a'], r['grind_b'], r['nominal_s']) for r in adverse} == {
        ('cibao', '93.4', 'optimal', 'coarse', '-1'), ('cibao', '90.4', 'optimal', 'coarse', '-1')}


def test_complete_pair_support_and_original_coefficient_lineage():
    obs, result = bundle()
    lookup = {o['source_condition_id']: o for o in obs}
    for r in result['contrasts']:
        assert sum(r['terms'].values()) == 0
        assert r['coefficient_l1'] == (2 if r['kind'] == 'duration' else 4)
        for oid, coefficient in r['terms'].items():
            o = lookup[oid]
            assert (o['coffee_id'], o['temperature_degC']) == (r['coffee_id'], r['temperature_degC'])
            expected = 1 if o['nominal_pressure_bar'] == r['pressure_to_bar'] else -1
            if o['grind_id'] == r['grind_b']:
                expected *= -1
            assert coefficient == expected
        if r['kind'] == 'interaction':
            assert m.GRINDS.index(r['grind_a']) < m.GRINDS.index(r['grind_b'])
    for coffee, temp in m.STRATA:
        grinds = m.GRINDS if (coffee, temp) == ('cibao', '93.4') else m.GRINDS[1:4]
        actual = {(r['grind_a'], r['grind_b']) for r in result['contrasts'] if r['kind'] == 'interaction'
                  and r['family'] == 'primary' and (r['coffee_id'], r['temperature_degC']) == (coffee, temp)}
        assert actual == set(combinations(grinds, 2))


def test_nominal_and_conditional_counts():
    _, result = bundle()
    for kind, nominal, conditional in [
        ('duration', {'positive': 3, 'negative': 8, 'reported_zero': 3}, {'negative': 8, 'unresolved': 6}),
        ('interaction', {'positive': 14, 'negative': 2, 'reported_zero': 3}, {'positive': 12, 'unresolved': 7})]:
        rows = [r for r in result['contrasts'] if r['family'] == 'primary' and r['kind'] == kind]
        assert Counter(r['nominal_status'] for r in rows) == nominal
        assert Counter(r['box_status'] for r in rows) == conditional
    secondary = [r for r in result['contrasts'] if r['family'] == 'secondary']
    assert [Q(r['nominal_s']) for r in secondary] == [7, -1, 8, 8, -7, 15]
    assert [(r['lower_s'], r['upper_s']) for r in secondary[-3:]] == [('7', '9'), ('-8', '-6'), ('13', '17')]


def test_box_extrema_against_all_original_cell_vertices():
    obs, result = bundle()
    values = {o['source_condition_id']: Q(o['tau_s']) for o in obs}
    for r in result['contrasts']:
        terms = r['terms']
        for h in [Q(0), Q(1, 2), Q(7, 3)]:
            vertex_values = [sum(a * (values[oid] + sign * h) for (oid, a), sign in zip(terms.items(), signs))
                             for signs in product([-1, 1], repeat=len(terms))]
            enclosure = m.enclosure(terms, values, h)
            assert (min(vertex_values), max(vertex_values)) == (Q(enclosure['lower_s']), Q(enclosure['upper_s']))


def test_strict_zero_touch_and_critical_boundaries():
    obs, result = bundle()
    values = {o['source_condition_id']: Q(o['tau_s']) for o in obs}
    for r in result['contrasts']:
        critical = Q(r['critical_h_s'])
        assert m.enclosure(r['terms'], values, critical)['box_status'] == 'unresolved'
        assert m.enclosure(r['terms'], values, critical + Q(1, 1000))['box_status'] == 'unresolved'
        if critical:
            assert m.enclosure(r['terms'], values, critical - Q(1, 1000))['box_status'] == r['nominal_status']
        else:
            assert r['nominal_status'] == 'reported_zero'
            assert m.enclosure(r['terms'], values, 0)['box_status'] == 'unresolved'
    with pytest.raises(ValueError):
        m.enclosure({}, {}, -1)


def test_shared_cell_cancellation_and_structural_identity():
    obs, result = bundle()
    values = {o['source_condition_id']: Q(o['tau_s']) for o in obs}
    for identity in result['arithmetic_identities']:
        assert identity['terms'] == {}
        assert identity['coefficient_l1'] == 0
        assert identity['critical_h_s'] is None
        assert identity['nominal_status'] == identity['box_status'] == 'structural_zero'
        assert identity['nominal_s'] == identity['lower_s'] == identity['upper_s'] == '0'
        assert m.enclosure(identity['terms'], values, 10**6)['upper_s'] == '0'
    # Naive interval addition would give radius 4h; the shared 9-bar cell cancels to 2h.
    terms = m.combine((1, {'p9': 1, 'p6': -1}), (1, {'p12': 1, 'p9': -1}))
    assert terms == {'p12': 1, 'p6': -1}
    assert m.enclosure(terms, {'p6': '73', 'p9': '74', 'p12': '81'}, Q(1, 2))['lower_s'] == '7'
    assert m.enclosure({'irrelevant': 0}, {}, 999)['critical_h_s'] is None


def test_reversal_is_separate_and_has_exact_boundaries():
    obs, result = bundle()
    values = {o['source_condition_id']: Q(o['tau_s']) for o in obs}
    contrasts = {r['contrast_id']: r for r in result['contrasts']}
    primary = [r for r in result['reversals'] if r['family'] == 'primary']
    assert sum(r['nominal_opposite_signs'] for r in primary) == 5
    assert not any(r['opposite_signs_at_h'] for r in primary)
    assert {r['reversal_critical_h_s'] for r in primary if r['nominal_opposite_signs']} == {'1/2'}
    assert [r['reversal_critical_h_s'] for r in result['reversals'] if r['family'] == 'secondary'] == ['1/2', '7/2']
    for r in result['reversals']:
        a, b = [contrasts[r[key]] for key in ('component_a_id', 'component_b_id')]
        assert Q(contrasts[r['interaction_id']]['nominal_s']) == Q(a['nominal_s']) - Q(b['nominal_s'])
        if r['nominal_opposite_signs']:
            h = Q(r['reversal_critical_h_s'])
            for at, expected in [(0, 'strict_opposite'), (h - Q(1, 1000), 'strict_opposite'),
                                 (h, 'unresolved'), (h + Q(1, 1000), 'unresolved')]:
                statuses = [m.enclosure(x['terms'], values, at)['box_status'] for x in (a, b)]
                assert m.reversal_status(*statuses) == expected
        else:
            assert r['reversal_critical_h_s'] is None
            assert r['nominal_status'] == 'nominal_opposite_not_established'
    assert any(contrasts[r['interaction_id']]['box_status'] == 'positive' and not r['opposite_signs_at_h'] for r in primary)


def test_breakpoints_cover_exact_sign_changes():
    obs, result = bundle()
    values = {o['source_condition_id']: Q(o['tau_s']) for o in obs}
    for r in result['breakpoints']:
        lo = Q(r['h_from_inclusive_s'])
        hi = Q(r['h_to_exclusive_s']) if r['h_to_exclusive_s'] else lo + 100
        rows = [c for c in result['contrasts'] if (c['family'], c['kind']) == (r['family'], r['kind'])]
        for h in (lo, (lo + hi) / 2):
            counts = Counter(m.enclosure(c['terms'], values, h)['box_status'] for c in rows)
            assert all(counts[k] == r[k] for k in ('positive', 'negative', 'unresolved'))


def test_offline_reproduction_lf_and_figure_data(tmp_path):
    b = m.write(tmp_path)
    for name in ('observations.csv', 'contrasts.csv', 'contrasts.json', 'reversals.csv',
                 'reversals.json', 'CONTRASTS.md', 'COMPARISON.svg'):
        assert (tmp_path / name).read_bytes() == (m.OUTPUT / name).read_bytes()
        assert b'\r' not in (tmp_path / name).read_bytes()
    svg = ET.fromstring((tmp_path / 'COMPARISON.svg').read_text())
    glyphs = {g.attrib['data-contrast-id']: g.attrib for g in svg.iter() if 'data-contrast-id' in g.attrib}
    assert len(glyphs) == 39
    for r in b['contrasts']:
        assert [glyphs[r['contrast_id']][f'data-{k}-s'] for k in ('nominal', 'lower', 'upper')] == [r[f'{k}_s'] for k in ('nominal', 'lower', 'upper')]
    assert json.loads((tmp_path / 'reversals.json').read_text())['reversals'] == b['reversals']
    assert {i['file_sha256'] for i in b['inputs']} == {'2c5fae8319d41c690b7e23ea00ddfc722e08c01ebcd8f012dafb1820a8fc6703', '1b5cd8891472d2d432fcb96a59e167d8fcca8b8e70a0a75187d810bf8a8e4419'}


def test_discovery_preserves_chemistry_without_pressure_or_calibration_edges():
    from puckworks.insights import extract

    datasets, _ = extract.extract_manifest()
    models, _ = extract.extract_registry()
    relations, _ = extract.dataset_relations(datasets, models)
    for dataset, _, _ in m.INPUTS:
        source = f'dataset:{dataset}'
        assert any(r.type == 'DERIVED_FROM' and r.source == source for r in relations)
        assert any(r.type == 'MEASURES' and r.source == source and r.target == 'observable:tds' for r in relations)
        assert not any(r.type == 'MEASURES' and r.source == source and r.target == 'observable:pressure' for r in relations)
        assert not any(r.type == 'CALIBRATED_FROM' and r.target == source for r in relations)
