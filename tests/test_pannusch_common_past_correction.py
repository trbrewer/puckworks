"""Small independent checks for 007's additive witness and retention correction."""
from dataclasses import replace
import json
import pickle
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest

from puckworks.models.pannusch2024 import common_past_contrast as cc, prefix_conditioned as pc, state_envelope as se
from tools import pannusch_common_past_contrast_verification as runner
from tools import pannusch_common_past_correction as evidence
from test_pannusch_common_past_contrast import inputs
from test_pannusch_state_envelope import state


def test_legacy_reconstructed_state_is_used_without_roundtrip_or_lp():
    conditioned, a, b = inputs(observations=False)
    u = conditioned.original
    r, _, _ = cc._validate(conditioned, a, b, 7.1, 1e-9, 1e-6, 'EXPLICIT_UNEQUAL_VOLUME')
    target = cc.FVSignedContrast(a, b, r)
    actual = u.upper_masses_kg
    raw = np.nextafter(actual, np.inf)
    legacy = SimpleNamespace(state=u.upper, optimizer_masses_kg=raw, status='FEASIBLE', repair='SAVED_REPAIR')
    poly = pc._base_polytope(u)
    e = pc._LPEvidence(poly, -target.weights, raw_masses_kg=raw)
    with patch.object(pc, '_candidate', side_effect=AssertionError('no roundtrip')), patch.object(pc, '_solve', side_effect=AssertionError('no LP')):
        w = cc._candidate(u, poly, e, target, legacy=legacy)
    assert not w.raw_residuals.feasible and w.final_residuals.feasible
    assert w.state is legacy.state and w.legacy_witness is legacy
    assert np.array_equal(w.raw_optimizer_masses_kg, raw)
    assert np.array_equal(w.masses_kg, actual)
    assert w.status == 'CHECKED_REPLAY_REQUIRED' and w.replay is None


def test_legacy_feasible_label_does_not_bypass_stricter_rows():
    conditioned, a, b = inputs(observations=False)
    u = conditioned.original
    r, _, _ = cc._validate(conditioned, a, b, 7.1, 1e-9, 1e-6, 'EXPLICIT_UNEQUAL_VOLUME')
    target = cc.FVSignedContrast(a, b, r)
    poly = pc._base_polytope(u)
    # A new exact row excludes the legacy state, regardless of its FEASIBLE label.
    poly = replace(poly, A=np.vstack((poly.A, np.ones(len(poly.lower)))),
                   b=np.r_[poly.b, 0.], row_labels=(*poly.row_labels, 'actual-inner:upper'))
    raw = u.upper_masses_kg
    legacy = SimpleNamespace(state=u.upper, optimizer_masses_kg=raw, status='FEASIBLE')
    e = pc._LPEvidence(poly, -target.weights, raw_masses_kg=raw)
    w = cc._candidate(u, poly, e, target, legacy=legacy)
    assert w.status == 'UNRESOLVED'
    assert w.previous_attempt.termination == 'EXISTING_STATE_FAILS_007_JOINT_CHECK'
    assert w.previous_attempt.legacy_witness is legacy


def local_fixture(sign=1):
    lo, hi = state(n=1, concentrations=np.zeros((3, 1))), state(n=1, concentrations=np.full((3, 1), 8.))
    u = se.FVChemicalStateSet(lo, hi, (0., hi.inventory_kg*2), 'SYNTHETIC_CORRECTION_TEST')
    target = SimpleNamespace(weights=sign*np.array([.5, -.25, .125]), coefficient_allowances=np.zeros(3),
                             settings=se.FVEnvelopeSettings())
    return u, target


@pytest.mark.parametrize('sign', [-1, 1])
@pytest.mark.parametrize('side', ['lower', 'upper'])
def test_local_all_row_proposal_inventory_box_and_simultaneous_observations(sign, side):
    u, target = local_fixture(sign)
    m = se._concentrations(state(n=1, concentrations=np.full((3, 1), 4.)))*u.capacities_m3
    # Independent cell observations plus an inventory row, all exactly active at
    # the supplied reference, with the other side left open.
    A = np.vstack((np.eye(3), np.ones(3), np.array([1., 1., 0.])))
    b = np.r_[m, sum(m), sum(m[:2])]
    if side == 'lower':
        A, b = -A, -b
    poly = pc._Polytope(u.lower_masses_kg, u.upper_masses_kg, A, b, u.inventory_scale_kg,
                       ('obs0', 'obs1', 'obs2', 'inventory', 'overlap'))
    raw = np.nextafter(m, -np.inf if side == 'lower' else np.inf)
    e = pc._LPEvidence(poly, target.weights, raw_masses_kg=raw)
    w = cc._joint_proposal(u, poly, e, target, previous=None)
    assert w.status == 'CHECKED_REPLAY_REQUIRED', w.termination
    assert pc._residuals(poly, w.masses_kg).feasible
    assert se._residuals(u, w.masses_kg).feasible
    assert np.array_equal(w.raw_optimizer_masses_kg, raw)
    assert w.mass_change_kg <= 64*target.settings.primal_tolerance*u.inventory_scale_kg
    assert w.prediction_interval_kg == pc._prediction(target, w.masses_kg)


def test_local_search_does_not_require_strict_interior_or_tighten_equalities():
    u, target = local_fixture()
    mass = u.lower_masses_kg
    # Dependent non-opposite rows imply x0=x1=0. This has no strictly feasible
    # interior, and the optional slack must be allowed to become zero.
    A = np.array([[1., 1., 0.], [-1., 0., 0.], [0., -1., 0.]])
    poly = pc._Polytope(mass, u.upper_masses_kg, A, np.zeros(3), u.inventory_scale_kg, ('sum', 'x0', 'x1'))
    raw = np.zeros(3)
    e = pc._LPEvidence(poly, target.weights, raw_masses_kg=raw)
    w = cc._joint_proposal(u, poly, e, target, previous=None)
    assert w.status == 'CHECKED_REPLAY_REQUIRED'
    assert w.repair_optimization.raw_masses_kg[-1] == 0.
    # Explicit dependent equality rows are retained unchanged as well.
    eq = replace(poly, A=np.array([[1., 0., 0.], [-1., 0., 0.], [2., 0., 0.]]))
    w = cc._joint_proposal(u, eq, replace(e, problem=eq), target, previous=None)
    assert w.status == 'CHECKED_REPLAY_REQUIRED'


def test_local_proposal_cap_and_optimizer_failure_preserve_failure():
    u, target = local_fixture()
    poly = pc._base_polytope(u)
    e = pc._LPEvidence(poly, target.weights, raw_masses_kg=u.upper_masses_kg*2)
    w = cc._joint_proposal(u, poly, e, target, previous='retained failure')
    assert w.termination == 'REPAIR_MASS_CHANGE_LIMIT' and w.status == 'UNRESOLVED'
    e = replace(e, raw_masses_kg=u.upper_masses_kg)
    with patch.object(pc, 'linprog', return_value=SimpleNamespace(success=False, status=2, nit=0)):
        w = cc._joint_proposal(u, poly, e, target, previous='retained failure')
    assert w.status == 'UNRESOLVED' and w.repair_optimization.solver_status == 2
    assert w.previous_attempt == 'retained failure'


def test_complete_forward_archive_before_and_after_transport_and_no_budget_reset(tmp_path):
    with patch.object(runner.subprocess, 'check_output', return_value=str(tmp_path)):
        b = runner.Budget(tmp_path/'evidence')
        b.run('original', 'forward', 1, lambda: None)
        b.lock.close()
        old = (tmp_path/'evidence/resources.json').read_bytes()
        b = runner.Budget(tmp_path/'evidence', correction='007-prefix-diagnostic-v1', dependencies={'verified': 'a'*64})
        value = {'complete': np.array([1., np.nan]), 'failed': True}
        returned = b.run('diagnostic', 'forward', 1, lambda: value, forward_inputs={'state': 'test'})
        assert returned['failed']
        row = b.data['executions'][-1]
        archive = b.evidence/row['archive']
        for label in ('inputs', 'before-transport', 'after-transport', 'after-freeze'):
            assert evidence.sha(archive/(label+'.pickle')) == row['archive_index'][label+'.pickle']['sha256']
        restored = pickle.loads((archive/'before-transport.pickle').read_bytes())
        assert np.isnan(restored['complete'][1])
        assert (tmp_path/'evidence/resources.json').read_bytes() == old
        assert sum(r['charged_propagations'] for r in b.data['executions']) == 2
        b.lock.close()
        with pytest.raises(ValueError, match='ALREADY_ATTEMPTED'):
            runner.Budget(tmp_path/'evidence', correction='007-prefix-diagnostic-v1', dependencies={'verified': 'a'*64})
    assert json.loads((archive/'index.json').read_text()) == row['archive_index']


def test_resource_accounting_includes_failed_prior_repair_lp():
    u, target = local_fixture()
    poly = pc._base_polytope(u)
    lp = pc._LPEvidence(poly, target.weights, calls=1)
    first = pc.FVConditionedWitness(u.lower_masses_kg, None, repair_optimization=lp)
    second = cc.FVContrastWitness(u.lower_masses_kg, None, repair_optimization=lp, previous_attempt=first)
    assert cc._repair_calls(second) == 2
    assert cc._repair_calls(None) == 0


def test_checked_archive_transport_rejects_bit_corruption_and_bad_content(tmp_path):
    value = {'masses': np.array([[1., 2.], [3., 4.]])}
    packet = runner._archive_value(tmp_path, 'before-transport', value)
    restored = runner._load_checked_forward(tmp_path, packet)
    np.testing.assert_array_equal(restored['masses'], value['masses'])
    wrong = dict(packet, content_identity='0'*64)
    with pytest.raises(RuntimeError, match='DESERIALIZED_CONTENT_MISMATCH'):
        runner._load_checked_forward(tmp_path, wrong)
    path = tmp_path/'before-transport.pickle'
    original = path.read_bytes()
    damaged = bytearray(original); damaged[-10] ^= 1
    path.write_bytes(damaged)
    with pytest.raises(RuntimeError, match='TRANSPORT_CHECKSUM_MISMATCH'):
        runner._load_checked_forward(tmp_path, packet)


def test_archival_failure_before_launch_is_charged_and_finalized(tmp_path):
    with patch.object(runner.subprocess, 'check_output', return_value=str(tmp_path)):
        budget = runner.Budget(tmp_path/'evidence')
        with patch.object(runner, '_archive_value', side_effect=OSError('archive unavailable')):
            with pytest.raises(OSError, match='archive unavailable'):
                budget.run('archive-failure', 'forward', 1, lambda: pytest.fail('must not launch'))
        row = budget.data['executions'][-1]
        assert row['status'] == 'FAILED' and row['charged_propagations'] == 1
        assert row['exponential_actions'] == 0 and row['archive_index'] == {}
        budget.lock.close()
        budget = runner.Budget(tmp_path/'evidence')
        assert budget.data['executions'][-1]['status'] == 'FAILED'
        budget.lock.close()
