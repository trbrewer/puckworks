"""Manufactured returned solutions only: persistence, fidelity and retained failure."""
from dataclasses import asdict
from types import SimpleNamespace

import numpy as np
import pytest
from scipy.integrate._ivp.bdf import BdfDenseOutput
from scipy.integrate._ivp.common import OdeSolution

from puckworks.analysis import grudeva2026_baseline_observation_005 as obs


def returned(a=0., b=1., size=4):
    # y_i(t)=(i+1)*t**2; coefficients and states independently derived.
    scale = np.arange(1., size+1)
    h = b-a
    differences = np.outer([b*b, 2*b*h-h*h, 2*h*h], scale)
    dense = BdfDenseOutput(a, b, h, 2, differences)
    t = np.array([a, b])
    r = SimpleNamespace(t=t, y=scale[:, None]*t[None, :]**2,
                        sol=OdeSolution(t, [dense], alt_segment=True), success=True,
                        status=1, message='manufactured event', nfev=0, njev=0, nlu=0,
                        t_events=[np.array([b])], y_events=[(scale*b*b)[None, :]])
    return dict(solution=r, requested_interval=[a, b], fixed=a >= 2, dripping=a >= 1)


def persist(folder, i=0):
    return obs.save_segment(folder, f'fixture-segment-{i}.npz', returned(i, i+1), 4,
                            attempt='manufactured', segment_index=i)


def test_three_segments_direct_fidelity_replay_and_independent_values(tmp_path):
    for i in range(3):
        m = persist(tmp_path, i)
        assert all(m[k] == 'PASS' for k in ('capture_outcome', 'artifact_integrity', 'array_fidelity', 'numerical_replay'))
        assert m['array_verification']['checked'] == len(m['array_manifest'])
        assert m['writer']['expected_sha256'] == m['file_verification']['observed_sha256'] == m['sha256']
        assert obs.sha(tmp_path/m['receipt_file']) == m['receipt_sha256']
        s = obs.Segment(tmp_path, m, 4)
        for t in [float(i), i+.13, i+.5, np.nextafter(float(i+1), float(i)), float(i+1)]:
            np.testing.assert_allclose(s.evaluate(t), np.arange(1., 5)*t*t, rtol=0, atol=2e-14)
        with np.load(tmp_path/m['file'], allow_pickle=False) as d:
            np.testing.assert_array_equal(d['accepted_y'], np.arange(1., 5)[:, None]*np.array([i, i+1])[None, :]**2)
            assert all(obs._array_identity(d[k]) == value for k, value in m['array_manifest'].items())
        s.close()


@pytest.mark.parametrize('failure', ['hash', 'replacement', 'truncated', 'payload', 'replay'])
def test_third_segment_failure_retains_expected_and_observed(tmp_path, monkeypatch, failure):
    for i in range(2):
        persist(tmp_path, i)
    check, save, segment = obs._segment_file_check, obs.np.savez, obs.Segment
    if failure in ('hash', 'replacement', 'truncated'):
        def bad_check(path, expected, record):
            if failure == 'hash':
                # Wrong expected metadata remains wrong; never repair it to pass.
                expected = '0'*64
            elif failure == 'replacement':
                replacement = path.with_suffix('.replacement')
                replacement.write_bytes(b'a different artifact')
                replacement.replace(path)
            else:
                with path.open('r+b') as f:
                    f.truncate(25)
            check(path, expected, record)
        monkeypatch.setattr(obs, '_segment_file_check', bad_check)
    elif failure == 'payload':
        def changed(f, **arrays):
            arrays = dict(arrays)
            arrays['D_0'] = arrays['D_0'].copy()
            arrays['D_0'][0, 0] += .25
            save(f, **arrays)
        monkeypatch.setattr(obs.np, 'savez', changed)
    else:
        class FailedReplay(segment):
            def evaluate(self, t):
                raise ArithmeticError('original replay failure')
        monkeypatch.setattr(obs, 'Segment', FailedReplay)
    with pytest.raises(obs.SegmentPersistenceError) as caught:
        persist(tmp_path, 2)
    m = caught.value.metadata
    assert m['capture_outcome'] == 'FAILED' and m['failure']['exception_message']
    assert len(m['writer']['expected_sha256']) == 64
    receipt = (tmp_path/m['receipt_file']).read_text()
    assert 'expected_file_identity' in receipt and '"stage":"failed"' in receipt
    if failure in ('hash', 'replacement', 'truncated'):
        assert m['file_verification']['expected_sha256'] != m['file_verification']['observed_sha256']
        assert m['array_fidelity'] == m['numerical_replay'] == 'NOT_CHECKED'
    elif failure == 'payload':
        assert m['artifact_integrity'] == 'PASS'  # ZIP bytes can agree while arrays differ.
        assert m['array_verification']['expected'] != m['array_verification']['observed']
        assert m['array_fidelity'] == 'FAILED'
    else:
        assert m['array_fidelity'] == 'PASS'
        assert m['failure']['exception_type'] == 'ArithmeticError'
        assert m['failure']['exception_message'] == 'original replay failure'


def test_existing_artifact_and_receipt_names_are_never_overwritten(tmp_path):
    first = persist(tmp_path)
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    with pytest.raises(obs.SegmentPersistenceError) as e:
        persist(tmp_path)
    assert e.value.metadata['failure']['exception_type'] == 'FileExistsError'
    assert all((tmp_path/name).read_bytes() == data for name, data in before.items())
    (tmp_path/first['file']).unlink()
    with pytest.raises(obs.SegmentPersistenceError):
        persist(tmp_path)
    assert (tmp_path/first['receipt_file']).read_bytes() == before[first['receipt_file']]


def test_malformed_archive_after_computed_identity_is_retained(tmp_path, monkeypatch):
    def malformed(f, **arrays):
        f.write(b'not an npz')
    monkeypatch.setattr(obs.np, 'savez', malformed)
    with pytest.raises(obs.SegmentPersistenceError) as e:
        persist(tmp_path)
    m = e.value.metadata
    assert m['artifact_integrity'] == 'PASS'
    assert m['array_fidelity'] == 'FAILED'
    assert m['sha256'] == m['file_verification']['observed_sha256']
    assert m['failure']['stage'] == 'array_fidelity'


def test_secondary_receipt_error_does_not_erase_original_failure(tmp_path, monkeypatch):
    original = obs._receipt_append
    def append(path, value, **kwargs):
        if value['stage'] == 'failed':
            raise OSError('secondary receipt failure')
        return original(path, value, **kwargs)
    monkeypatch.setattr(obs, '_receipt_append', append)
    def fail(path, expected, record):
        record.update(expected_sha256=expected, observed_sha256='1'*64)
        raise ValueError('original identity failure')
    monkeypatch.setattr(obs, '_segment_file_check', fail)
    with pytest.raises(obs.SegmentPersistenceError) as e:
        persist(tmp_path)
    m = e.value.metadata
    assert m['failure']['exception_message'] == 'original identity failure'
    assert m['receipt_failure']['exception_message'] == 'secondary receipt failure'
    assert 'expected_file_identity' in (tmp_path/m['receipt_file']).read_text()


@pytest.mark.parametrize('solver_exception', [False, True])
def test_execute_preserves_complete_public_or_original_solver_exception(tmp_path, monkeypatch, solver_exception):
    from puckworks.models.grudeva2026 import reduced
    c = dict(cells=8, modes=2, front_mesh_power=2., rtol=2e-8, atol=2e-10, max_step=.05)
    monkeypatch.setattr(obs, 'controls', lambda row: c)
    monkeypatch.setattr(obs, '_production_geometry', lambda captured: {})
    calls = []
    def original(fun, span, initial, **kwargs):
        r = returned(*span, size=34)['solution']; calls.append(r); return r
    monkeypatch.setattr(reduced, 'solve_ivp', original)
    result = reduced.Result('NUMERICAL_VERIFICATION_FAILED', asdict(reduced.Parameters()), c,
                            diagnostics={'preserved': True}, unavailable_reasons={'synthetic': 'keep this'})
    failure = RuntimeError('original simulation exception')
    def simulate(**kwargs):
        for i in range(3):
            assert reduced.solve_ivp(lambda t, y: y, (i, i+1), np.zeros(4), events=()) is calls[-1]
        if solver_exception:
            raise failure
        return result
    monkeypatch.setattr(reduced, 'simulate', simulate)
    original_check = obs._segment_file_check
    def check(path, expected, record):
        if '-2.npz' in path.name:
            record.update(expected_sha256=expected, observed_sha256='0'*64)
            raise ValueError('third segment identity failure')
        original_check(path, expected, record)
    monkeypatch.setattr(obs, '_segment_file_check', check)
    path = tmp_path/'run.json'
    if solver_exception:
        with pytest.raises(RuntimeError) as e:
            obs.execute(path)
        assert e.value is failure
    else:
        m = obs.execute(path)
        assert m['public_result'] == result.to_dict()
        assert obs.read_json(tmp_path/m['public_checkpoint']['file']) == result.to_dict()
        assert m['public_result_unchanged_after_capture']
    saved = obs.read_json(path)
    assert reduced.solve_ivp is original and saved['restored'] and saved['returned'] == 3
    assert saved['segments'][0]['capture_outcome'] == saved['segments'][1]['capture_outcome'] == 'PASS'
    failed = saved['segments'][2]
    assert failed['failure']['exception_message'] == 'third segment identity failure'
    assert failed['file_verification']['expected_sha256'] != failed['file_verification']['observed_sha256']
    if solver_exception:
        assert saved['original_exception'] == {'type': 'RuntimeError', 'message': str(failure)}
