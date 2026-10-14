"""Rights-independent arithmetic, membership and preservation tests."""
import copy
import importlib
import math
import random

import pytest

from puckworks.analysis import mass_uncertainty_audit as a


def unit(r, b=None):
    b = r if b is None else b
    return dict(R_pp=r, B_pp=b, absB_pp=abs(b))


def test_units_unequal_mass_and_independent_arithmetic():
    m = a.metric([1., 3.], [.02, .04], [3., 2.])
    assert m == a.metric([1., 3.], [2., 4.], [3., 2.], observed_unit='percent')
    assert m['R_pp'] == math.sqrt(13/4)
    assert m['B_pp'] == -1.25
    assert m['absB_pp'] == 1.25
    with pytest.raises(ValueError, match='UNITS'):
        a.metric([1], [2], [3])
    for masses in ([], [0.], [-1.], [float('nan')]):
        with pytest.raises(ValueError):
            a.metric(masses, [0.], [0.])


def test_shot_first_condition_first_and_bias_cancellation():
    units = {1: unit(1, 1), 2: unit(1, -1), 3: unit(4, 4)}
    m = a.balanced(units, {1: 'a', 2: 'a', 3: 'b'})
    assert m == dict(R_pp=2.5, B_pp=2., absB_pp=2.5)
    assert m['R_pp'] != a.balanced(units)['R_pp']
    assert a.balanced({1: unit(1, 1), 2: unit(1, -1)})['absB_pp'] == 1
    assert m['R_pp'] != math.sqrt((1+1+16)/3)


@pytest.mark.parametrize('rows', [[{'shot': 1, 'window': 1}]*2, [], [{'shot': 2, 'window': 1}]])
def test_reject_duplicate_missing_and_extra_rows(rows):
    with pytest.raises(ValueError):
        a.index(rows, ('shot', 'window'), {(1, 1)})


def test_aliases_do_not_merge_distinct_physical_shots():
    row = {'dataset': 'pannusch', 'campaign': 'p', 'shot': 1, 'window': 3, 'value': 2.}
    rows = [row, dict(row, dataset='schmieder'), dict(row, shot=2)]
    assert len(a.deduplicate_aliases(rows, {'schmieder': 'pannusch'})) == 2
    with pytest.raises(ValueError, match='CONFLICTING_ALIAS'):
        a.deduplicate_aliases([row, dict(row, dataset='schmieder', value=3)], {'schmieder': 'pannusch'})


def test_joint_role_deletion_and_all_arm_pairing():
    pairs = {(j, i): unit(j+i) for j in range(11) for i in range(11) if j != i}
    arms = {name: copy.deepcopy(pairs) for name in ('F2', 'A2', 'A0', 'M')}
    public, private = a.leave_one_out(arms, 'A2', pairs=True)
    assert public['remaining_units'] == [90]
    assert public['remaining_physical_shots'] == [10]
    assert len(private) == 11
    assert all(v['remaining_units'] == 90 for v in private)
    # Removing identity 10 from both roles leaves indices 0..9 and mean 9.
    assert private[-1]['metrics']['A2']['R_pp'] == 9
    bad = copy.deepcopy(arms); del bad['F2'][0, 1]
    with pytest.raises(ValueError, match='IDENTICAL_PAIRING'):
        a.leave_one_out(bad, 'A2', pairs=True)
    bad = {name: {**pairs, (0, 0): unit(0)} for name in arms}
    with pytest.raises(ValueError, match='OFF_DIAGONAL'):
        a.leave_one_out(bad, 'A2', pairs=True)


def test_small_degenerate_unavailable_and_nearzero():
    assert a.spread([])['sd'] is None
    assert a.spread([2])['sd'] is None
    assert a.spread([2, 2])['sd'] == 0
    assert a.gain(unit(0), unit(1e-13))['relative_gain'] is None
    assert a.balanced({1: None, 2: unit(2)}) is None
    assert a.uncertainty_components()['early_input_propagation'] is None
    public, _ = a.leave_one_out({'C2': {1: unit(1)}, 'C0': {1: unit(2)}}, 'C2', {1: 'only'})
    assert public['metrics']['C2']['available'] == 0


def test_order_invariance_with_fixed_shuffle_seed():
    units = {i: unit(i/7) for i in range(12)}
    expected = a.leave_one_out({'C2': units, 'C0': units}, 'C2')
    keys = list(units); random.Random(314159).shuffle(keys)
    shuffled = {k: units[k] for k in keys}
    assert a.leave_one_out({'C2': shuffled, 'C0': shuffled}, 'C2') == expected


def test_hash_mismatch_readback_and_source_overwrite(tmp_path):
    source = tmp_path/'source'; source.mkdir()
    p = source/'predictions.json'; p.write_text('{}')
    t = a.Inputs(); t.json(p, a.sha(b'{}'))
    p.write_text('{"changed":true}')
    with pytest.raises(a.IntegrityStop, match='HASH_MISMATCH'):
        t.recheck()
    with pytest.raises(a.IntegrityStop, match='READBACK'):
        t.json(p)
    with pytest.raises(ValueError, match='OVERWRITE'):
        a.private_output(source/'new', [source])
    with pytest.raises(FileExistsError):
        a.private_output(source)


def test_reconcile_identity_not_scientific_tolerance():
    a.reconcile({'v': 1.+math.ulp(1)}, {'v': 1.})
    with pytest.raises(a.IntegrityStop):
        a.reconcile({'v': 1.000001}, {'v': 1.})
    with pytest.raises(a.IntegrityStop):
        a.reconcile({'n': 10.}, {'n': 10})
    with pytest.raises(a.IntegrityStop):
        a.reconcile({'v': None}, {'v': 0.})


def test_retained_report_checks_completion_without_inputs(tmp_path):
    result = {'task': a.TASK, 'completeness': 'COMPLETE', 'tasks': {}}
    a.write(tmp_path/'RESULTS.json', result)
    a.write(tmp_path/'completion.json', {'status': 'COMPLETE', 'results_sha256': a.sha((tmp_path/'RESULTS.json').read_bytes())})
    assert a.retained_report(tmp_path) == result
    (tmp_path/'RESULTS.json').write_text('{}')
    with pytest.raises(a.IntegrityStop):
        a.retained_report(tmp_path)


@pytest.fixture
def prohibit_campaigns(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('PROHIBITED_CAMPAIGN_OR_FITTING_CALL')
    for modname in ('conditional_tail_scoring', 'grudeva_pooled_tail_scoring', 'grudeva_one_shot_scoring',
                    'pannusch_conditional_tail_delivery', 'grudeva_pooled_tail_delivery',
                    'grudeva_one_shot_calibration', 'conditional_tail_training', 'grudeva_clock'):
        module = importlib.import_module('puckworks.analysis.'+modname)
        for name in ('score', 'evaluate', 'fit', 'fit_predict', 'predict', 'prepare', 'develop', 'final_fit', 'calibrate', 'least_squares', 'minimize'):
            if hasattr(module, name):
                monkeypatch.setattr(module, name, forbidden)
    import scipy.optimize
    monkeypatch.setattr(scipy.optimize, 'least_squares', forbidden)


def grudeva_fixture(pairs=False):
    queries = [{'shot': i, 'vial': v, 'mass_kg': .01, 'start_kg': (v-1)*.01, 'end_kg': v*.01} for i in range(1, 4) for v in (15, 16)]
    outcomes = [{'shot': q['shot'], 'vial': q['vial'], 'q': .02, 'solute_kg': .0002, 'chemistry_status': 'AVAILABLE'} for q in queries]
    arms = ('F2', 'A2', 'A0', 'M') if pairs else ('C0', 'C1', 'C2')
    predictions = {}
    for arm in arms:
        rows = []
        for j in (range(1, 4) if pairs else [None]):
            for q in queries:
                if j == q['shot']:
                    continue
                row = dict(q, status='QUALIFIED', feature_extrapolation=[], prediction={
                    'tds_percent': 2.2, 'solute_kg': .00022, 'allowance_kg': 1e-14, 'numerical_qualified': True})
                if pairs:
                    row.update(calibrator=j, calibration_mass_extrapolation=False)
                rows.append(row)
        predictions[arm] = rows
    return {'queries.json': queries, 'outcomes.json' if pairs else 'observed_suffix.json': outcomes,
            'predictions.json': predictions,
            'cohort.json': [{'shot': i, 'eligible': i <= 3, 'k2': 14} for i in range(1, 14)],
            'folds.json': {'calibrators': [1, 2, 3], 'targets': [1, 2, 3],
                           'pairs': [[j, i] for j in range(1, 4) for i in range(1, 4) if i != j],
                           'intended_slots_per_arm': 12, 'unique_suffix_windows': 6}}


@pytest.mark.parametrize('pairs', [False, True])
def test_reduction_calls_no_campaigns_and_rejects_incomplete_support(prohibit_campaigns, pairs):
    data = grudeva_fixture(pairs)
    shots, details, units = a.grudeva_units(data, pairs=pairs)
    assert shots == [1, 2, 3]
    assert all(m['R_pp'] == pytest.approx(.2) for arm in units.values() for m in arm.values())
    data['predictions.json'][next(iter(data['predictions.json']))].pop()
    with pytest.raises(ValueError, match='MISSING_OR_UNEXPECTED'):
        a.grudeva_units(data, pairs=pairs)


def test_primary_stress_and_exact_legacy_support(prohibit_campaigns):
    from puckworks.analysis import conditional_tail_scoring as s
    obs = []; predictions = []
    for c in ('primary', 'stress'):
        for shot in range(3):
            for f in (3, 5, 7, 10):
                obs.append(dict(condition=c, shot=f'{c}{shot}', fraction=f, eligible=True, q=.02, mass_kg=.01, solute_kg=.0002))
                predictions.append(dict(shot=f'{c}{shot}', fraction=f, supported=True,
                    legacy_supported=(c == 'primary'), numerical_qualified=True,
                    predicted_tds_percent=2.2 if c == 'primary' else 10., predicted_solute_kg=.00022,
                    numerical_allowance_kg=1e-14))
    primary, _ = s.panel_metrics(obs, predictions, ['primary'])
    stress, _ = s.panel_metrics(obs, predictions, ['stress'])
    common, _ = s.panel_metrics(obs, predictions, ['stress'], common_legacy=True)
    assert primary['full_scope_metrics']['R_pp'] == pytest.approx(.2)
    assert stress['full_scope_metrics']['R_pp'] == pytest.approx(8)
    assert common['full_scope_metrics'] is None
    assert common['complete_scope'] is False


def test_deleted_incomplete_shot_does_not_restore_original_full_scope():
    arms = {'C2': {1: unit(1), 2: unit(2), 3: None}, 'C0': {1: unit(2), 2: unit(3), 3: None}}
    assert a.balanced(arms['C2']) is None
    result, details = a.leave_one_out(arms, 'C2')
    assert result['metrics']['C2']['available'] == 0
    assert details[2]['metrics']['C2'] is None
    assert a.balanced(arms['C2']) is None
