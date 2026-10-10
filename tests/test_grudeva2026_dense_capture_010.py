"""Solver-free deliberate faults; never applied to retained scientific evidence."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import numpy as np
import pytest

from puckworks.analysis import grudeva2026_full_reference_010_io as io
from puckworks.analysis.grudeva2026_full_reference_010 import Model, Settings


def fixture(layout='C'):
    model = Model(Settings(axial=3, fines=3, boulders=3))
    nv = model.n*model.width+2
    t = np.linspace(1., 8., 6)
    y = (np.arange(6*nv, dtype=float).reshape(6, nv)/17).T
    parts = []
    for order in range(1, 6):
        a = np.arange((order+1)*nv, dtype=float).reshape(order+1, nv)/13
        a[0, 0] = -0.
        if layout == 'transpose':
            a = np.array(a.T, order='C').T
        if layout == 'stride':
            backing = np.zeros((order+1, 2*nv)); backing[:, ::2] = a; a = backing[:, ::2]
        parts.append(SimpleNamespace(order=order, D=a, t_shift=np.arange(order, dtype=float),
                                     denom=np.arange(1, order+1, dtype=float)))
    result = SimpleNamespace(t=t, y=y, sol=SimpleNamespace(interpolants=parts),
                             success=True, message='synthetic diagnostic fixture', nfev=0, njev=0, nlu=0)
    return model, result


def independent_part(part):
    def identity(a):
        return {'shape': list(a.shape), 'dtype': a.dtype.str,
                'sha256': hashlib.sha256(a.tobytes(order='C')).hexdigest()}
    return {'order': int(part.order), 'D': identity(part.D),
            'shift': identity(part.t_shift), 'denom': identity(part.denom)}


@pytest.mark.parametrize('layout', ['C', 'transpose', 'stride'])
def test_dense_orders_and_independent_canonical_commitment(layout):
    model, result = fixture(layout)
    chain = hashlib.sha256()
    for part in result.sol.interpolants:
        expected = json.dumps(independent_part(part), sort_keys=True).encode()
        assert io._dense_part_commitment(part.order, part.D, part.t_shift, part.denom) == expected
        chain.update(expected)
    trajectory = io.capture(model, [(False, result)])
    seg = trajectory.segments[0]
    assert seg['dense_source_chain_sha256'] == chain.hexdigest()
    assert seg['dense_comparisons']['source_matches'] and seg['dense_comparisons']['target_matches']
    for j, part in enumerate(result.sol.interpolants):
        assert seg['D'][j, :part.order+1].tobytes() == part.D.tobytes(order='C')
        assert np.signbit(seg['D'][j, 0, 0])
        assert seg['D'][j, part.order+1:].tobytes() == np.zeros_like(seg['D'][j, part.order+1:]).tobytes()


def fault_child(output, fault):
    """Fresh child calls the real run_row exception path with a solver-free stub."""
    from tools import run_grudeva2026_full_reference_010 as runner
    model, result = fixture()
    output = Path(output); output.mkdir()
    # Immutable pre-injection replay material, exact bytes, safe numeric format.
    np.save(output/'prior-D.npy', result.sol.interpolants[0].D, allow_pickle=False)
    inputs = {'file': 'prior-D.npy', 'sha256': io.sha256(output/'prior-D.npy'),
              'array': independent_part(result.sol.interpolants[0])['D']}
    io.write_json(output/'INPUT.json', inputs)
    original = io._dense_part_commitment
    zeros, empty = np.zeros, np.empty
    target = {}; calls = 0
    def track_zeros(shape, *args, **kwargs):
        a = zeros(shape, *args, **kwargs)
        if shape == (5, 6, len(result.y)):
            target['D'] = a
        return a
    def track_empty(shape, *args, **kwargs):
        a = empty(shape, *args, **kwargs)
        if shape == 5 and kwargs.get('dtype') == np.int8:
            target['order'] = a
        return a
    def inject(order, D, shift, denom):
        nonlocal calls
        calls += 1
        if calls == 6:
            if fault in ('source', 'both'):
                result.sol.interpolants[0].D.view(np.uint64)[0, 4] ^= np.uint64(1)
            if fault in ('target', 'both', 'persist'):
                target['D'].view(np.uint64)[0, 0, 5] ^= np.uint64(2)
            if fault == 'padding':
                target['D'][0, 5, 4] = -0.
            if fault == 'order':
                target['order'][0] = 4
        raw = original(order, D, shift, denom)
        if calls == 6 and fault == 'checker':
            v = json.loads(raw); v['D']['sha256'] = '0'*64
            return json.dumps(v, sort_keys=True).encode()
        return raw
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(np, 'zeros', track_zeros); patch.setattr(np, 'empty', track_empty)
        patch.setattr(io, '_dense_part_commitment', inject)
        patch.setattr(runner, 'load_matrix', lambda *_: {'rows': {'fixture': {}}})
        patch.setattr(runner, 'integrate', lambda *_: (model, [(False, result)]))
        patch.setattr(runner, 'resources', lambda: {'available_bytes': 200*1024**3})
        original_capture = runner.capture
        def capture(*args, **kwargs):
            return original_capture(*args[:2], context={'run': 'fixture', 'diagnostic': fault,
                                                       'replay_input': inputs})
        patch.setattr(runner, 'capture', capture)
        if fault == 'persist':
            def fail(*args, **kwargs):
                raise OSError('INJECTED witness persistence failure')
            patch.setattr(io, 'write_numeric', fail)
        runner.run_row(output/'run', 'fixture')


@pytest.mark.parametrize('fault', ['source', 'target', 'both', 'order', 'padding', 'checker', 'persist'])
def test_fresh_process_failure_preservation(tmp_path, fault):
    output = tmp_path/'fault'
    command = 'import runpy,sys; runpy.run_path(sys.argv[1])["fault_child"](sys.argv[2],sys.argv[3])'
    completed = subprocess.run([sys.executable, '-c', command, str(Path(__file__)), str(output), fault],
                               capture_output=True, text=True)
    assert completed.returncode == 1, completed.stderr
    q = output/'run/fixture/capture-quarantine'
    failure = json.loads((output/'run/fixture/failure.json').read_text())
    assert failure['stage'] == 'CAPTURING'
    assert failure['exception'] == 'CaptureMismatch'
    record = json.loads((q/'FAILURE.json').read_text())
    check = record['comparisons']
    assert check['source_matches'] == (fault not in ('source', 'both', 'checker'))
    assert check['target_matches'] == (fault not in ('target', 'both', 'order', 'persist'))
    assert record['segment'] == 0 and record['moving'] is False
    assert record['issues'][0]['interval'] == 0
    assert record['issues'][0]['times'] == [1., 2.4]
    assert len(record['prospective_pieces']) == len(record['source_after_pieces']) == len(record['target_pieces']) == 5
    receipt = json.loads((q/'PRESERVATION.json').read_text())
    assert not (q/'manifest.json').exists()
    with pytest.raises(FileNotFoundError):
        io.load_archive(q)
    if fault == 'persist':
        assert receipt['errors'] and receipt['status'] == 'PARTIAL_EVIDENCE_WRITE_FAILURE'
        assert 'INJECTED witness persistence failure' in completed.stderr
        assert (q/'witness-0.json').exists()
        return
    assert receipt['status'] == 'PRESERVED' and len(receipt['snapshots']) == 2
    # Independent fresh reader reproduces witness bytes/count from safe files.
    reader = '''import json,sys,numpy as np
from pathlib import Path
p=Path(sys.argv[1]); r=json.loads((p/'PRESERVATION.json').read_text())
for j,w in enumerate(r['witnesses']):
 if w['status']=='METADATA_DIFFERENCE': continue
 a=np.load(p/f'witness-{j}-source.npy',allow_pickle=False)
 b=np.load(p/f'witness-{j}-target.npy',allow_pickle=False)
 mask=a.view(np.uint8)!=b.view(np.uint8)
 assert int(mask.sum())==w['differing_bytes']
 assert int(mask.reshape(-1,a.itemsize).any(axis=1).sum())==w['differing_entries']
 if mask.any(): assert int(np.flatnonzero(mask)[0])==w['first_byte']
print('reproduced')'''
    read = subprocess.run([sys.executable, '-c', reader, str(q)], capture_output=True, text=True)
    assert read.returncode == 0, read.stderr
    if fault == 'checker':
        assert receipt['witnesses'][0]['status'] == 'NO_CURRENT_BYTE_DIFFERENCE'
        prior = np.load(output/'prior-D.npy', allow_pickle=False)
        assert hashlib.sha256(prior.tobytes()).hexdigest() == record['prospective_pieces'][0]['commitment']['D']['sha256']
        assert (q/'witness-0-source.npy').exists()


def test_essential_record_failure_does_not_mask_original(tmp_path, monkeypatch, capsys):
    from tools.run_grudeva2026_full_reference_010 import preserve_run_failure
    def fail(*args, **kwargs):
        raise OSError('INJECTED no space')
    monkeypatch.setattr(io, 'write_json', fail)
    error = io.CaptureMismatch('original mismatch', {'component': 'D'})
    preserve_run_failure(tmp_path, error, {'message': str(error)})
    assert json.loads((tmp_path/'failure.json').read_text())['message'] == 'original mismatch'
    assert 'INJECTED no space' in capsys.readouterr().err


def test_source_metadata_rejected_with_prospective_identity():
    model, result = fixture()
    result.sol.interpolants[0].D = result.sol.interpolants[0].D.astype(np.float32)
    with pytest.raises(io.CaptureMismatch) as raised:
        io.capture(model, [(False, result)])
    r = raised.value.record
    assert r['stage'] == 'before_copy' and r['interval'] == 0
    assert r['prospective_pieces'][0]['commitment']['D']['dtype'] == '<f4'


@pytest.mark.parametrize('direct_zip', [False, True])
def test_replay_final_input_mismatch_preserves_available_buffers(tmp_path, direct_zip):
    from tools.diagnose_grudeva2026_dense_capture_010 import check_replay_target
    from tools.run_grudeva2026_full_reference_010 import preserve_run_failure
    model, result = fixture()
    trajectory = io.capture(model, [(False, result)])
    seg = trajectory.segments[0]
    records = {}
    for name in ('t', 'D', 'shift', 'denom', 'order'):
        path = tmp_path/(name+'.npy')
        np.save(path, seg[name], allow_pickle=False)
        records[name] = {'file': path.name, 'array': io.array_identity(seg[name])}
    if direct_zip:
        np.savez(tmp_path/'original.npz', D=seg['D'])
        records['D'] = {'npz_file': str(tmp_path/'original.npz'), 'member': 'D',
                        'array': io.array_identity(seg['D'])}
    seg['D'].flags.writeable = True
    seg['D'][0, 0, 2] = .125  # deliberate fixture corruption, never science
    seg['capture_commitment']['D'] = io.array_identity(seg['D'])
    with pytest.raises(io.CaptureMismatch) as caught:
        check_replay_target(trajectory, tmp_path, {'segments': [records]}, {'diagnostic': 'injected'})
    preserve_run_failure(tmp_path, caught.value, {'message': str(caught.value)})
    q = tmp_path/'capture-quarantine'
    record = json.loads((q/'FAILURE.json').read_text())
    assert record['comparisons']['source_matches'] and not record['comparisons']['target_matches']
    assert len(record['completed_pieces']) == 5
    receipt = json.loads((q/'PRESERVATION.json').read_text())
    assert receipt['status'] == 'PRESERVED'
    if direct_zip:
        assert record['input_comparison']['first_payload_byte'] is not None
        assert record['input_comparison']['differing_entries'] == 1
    else:
        assert receipt['witnesses'][0]['first_index'] == [0, 0, 2]
    assert len(receipt['snapshots']) == 2


@pytest.mark.parametrize('direct_zip', [False, True])
def test_replay_witness_read_failure_preserves_primary_mismatch(tmp_path, monkeypatch, direct_zip):
    from tools import diagnose_grudeva2026_dense_capture_010 as diagnostic
    from tools.run_grudeva2026_full_reference_010 import preserve_run_failure
    model, result = fixture()
    trajectory = io.capture(model, [(False, result)])
    seg = trajectory.segments[0]
    records = {k: {'file': k+'.npy', 'array': dict(seg['capture_commitment'][k])}
               for k in ('t', 'D', 'shift', 'denom', 'order')}
    records['D']['array']['sha256'] = '0'*64  # stale fixture expectation
    if direct_zip:
        records['D'].update(npz_file='missing-original.npz', member='D')
        def unavailable(*args):
            raise OSError('INJECTED witness read failure')
        monkeypatch.setattr(diagnostic, 'zip_target_witness', unavailable)
    with pytest.raises(io.CaptureMismatch) as caught:
        diagnostic.check_replay_target(trajectory, tmp_path, {'segments': [records]}, {})
    preserve_run_failure(tmp_path, caught.value, {'message': str(caught.value)})
    record = json.loads((tmp_path/'capture-quarantine/FAILURE.json').read_text())
    assert record['message'] == 'Completed diagnostic target differs from immutable input'
    assert not record['comparisons']['target_matches']
    assert record['comparisons']['source_after'] is None
    assert record['source_after_status'] == 'UNAVAILABLE_UNTIL_WITNESS_READ'
    assert record['enrichment_error'] and len(record['completed_pieces']) == 5
    preserved = json.loads((tmp_path/'capture-quarantine/PRESERVATION.json').read_text())
    assert len(preserved['snapshots']) == 2
