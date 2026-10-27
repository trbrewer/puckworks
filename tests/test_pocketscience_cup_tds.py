"""Synthetic public fixtures; no owner data or source predictions."""
from dataclasses import replace
import numpy as np
import pytest

from puckworks.analysis.pocketscience_cup_tds import (
    Shot, arrays, observe_sheet, cross_predict, metrics, bootstrap_weights,
    evaluate, membership_hash, grade, interval_grades, decide,
)
from puckworks.analysis.pocketscience2024_assay import workbook_graph


def fixture():
    return [Shot('synthetic', 10*g+i, ('synthetic', str(g)), style,
                 .018, .030+.002*g+.001*i, 7+.6*g+.2*i, 7.1+.6*g+.2*i)
            for g, style in enumerate(['traditional', 'turbo']*3) for i in range(3)]


def test_grouped_prediction_and_training_only_leakage():
    x, y, s, g = arrays(fixture())
    p, fits = cross_predict(x, y, s, g)
    assert p.shape == (18, 3) and len(fits) == 6
    for held in np.unique(g):
        changed = y.copy()
        changed[g == held] += 42
        q, _ = cross_predict(x, changed, s, g)
        np.testing.assert_array_equal(p[g == held], q[g == held])


def test_independent_least_squares_and_global_multiplicities():
    x, y, s, g = arrays(fixture())
    rng = np.random.default_rng(71)
    for _ in range(12):
        w = bootstrap_weights(g, rng)
        assert all(w[g == k].sum() == (g == k).sum() for k in np.unique(g))
        p, _ = cross_predict(x, y, s, g, w)
        oracle, _ = cross_predict(x, y, s, g, w, oracle=True)
        np.testing.assert_allclose(p, oracle, atol=1e-10, rtol=0)
        expanded = np.repeat(np.arange(len(y)), w)
        q, _ = cross_predict(x[expanded], y[expanded], s[expanded], g[expanded])
        np.testing.assert_allclose(p[expanded], q, atol=1e-12, rtol=0)
        for arm in ('M', 'C', 'N'):
            assert metrics(y, p, g, w)[arm] == pytest.approx(metrics(y[expanded], q, g[expanded])[arm])


def test_raw_b54_and_sectioning_exclusions_without_section_primitives():
    openpyxl = pytest.importorskip('openpyxl')
    w = openpyxl.Workbook()
    s = w.active
    s.title = 'Sworks High Flow'
    for col, v in dict(A='Shot', B='TDS (filtered) ', C='TDS (unfiltered)', D='Dose',
                       E='Output', F='Grinder', I='Puck Screen', J='Dispersion block').items():
        s[f'{col}52'] = v
    for r in (53, 54, 55):
        for col, v in dict(A=1, B=8.25, C=9.5, D=20, E=40, F='Niche Zero', I='N', J='Teflon').items():
            s[f'{col}{r}'] = v
    s['Y54'] = '=C54*E54/D54'
    s['AV55'] = 'Reject sample: section lost'
    rows, bad = observe_sheet(s)
    assert not bad and len(rows) == 3
    assert rows[1].filtered_tds_pp == 8.25 and rows[1].dose_kg == .020
    assert rows[1].beverage_kg == .040 and rows[2].source_excluded
    assert len({r.identity for r in rows}) == 3  # repeated A is not identity
    assert workbook_graph(s.title, 54)['Y54'][1][0] == 'C54'
    s['B54'] = None
    with pytest.raises(ValueError, match='required primary'):
        observe_sheet(s)
    s['B54'] = 8.25
    s['F54'] = 'unknown grinder'
    with pytest.raises(ValueError, match='unmapped'):
        observe_sheet(s)
    s['F54'] = 'Niche Zero'
    s['B54'].number_format = '0.00%'
    with pytest.raises(ValueError, match='required primary'):
        observe_sheet(s)


@pytest.mark.parametrize('value', [None, np.nan, np.inf, -1, 0, True])
def test_mass_primitives_never_blank_as_zero(value):
    with pytest.raises(ValueError):
        replace(fixture()[0], dose_kg=value)


def test_bounds_rank_identity_and_zero_reference():
    shots = fixture()
    x, y, s, g = arrays(shots)
    p, fits = cross_predict(x*.001, y, s, g)
    assert all(all(f['parameters']['M']['active_bounds']) for f in fits)
    with pytest.raises(ValueError, match='rank'):
        cross_predict(x, y, s, s)
    with pytest.raises(ValueError, match='duplicate'):
        arrays(shots+[shots[0]])
    assert membership_hash(shots) == membership_hash(list(reversed(shots)))
    zero = [replace(z, filtered_tds_pp=0) for z in shots]
    r = evaluate(zero, draws=3)
    assert r['contrasts']['M/C']['gain'] is None
    assert r['contrasts']['M/C']['gain_ci95'] is None
    assert r['contrasts']['M/C']['difference'] == 0


def test_deterministic_bootstrap_and_threshold_decisions():
    a = evaluate(fixture(), draws=11)
    b = evaluate(fixture(), draws=11)
    assert a == b and a['bootstrap']['completed'] == 11
    assert len(a['contrasts']['M/C']['boundary_check']) == 9
    assert grade(0) == 'small' and grade(.10) == 'moderate' and grade(.25) == 'large'
    assert interval_grades([-.1, .25]) == ['worse', 'small', 'moderate', 'large']
    def decision(mc, mn, cn):
        return decide({k: {'gain_ci95': v} for k, v in zip(['M/C', 'M/N', 'C/N'], [mc, mn, cn])})
    assert decision([.01,.2], [.1,.3], [.1,.2])['selected'] == 'M_CONDITIONAL_RESEARCH_REUSE'
    assert decision([-.1,.2], [.1,.3], [.1,.2])['mc_choice_unresolved']
    assert decision([-.1,.2], [.1,.3], [-.1,.2])['selected'] == 'NO_SELECTED_WINNER'
    assert decision([-.1,.2], [-.1,.3], [-.1,.2])['selected'].startswith('N_REFERENCE')
    assert decision([-.2,-.1], [.1,.3], [.1,.2])['m_conditional_disadvantage']
