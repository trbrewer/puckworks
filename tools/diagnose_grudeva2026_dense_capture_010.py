#!/usr/bin/env python3
"""Solver-free dense capture replay. Diagnostic inputs are NEVER references."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import resource
import shutil
import sys
import time
from types import SimpleNamespace
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import scipy.integrate  # noqa: E402
from puckworks.analysis import grudeva2026_full_reference_010 as solver  # noqa: E402
from puckworks.analysis import grudeva2026_full_reference_010_io as io  # noqa: E402
from tools import run_grudeva2026_full_reference_010 as runner  # noqa: E402


def forbidden(*args, **kwargs):
    raise AssertionError('No integrator is authorized in diagnostic replay')


def check_plan(path):
    plan = json.loads(path.read_text())
    for name, digest in plan['implementation'].items():
        if io.sha256(ROOT/name) != digest:
            raise ValueError('Diagnostic implementation differs from prospective plan: '+name)
    if runner.environment() != plan['environment']:
        raise ValueError('Diagnostic environment differs from prospective plan')
    for name, digest in plan['preserved'].items():
        if io.sha256(ROOT/name) != digest:
            raise ValueError('Preserved scientific contract changed: '+name)
    return plan


def extract(source, output, plan):
    """Explicit diagnostic-only extraction, without admitting the failed archive."""
    manifest_path = source/'manifest.json'
    if io.sha256(manifest_path) != plan['original_manifest_sha256']:
        raise ValueError('Unexpected original manifest')
    manifest = json.loads(manifest_path.read_text())
    receipt = {'role': 'DIAGNOSTIC_INPUT_ONLY_NOT_ACCEPTED_STATE_RECOVERY',
               'original_archive_status': 'FAILED_QUARANTINED',
               'original_manifest_sha256': io.sha256(manifest_path), 'segments': []}
    for j, seg in enumerate(manifest['segments']):
        records = {}
        with zipfile.ZipFile(source/seg['file']) as bundle:
            for key in ('t', 'order', 'shift', 'denom', 'D'):
                target = output/f'segment-{j}-{key}.npy'
                with bundle.open(key+'.npy') as src, target.open('xb') as dst:
                    shutil.copyfileobj(src, dst, length=io.CHUNK_BYTES)
                # ZIP CRC is checked on extraction; raw NPY payload hash must
                # independently match the original producer's individual identity.
                got = io.payload_identity(target)
                if got != seg['arrays'][key]:
                    raise io.CaptureMismatch('Diagnostic input identity mismatch',
                            {'stage': 'INPUT_EXTRACTION', 'segment': j, 'component': key,
                             'expected': seg['arrays'][key], 'observed': got,
                             'retained_candidate': target.name,
                             'original_member': seg['file']+':'+key+'.npy',
                             'prior_bytes': 'Original ZIP member; candidate file remains quarantined'})
                records[key] = {'file': target.name, 'array': got, 'file_sha256': io.sha256(target)}
                target.chmod(0o444)
                print('VERIFIED_INPUT', j, key, got, flush=True)
        receipt['segments'].append(records)
    io.write_json(output/'INPUT.json', receipt)


def zip_target_witness(record, target):
    """Compare the original ZIP payload with a target using bounded buffers."""
    source_hash, target_hash = hashlib.sha256(), hashlib.sha256()
    offset = count = 0
    witness = None
    with zipfile.ZipFile(record['npz_file']) as archive, archive.open(record['member']+'.npy') as stream:
        version = np.lib.format.read_magic(stream)
        reader = np.lib.format.read_array_header_1_0 if version == (1, 0) else np.lib.format.read_array_header_2_0
        shape, fortran, dtype = reader(stream)
        if fortran or tuple(shape) != target.shape or dtype != target.dtype:
            raise ValueError('Original ZIP witness metadata differs from target')
        raw_target = memoryview(target.reshape(-1)).cast('B')
        while block := stream.read(io.CHUNK_BYTES):
            other = raw_target[offset:offset+len(block)]
            source_hash.update(block); target_hash.update(other)
            different = np.frombuffer(block, dtype=np.uint8) != np.frombuffer(other, dtype=np.uint8)
            count += int(np.count_nonzero(different.reshape(-1, dtype.itemsize).any(axis=1)))
            if witness is None and different.any():
                byte = int(np.argmax(different))
                start = max(0, byte//dtype.itemsize*dtype.itemsize-8*dtype.itemsize)
                stop = min(len(block), start+32*dtype.itemsize)
                witness = (offset+byte, offset+start,
                           np.frombuffer(block[start:stop], dtype=dtype).copy(),
                           np.frombuffer(other[start:stop], dtype=dtype).copy())
            offset += len(block)
    if offset != target.nbytes:
        raise ValueError('Original ZIP witness payload length differs')
    detail = {'source_payload_sha256': source_hash.hexdigest(), 'target_payload_sha256': target_hash.hexdigest(),
              'differing_entries': count, 'first_payload_byte': witness[0] if witness else None,
              'window_start_payload_byte': witness[1] if witness else None,
              'scope': 'original ZIP payload versus current target; independent bounded stream'}
    return detail, [('original_zip_window', witness[2], witness[3])] if witness else []


def check_replay_target(trajectory, inputs, receipt, context):
    """Keep available buffers and checked pieces if final input comparison fails."""
    for j, seg in enumerate(trajectory.segments):
        for name in ('t', 'D', 'shift', 'denom', 'order'):
            record = receipt['segments'][j][name]
            if seg['capture_commitment'][name] != record['array']:
                # Establish the primary failure and checked evidence BEFORE
                # fallible witness reads. Enrichment may fail independently.
                exc = io.CaptureMismatch('Completed diagnostic target differs from immutable input',
                        {**context, 'segment': j, 'moving': seg['moving'], 'component': name,
                         'comparisons': io.comparisons(record['array'], None,
                                                      seg['capture_commitment'][name]),
                         'completed_pieces': seg['dense_piece_commitments'],
                         'source_after_status': 'UNAVAILABLE_UNTIL_WITNESS_READ',
                         'input_record': record})
                exc.snapshots = [(f'segment-{k}-{key}', s[key], s['capture_commitment'][key])
                                 for k, s in enumerate(trajectory.segments) for key in ('t', 'y')]
                try:
                    if 'npz_file' in record:
                        detail, pairs = zip_target_witness(record, seg[name])
                        source_identity = {**record['array'], 'sha256': detail['source_payload_sha256']}
                    else:
                        prior = np.load(inputs/record['file'], allow_pickle=False, mmap_mode='r')
                        detail, pairs = {'input_file': record['file']}, [(name, prior, seg[name])]
                        source_identity = io.array_identity(prior)
                    exc.record.update(comparisons=io.comparisons(record['array'], source_identity,
                                      seg['capture_commitment'][name]), input_comparison=detail,
                                      source_after_status='READ')
                    exc.pairs = pairs
                except BaseException as secondary:
                    exc.record['enrichment_error'] = f'{type(secondary).__name__}: {secondary}'
                raise exc


def replay(inputs, output, plan):
    receipt = json.loads((inputs/'INPUT.json').read_text())
    if receipt['original_manifest_sha256'] != plan['original_manifest_sha256']:
        raise ValueError('Wrong replay input lineage')
    model = solver.Model(solver.Settings(**plan['layout_settings']))
    nv = model.n*model.width+2
    results, layouts = [], []
    for j, records in enumerate(receipt['segments']):
        if {k: v['array'] for k, v in records.items()} != plan['input_arrays'][j]:
            raise ValueError('Replay input differs from original individual commitments')
        source = {}
        for name, record in records.items():
            if 'npz_file' in record:
                # Explicit diagnostic-only selection of the original individually
                # verified D member. This does NOT admit its failed parent archive.
                if j != 1 or name != 'D' or record['member'] != 'D':
                    raise ValueError('Unexpected direct diagnostic member')
                with np.load(record['npz_file'], allow_pickle=False) as bundle:
                    value = bundle[record['member']]
                got = io.array_identity(value)
                if got != record['array']:
                    raise io.CaptureMismatch('Direct diagnostic input commitment mismatch',
                            {**{'segment': j, 'component': name}, 'expected': record['array'],
                             'observed': got, 'replay_input': record,
                             'witness_scope': 'Current loaded buffer only; no prior bytes in memory'},
                            [('loaded_input_self_comparison', value, value)])
                source[name] = value
                del value
                continue
            path = inputs/record['file']
            if Path(record['file']).name != record['file'] or io.payload_identity(path) != record['array']:
                raise ValueError('Replay input identity mismatch')
            source[name] = np.load(path, allow_pickle=False, mmap_mode='r')
        times = np.array(source['t'], copy=True)
        parts = []
        # Only preparation reads mapped inputs. ALL source pieces are then
        # owned resident writable buffers, as in the inspected SciPy source.
        for k, raw_order in enumerate(source['order']):
            order = int(raw_order)
            parts.append(SimpleNamespace(order=order,
                         D=np.array(source['D'][k, :order+1], copy=True, order='C'),
                         t_shift=np.array(source['shift'][k, :order], copy=True),
                         denom=np.array(source['denom'][k, :order], copy=True)))
        base = np.empty((len(times), nv))
        column = np.arange(nv, dtype=float)/32768
        for k in range(len(times)):
            base[k] = column+(k+1)/1048576
        base[0, 0] = -0.
        y = base.T  # observed SciPy accepted-y ownership/strides; synthetic bytes
        result = SimpleNamespace(t=times, y=y, sol=SimpleNamespace(interpolants=parts),
                                 success=True, message='solver-free replay; synthetic y', nfev=0, njev=0, nlu=0)
        results.append((j == 0, result))
        layouts.append({'segment': j, 't': io.memory_layout(times), 'y': io.memory_layout(y),
                        'orders': {str(o): sum(p.order == o for p in parts) for o in range(1, 6)},
                        'source_dense_bytes': sum(p.D.nbytes+p.t_shift.nbytes+p.denom.nbytes for p in parts),
                        'example_piece': {k: io.memory_layout(v) for k, v in io._dense_values(parts[0]).items()}})
        del source
        print('RESIDENT_SEGMENT_READY', j, len(times), layouts[-1]['source_dense_bytes'], flush=True)
    io.write_json(output/'RESIDENT_INPUT.json', {'input_sha256': io.sha256(inputs/'INPUT.json'),
                                               'layouts': layouts, 'solver_calls': 0})
    context = {'run': output.name, 'diagnostic': 'retained-dense-resident-replay',
               'replay_input': {'INPUT_sha256': io.sha256(inputs/'INPUT.json'),
                                'original_manifest_sha256': receipt['original_manifest_sha256'],
                                'synthetic_y_rule': 'C base[k,i]=i/32768+(k+1)/1048576; base[0,0]=-0; y=base.T'}}
    try:
        trajectory = io.capture(model, results, context)
    except io.CaptureMismatch as exc:
        runner.preserve_run_failure(output, exc, {'stage': 'CAPTURING', 'exception': type(exc).__name__,
                                                 'message': str(exc), 'solver_calls': 0})
        raise
    summaries = []
    check_replay_target(trajectory, inputs, receipt, context)
    for seg in trajectory.segments:
        summaries.append({k: seg[k] for k in ('moving', 'capture_commitment', 'dense_comparisons',
                                              'dense_piece_commitments')})
    io.write_json(output/'CAPTURE.json', {'role': 'DIAGNOSTIC_ONLY_NOT_A_TRAJECTORY_ARCHIVE',
                                        'segments': summaries})
    return {'status': 'PASS_ON_DECLARED_DIAGNOSTIC_WORKLOADS', 'segments': len(summaries),
            'input_sha256': io.sha256(inputs/'INPUT.json'),
            'capture_sha256': io.sha256(output/'CAPTURE.json'), 'solver_calls': 0,
            'accepted_state_oracle': 'NONE; synthetic y, no numerical qualification'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['extract', 'replay'])
    parser.add_argument('--plan', required=True, type=Path)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    # Belt-and-braces denial in this process, not a modified scientific solver.
    solver.integrate = solver.solve_ivp = runner.integrate = scipy.integrate.solve_ivp = forbidden
    plan = check_plan(args.plan)
    args.output.mkdir(exist_ok=False)
    start = time.monotonic()
    io.write_json(args.output/'START.json', {'action': args.action, 'started': runner.now(),
                  'plan_sha256': io.sha256(args.plan), 'environment': runner.environment(),
                  'resources': runner.resources(), 'input': str(args.input), 'solver_calls': 0})
    try:
        if runner.resources()['available_bytes'] < plan['memory_admission_bytes']:
            raise OSError('Insufficient real available memory for declared resident workload')
        if shutil.disk_usage(args.output).free < plan['disk_admission_bytes']:
            raise OSError('Insufficient disk headroom for inputs/quarantine')
        if args.action == 'extract':
            extract(args.input, args.output, plan)
            result = {'status': 'INDIVIDUAL_DENSE_INPUT_IDENTITIES_VERIFIED', 'solver_calls': 0}
        else:
            result = replay(args.input, args.output, plan)
        io.write_json(args.output/'END.json', {**result, 'ended': runner.now(),
                      'elapsed_seconds': time.monotonic()-start,
                      'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
    except BaseException as exc:
        if isinstance(exc, io.CaptureMismatch) and not (args.output/'failure.json').exists():
            runner.preserve_run_failure(args.output, exc, {'stage': 'DIAGNOSTIC_TARGET_CHECK',
                                        'exception': type(exc).__name__, 'message': str(exc)})
        try:
            io.write_json(args.output/'EXIT_FAILURE.json', {'exception': type(exc).__name__, 'message': str(exc),
                          'elapsed_seconds': time.monotonic()-start, 'solver_calls': 0})
        except BaseException as secondary:
            print('Secondary diagnostic exit-record failure:', repr(secondary), file=sys.stderr, flush=True)
        raise


if __name__ == '__main__':
    main()
