"""010 observations and exact numeric archives; no pickle/source execution.

v1 remains readable and strict. v2 commits source bytes before serialization,
checks mutation boundaries, and independently verifies payload and loaded bytes.
"""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np

from .grudeva2026_full_reference_010 import Case, Model, Settings, liquid_flux

CHUNK_BYTES = 4 * 1024**2
SCHEMA = 'grudeva-full-010-v2'


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(CHUNK_BYTES), b''):
            h.update(block)
    return h.hexdigest()


def numeric_chunks(value):
    """Bounded C-order stream, including transposes/strides; no full byte copy."""
    a = np.asarray(value)
    if a.dtype.kind not in 'fiu':
        raise ValueError('Only numeric float/integer arrays are supported')
    if a.flags.c_contiguous:
        if a.size:
            raw = memoryview(a.reshape(-1)).cast('B')
            for start in range(0, len(raw), CHUNK_BYTES):
                yield raw[start:start+CHUNK_BYTES]
    else:
        with np.nditer(a, flags=['external_loop', 'buffered', 'zerosize_ok'],
                       op_flags=['readonly'], order='C',
                       buffersize=max(1, CHUNK_BYTES//a.itemsize)) as iterator:
            for block in iterator:
                yield memoryview(np.ascontiguousarray(block)).cast('B')


def array_identity(value):
    a = np.asarray(value)
    h = hashlib.sha256()
    for block in numeric_chunks(a):
        h.update(block)
    return {'shape': list(a.shape), 'dtype': a.dtype.str, 'sha256': h.hexdigest()}


def finite(value):
    a = np.asarray(value)
    for block in numeric_chunks(a):
        if not np.isfinite(np.frombuffer(block, dtype=a.dtype)).all():
            return False
    return True


def stable_copy(value, context=None):
    """Commit before copy; ownership/contiguity alone never proves identity."""
    before = array_identity(value)
    snapshot = np.array(value, copy=True, order='C')
    after, target = array_identity(value), array_identity(snapshot)
    if after != before or target != before:
        raise CaptureMismatch('Snapshot commitment mismatch',
                              {**(context or {}), 'stage': 'snapshot',
                               'comparisons': comparisons(before, after, target)},
                              [('snapshot', value, snapshot)])
    snapshot.flags.writeable = False
    return snapshot


def write_json(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def comparisons(before, after, target):
    """All operands are evaluated by the caller, including on a source mismatch."""
    return {'prospective_source': before, 'source_after': after,
            'completed_target': target, 'source_matches': after == before,
            'target_matches': target == before, 'source_target_match': after == target}


def memory_layout(value):
    a = np.asarray(value)
    return {'shape': list(a.shape), 'dtype': a.dtype.str, 'canonical_order': 'C',
            'strides': list(a.strides), 'owned': bool(a.flags.owndata),
            'writeable': bool(a.flags.writeable), 'C': bool(a.flags.c_contiguous),
            'F': bool(a.flags.f_contiguous), 'base_type': type(a.base).__name__}


class CaptureMismatch(ValueError):
    """Neutral integrity failure; live references are quarantined before unwind.

    No inference about a mutation mechanism follows from a digest discrepancy.
    Pairs are current source/target, never a fabricated copy of prior bytes.
    """
    def __init__(self, message, record, pairs=()):
        super().__init__(message)
        self.record = {'status': 'QUARANTINED_NOT_A_REFERENCE', 'message': message,
                       'prior_bytes': 'Unavailable unless identified immutable replay input supplies them',
                       **record}
        self.pairs = list(pairs)
        self.snapshots = []
        self.numeric_values = []


def nonfinite_detail(value):
    """Optional bounded witness of the current buffer, after primary preservation."""
    a = np.asarray(value)
    count, offset, first = 0, 0, None
    for raw in numeric_chunks(a):
        block = np.frombuffer(raw, dtype=a.dtype)
        bad = ~np.isfinite(block)
        count += int(np.count_nonzero(bad))
        if first is None and bad.any():
            first = offset + int(np.flatnonzero(bad)[0])
        offset += block.size
    result = {'scope': 'current buffer during later enrichment, not earlier comparison bytes',
              'nonfinite_count': count, 'first_flat_index': first,
              'first_index': None if first is None else [int(i) for i in np.unravel_index(first, a.shape)]}
    if first is not None:
        start, stop = max(0, first-8), min(a.size, first+24)
        window = a.flat[start:stop]
        result['window'] = {'flat_elements': [start, stop], 'dtype': a.dtype.str,
                            'values_repr': [repr(v.item()) for v in window],
                            'bytes_hex': window.tobytes().hex()}
    return result


def byte_difference(source, target):
    """Independent bounded flat-slice bytes, not the commitment chunk helper.

    This describes current buffers. It cannot locate changed prior bytes when
    only an earlier digest survives. Signed zero is distinguished exactly.
    """
    detail = {'source_layout': memory_layout(source), 'target_layout': memory_layout(target),
              'shares_memory': bool(np.shares_memory(source, target)),
              'comparison_scope': 'current source versus current target'}
    if source.shape != target.shape or source.dtype != target.dtype:
        return {**detail, 'status': 'METADATA_DIFFERENCE', 'first_byte': None}, {}
    count = byte_count = 0
    first = None
    for start in range(0, source.size, 32768):
        a = np.frombuffer(source.flat[start:start+32768].tobytes(), dtype=np.uint8)
        b = np.frombuffer(target.flat[start:start+32768].tobytes(), dtype=np.uint8)
        different = a != b
        byte_count += int(np.count_nonzero(different))
        count += int(np.count_nonzero(different.reshape(-1, source.itemsize).any(axis=1)))
        if first is None and different.any():
            first = start*source.itemsize + int(np.flatnonzero(different)[0])
    detail.update(status='OBSERVED_BYTE_DIFFERENCE' if count else 'NO_CURRENT_BYTE_DIFFERENCE',
                  differing_entries=count, differing_bytes=byte_count, first_byte=first,
                  first_index=[int(i) for i in np.unravel_index(first//source.itemsize, source.shape)] if first is not None else None)
    # A small piece is retained in full; t/y get a bounded C-order witness window.
    start = max(0, (first//source.itemsize if first is not None else 0)-8)
    if source.nbytes <= 2*1024**2:
        start, stop = 0, source.size
    else:
        stop = min(source.size, start+32)
    detail['window_flat_elements'] = [start, stop]
    return detail, {'source': source.flat[start:stop], 'target': target.flat[start:stop]}


def persist_capture_failure(directory, exc):
    """Essential record first, safe bounded numeric witnesses second; never mask exc."""
    directory = Path(directory)
    receipt = {'status': 'INCOMPLETE', 'errors': [], 'witnesses': [], 'snapshots': []}
    try:
        directory.mkdir(exist_ok=False)
        write_json(directory/'FAILURE.json', exc.record)
    except BaseException as error:
        receipt['errors'].append(f'essential record: {type(error).__name__}: {error}')
        print('Capture diagnostic preservation failure:', receipt, file=sys.stderr, flush=True)
        return receipt
    # No count/location scan or witness construction precedes FAILURE.json.
    for index, (role, value) in enumerate(exc.numeric_values):
        try:
            write_json(directory/f'numeric-detail-{index}.json',
                       {'role': role, **nonfinite_detail(value)})
        except BaseException as error:
            receipt['errors'].append(f'numeric detail {role}: {type(error).__name__}: {error}')
    for index, (component, source, target) in enumerate(exc.pairs[:8]):
        try:
            detail, arrays = byte_difference(source, target)
            detail['component'] = component
            detail['arrays'] = {}
            # Record the scalar/byte comparison before attempting numeric writes.
            write_json(directory/f'witness-{index}.json', detail)
            for name, value in arrays.items():
                # Nonfinite floating witnesses are retained as exact bytes; the
                # numeric writer still rejects nonfinite scientific arrays.
                encoding = {'dtype': value.dtype.str, 'shape': list(value.shape)}
                if not finite(value):
                    value = np.ascontiguousarray(value).view(np.uint8)
                    encoding['storage'] = 'raw bytes of nonfinite numeric witness'
                expected = array_identity(value)
                detail['arrays'][name] = {**write_numeric(directory/f'witness-{index}-{name}.npy', value, expected),
                                         'original_numeric_encoding': encoding}
            receipt['witnesses'].append(detail)
        except BaseException as error:
            receipt['errors'].append(f'witness {index}: {type(error).__name__}: {error}')
    receipt['unretained_pair_count'] = max(0, len(exc.pairs)-8)
    # Preserve previously checked accepted t/y snapshots without another full
    # memory copy. Completed dense pieces are represented by their commitments
    # and bounded witnesses; duplicating all dense targets is deliberately avoided.
    for name, value, expected in exc.snapshots:
        try:
            receipt['snapshots'].append(write_numeric(directory/f'{name}.npy', value, expected))
        except BaseException as error:
            receipt['errors'].append(f'snapshot {name}: {type(error).__name__}: {error}')
    receipt['status'] = 'PRESERVED' if not receipt['errors'] else 'PARTIAL_EVIDENCE_WRITE_FAILURE'
    try:
        write_json(directory/'PRESERVATION.json', receipt)
    except BaseException as error:
        receipt['errors'].append(f'preservation receipt: {type(error).__name__}: {error}')
        print('Capture diagnostic preservation failure:', receipt, file=sys.stderr, flush=True)
    return receipt


class Trajectory:
    def __init__(self, model, segments):
        self.model, self.segments = model, segments

    def state(self, t):
        if t < 0 or t > self.segments[-1]['t'][-1]:
            raise ValueError('Time outside captured support')
        if t <= self.model.settings.startup:
            return self.model.startup(t)
        segment = self.segments[0] if t <= 1 else self.segments[-1]
        times = segment['t']
        if t < times[0] or t > times[-1]:
            raise ValueError('Missing required segment')
        k = np.searchsorted(times, t, side='left')
        if k < len(times) and times[k] == t:
            return segment['y'][:, k].copy()
        k = max(0, k-1)
        order = int(segment['order'][k])
        p = np.cumprod((t-segment['shift'][k, :order]) / segment['denom'][k, :order])
        return segment['D'][k, 0] + p @ segment['D'][k, 1:order+1]


def _dense_part_commitment(order, D, shift, denom):
    return json.dumps({'order': int(order), 'D': array_identity(D),
                       'shift': array_identity(shift), 'denom': array_identity(denom)},
                      sort_keys=True).encode()


def dense_chain(arrays, records=None, padding_issues=None):
    """Same canonical chain, with optional complete diagnostic collection."""
    chain = hashlib.sha256()
    for j, order in enumerate(arrays['order']):
        order = int(order)
        if order < 1 or order > 5:
            raise CaptureMismatch('Dense order metadata mismatch',
                                  {'interval': j, 'component': 'order', 'observed': order,
                                   'expected': 'integer 1..5'})
        raw = _dense_part_commitment(order, arrays['D'][j, :order+1],
                                    arrays['shift'][j, :order], arrays['denom'][j, :order])
        chain.update(raw)
        if records is not None:
            records.append(json.loads(raw))
        for name, actual, expected in [
                ('D', arrays['D'][j, order+1:], np.zeros_like(arrays['D'][j, order+1:])),
                ('shift', arrays['shift'][j, order:], np.ones_like(arrays['shift'][j, order:])),
                ('denom', arrays['denom'][j, order:], np.ones_like(arrays['denom'][j, order:]))]:
            got, want = array_identity(actual), array_identity(expected)
            if got != want:
                issue = {'interval': j, 'component': 'padding.'+name,
                         'expected': want, 'observed': got}
                if padding_issues is None:
                    raise CaptureMismatch('Dense padding commitment mismatch', issue,
                                          [('padding.'+name, expected, actual)])
                padding_issues.append((issue, expected, actual))
    return chain.hexdigest()


def _dense_values(part):
    return {'D': part.D, 'shift': part.t_shift, 'denom': part.denom}


def capture_dense(dense, nvar, times, context=None):
    """Actual per-piece capture, also used by the solver-free resident replay."""
    context = context or {}
    ns = len(dense)
    D = np.zeros((ns, 6, nvar))
    shift, denom = np.ones((ns, 5)), np.ones((ns, 5))
    order = np.empty(ns, dtype=np.int8)
    arrays = {'D': D, 'shift': shift, 'denom': denom, 'order': order}
    before = []
    source_chain = hashlib.sha256()
    for j, part in enumerate(dense):
        values = _dense_values(part)
        raw = _dense_part_commitment(part.order, values['D'], values['shift'], values['denom'])
        record = json.loads(raw)
        location = {'interval': j, 'times': [float(times[j]), float(times[j+1])]}
        before.append({**location, 'commitment': record,
                       'source_layouts': {k: memory_layout(v) for k, v in values.items()}})
        source_chain.update(raw)
        valid_order = isinstance(part.order, (int, np.integer)) and 1 <= part.order <= 5
        shapes = {'D': [int(part.order)+1, nvar], 'shift': [int(part.order)], 'denom': [int(part.order)]}
        if not valid_order or any(record[k]['shape'] != shapes[k] or record[k]['dtype'] != np.dtype('f8').str
                                  for k in values):
            raise CaptureMismatch('Dense source metadata mismatch',
                                  {**context, **location, 'stage': 'before_copy',
                                   'component': 'order/metadata', 'prospective_pieces': before,
                                   'expected_shapes': shapes, 'expected_dtype': np.dtype('f8').str})
        order[j] = part.order
        for name, source in values.items():
            target = arrays[name][j, :part.order+(name == 'D')]
            expected = record[name]
            target[...] = source
            after, got = array_identity(source), array_identity(target)
            check = comparisons(expected, after, got)
            if not check['source_matches'] or not check['target_matches']:
                raise CaptureMismatch('Dense piece commitment mismatch',
                                      {**context, **location, 'stage': 'piece_copy', 'component': name,
                                       'prospective_pieces': before, 'comparisons': check},
                                      [(name, source, target)])
    # Evaluate BOTH complete passes. No source-first short circuit.
    after, source_after = [], hashlib.sha256()
    for part in dense:
        raw = _dense_part_commitment(part.order, part.D, part.t_shift, part.denom)
        after.append(json.loads(raw))
        source_after.update(raw)
    target, padding = [], []
    try:
        target_chain = dense_chain(arrays, target, padding)
    except CaptureMismatch as exc:
        exc.record.update({**context, 'stage': 'final_dense_pass',
                           'prospective_pieces': before, 'source_after_pieces': after,
                           'target_pieces': target,
                           'comparisons': comparisons(source_chain.hexdigest(), source_after.hexdigest(), None),
                           'target_chain_unavailable': 'Invalid target metadata; see component/interval'})
        raise
    chains = comparisons(source_chain.hexdigest(), source_after.hexdigest(), target_chain)
    issues, pairs = [], []
    for j, prior in enumerate(before):
        for name in ('order', 'D', 'shift', 'denom'):
            check = comparisons(prior['commitment'][name], after[j][name], target[j][name])
            if not check['source_matches'] or not check['target_matches']:
                issues.append({'interval': j, 'times': prior['times'], 'component': name,
                               'comparisons': check})
                if name == 'order':
                    pairs.append((f'{j}.order', np.array([dense[j].order]), np.array([order[j]])))
                else:
                    pairs.append((f'{j}.{name}', _dense_values(dense[j])[name],
                                  arrays[name][j, :int(order[j])+(name == 'D')]))
    for issue, expected, actual in padding:
        issues.append({**issue, 'times': before[issue['interval']]['times']})
        pairs.append((f"{issue['interval']}.{issue['component']}", expected, actual))
    if not chains['source_matches'] or not chains['target_matches'] or issues:
        raise CaptureMismatch('Dense final commitment mismatch',
                              {**context, 'stage': 'final_dense_pass', 'comparisons': chains,
                               'prospective_pieces': before, 'source_after_pieces': after,
                               'target_pieces': target, 'issues': issues}, pairs)
    return arrays, {'dense_source_chain_sha256': source_chain.hexdigest(),
                    'dense_comparisons': chains, 'dense_piece_commitments': before}


def capture(model, results, context=None, checkpoints=None):
    segments, checked = [], []
    for segment_index, (moving, result) in enumerate(results):
        location = {**(context or {}), 'segment': segment_index, 'moving': bool(moving)}
        try:
            if checkpoints is None:
                t = stable_copy(result.t, {**location, 'component': 't'})
                y = stable_copy(result.y, {**location, 'component': 'y'})
            else:
                t, y = (checkpoints.segments[segment_index][k] for k in ('t', 'y'))
                for key, source, saved in [('t', result.t, t), ('y', result.y, y)]:
                    expected = checkpoints.segments[segment_index]['arrays'][key]['array']
                    check = comparisons(expected, array_identity(source), array_identity(saved))
                    if not check['source_matches'] or not check['target_matches']:
                        raise CaptureMismatch('Checkpoint/source commitment mismatch',
                                              {**location, 'component': key, 'comparisons': check},
                                              [(key, source, saved)])
            accepted = {'t': array_identity(t), 'y': array_identity(y)}
            checked.extend((f'segment-{segment_index}-{k}', a, accepted[k]) for k, a in [('t', t), ('y', y)])
            arrays, dense_receipt = capture_dense(result.sol.interpolants, len(y), t, location)
            arrays.update(t=t, y=y)
            identities = {k: array_identity(v) for k, v in arrays.items()}
            source_after = {'t': array_identity(result.t), 'y': array_identity(result.y)}
            target_after = {k: identities[k] for k in accepted}
            check = comparisons(accepted, source_after, target_after)
            if not check['source_matches'] or not check['target_matches']:
                raise CaptureMismatch('Accepted state commitment mismatch',
                                      {**location, 'stage': 'after_dense_capture', 'comparisons': check},
                                      [('t', result.t, t), ('y', result.y, y)])
            for value in arrays.values():
                value.flags.writeable = False
            segments.append({**arrays, 'moving': moving, 'capture_commitment': identities,
                             **dense_receipt, 'success': bool(result.success), 'message': result.message,
                             'nfev': result.nfev, 'njev': result.njev, 'nlu': result.nlu})
        except CaptureMismatch as exc:
            exc.record.update(location)
            exc.record['completed_segments'] = [
                {'moving': s['moving'], 'capture_commitment': s['capture_commitment'],
                 'dense_comparisons': s['dense_comparisons'],
                 'dense_piece_commitments': s['dense_piece_commitments']} for s in segments]
            exc.snapshots = checked
            raise
    return Trajectory(model, segments)


def payload_identity(path):
    """Read NPY header and raw serialized bytes independently of NumPy loading."""
    with Path(path).open('rb') as stream:
        version = np.lib.format.read_magic(stream)
        if version == (1, 0):
            shape, fortran, dtype = np.lib.format.read_array_header_1_0(stream)
        elif version == (2, 0):
            shape, fortran, dtype = np.lib.format.read_array_header_2_0(stream)
        else:
            raise ValueError('Unsupported numeric NPY header')
        if dtype.kind not in 'fiu' or fortran:
            raise ValueError('Unsafe dtype or non-C payload ordering')
        remaining = int(np.prod(shape, dtype=object))*dtype.itemsize
        h = hashlib.sha256()
        while remaining:
            block = stream.read(min(CHUNK_BYTES, remaining))
            if not block:
                raise ValueError('Incomplete numeric payload')
            h.update(block)
            remaining -= len(block)
        if stream.read(1):
            raise ValueError('Unexpected trailing payload')
    return {'shape': list(shape), 'dtype': dtype.str, 'sha256': h.hexdigest()}


def numeric_checks(value, expected):
    """Evaluate both admission predicates; a failure never short-circuits the other."""
    result = {'expected': expected}
    try:
        result['observed'] = array_identity(value)
        result['identity'] = 'PASS' if result['observed'] == expected else 'FAIL'
    except Exception as error:
        result.update(identity='ERROR', observed=None, identity_error=f'{type(error).__name__}: {error}')
    try:
        result['finiteness'] = 'PASS' if finite(value) else 'FAIL'
    except Exception as error:
        result.update(finiteness='ERROR', finiteness_error=f'{type(error).__name__}: {error}')
    return result


def require_numeric(path, stage, checks, context, values=(), pairs=()):
    failures = [f'{role}.{predicate}' for role, result in checks.items()
                for predicate in ('identity', 'finiteness') if result.get(predicate) in ('FAIL', 'ERROR')]
    if failures:
        exc = CaptureMismatch(f'Numeric member rejected at {stage}: {Path(path).name}',
                              {**(context or {}), 'kind': 'NUMERIC_MEMBER_REJECTED',
                               'path': str(Path(path)), 'member': Path(path).name,
                               'archive_group': (context or {}).get('archive_group'),
                               'stage': stage, 'checks': checks, 'failed_conditions': failures,
                               'comparison_bytes': 'Current source/target pairs only; prospective hashes do not supply prior bytes'},
                              pairs)
        exc.numeric_values = list(values)
        raise exc


def write_numeric(path, value, expected, context=None):
    """Serialize against a prospective source commitment, never a file-derived one."""
    location = {**(context or {}), 'path': str(Path(path)), 'member': Path(path).name}
    require_numeric(path, 'pre_write_source', {'source': numeric_checks(value, expected)},
                    location, [('source', value)])
    # Capture snapshots already own read-only C buffers. Other callers get an
    # independent checked snapshot; ascontiguousarray alone would not suffice.
    a = value if (value.flags.owndata and value.flags.c_contiguous
                  and not value.flags.writeable) else stable_copy(value, location)
    with Path(path).open('xb') as stream:
        np.save(stream, a, allow_pickle=False)
        stream.flush()
        os.fsync(stream.fileno())
    require_numeric(path, 'post_write_source',
                    {'source': numeric_checks(value, expected), 'snapshot': numeric_checks(a, expected)},
                    location, [('source', value), ('snapshot', a)], [('source/snapshot', value, a)])
    raw_check = {'expected': expected, 'finiteness': 'NOT_APPLICABLE',
                 'finiteness_reason': 'Raw NPY bytes; safe loaded payload is checked independently below'}
    try:
        raw_check['observed'] = payload_identity(path)
        raw_check['identity'] = 'PASS' if raw_check['observed'] == expected else 'FAIL'
    except Exception as error:
        raw_check.update(identity='ERROR', observed=None, identity_error=f'{type(error).__name__}: {error}')
    loaded = None
    try:
        loaded = np.load(path, allow_pickle=False, mmap_mode='r')
        loaded_check = numeric_checks(loaded, expected)
    except Exception as error:
        loaded_check = {'expected': expected, 'observed': None, 'identity': 'ERROR', 'finiteness': 'ERROR',
                        'identity_error': f'{type(error).__name__}: {error}',
                        'finiteness_error': 'Safe numeric loading failed; no array to evaluate'}
    require_numeric(path, 'saved_payload', {'serialized_payload': raw_check, 'loaded_payload': loaded_check},
                    location, [] if loaded is None else [('loaded_payload', loaded)],
                    [] if loaded is None else [('source/loaded', value, loaded)])
    return {'file': Path(path).name, 'sha256': sha256(path), 'array': expected,
            'order': 'C', 'pre_write_source': 'PASS', 'post_write_source': 'PASS',
            'serialized_payload': 'PASS', 'independently_loaded_payload': 'PASS'}


def _same_bits(a, b):
    return a.dtype == b.dtype and a.shape == b.shape and array_identity(a) == array_identity(b)


def _segment_shape_check(model, arrays):
    nt = len(arrays['t'])
    nv = model.n*model.width+2
    shapes = {'t': (nt,), 'y': (nv, nt), 'D': (nt-1, 6, nv),
              'shift': (nt-1, 5), 'denom': (nt-1, 5), 'order': (nt-1,),
              'concentrations': (nt, nv-2), 'boundary_accumulators': (nt, 2),
              'physical_z_faces': (nt, model.n+1), 'physical_z_centers': (nt, model.n)}
    if set(arrays) != set(shapes):
        raise ValueError('Archive array set mismatch')
    for key, shape in shapes.items():
        if arrays[key].shape != shape or arrays[key].dtype != np.dtype('i1' if key == 'order' else 'f8'):
            raise ValueError('Archive dtype or shape mismatch')
    if nt < 1 or not np.all(np.diff(arrays['t']) > 0) or not np.all((arrays['order'] >= 1) & (arrays['order'] <= 5)):
        raise ValueError('Invalid accepted-time or dense-order support')
    if np.any(arrays['denom'] <= 0):
        raise ValueError('Invalid dense denominators')


PRIMARY_KEYS = ('t', 'y', 'D', 'shift', 'denom', 'order')


def concentration_blocks(t, y):
    """Original float64 C-layout construction, also used by solver-free checks."""
    concentrations = np.empty((len(t), len(y)-2))
    for start in range(0, len(t), 64):
        concentrations[start:start+64] = y[:-2, start:start+64].T/np.minimum(t[start:start+64, None], 1.)
    return concentrations


def _relationship(expected, observed, member, context, operands, before):
    want, got = array_identity(expected), array_identity(observed)
    after = {key: array_identity(value) for key, value in operands.items()}
    if want != got or before != after:
        exc = CaptureMismatch('Redundant '+member+' disagreement',
                              {**context, 'stage': 'redundancy', 'component': member,
                               'expected': want, 'observed': got, 'identity_matches': want == got,
                               'operand_identities_before': before, 'operand_identities_after': after,
                               'sources_stable': before == after}, [(member, expected, observed)])
        # Actual current operands, bounded by the existing preservation utility.
        exc.pairs.extend((key, value, value) for key, value in operands.items())
        raise exc


def check_concentrations(t, y, concentrations, context=None):
    """Exact separately evaluated block check; includes signed zero."""
    for start in range(0, len(t), 64):
        stop = min(start+64, len(t))
        operands = {'accepted_t': t[start:stop], 'accepted_y': y[:-2, start:stop].T}
        before = {key: array_identity(value) for key, value in operands.items()}
        scale = np.minimum(t[start:stop, None], 1.)
        want = y[:-2, start:stop].T/scale
        _relationship(want, concentrations[start:stop], 'concentrations',
                      {**(context or {}), 'block': [start, stop],
                       'time_range': [float(t[start]), float(t[stop-1])]}, operands, before)


def _redundancy(model, arrays, context=None):
    _segment_shape_check(model, arrays)
    check_concentrations(arrays['t'], arrays['y'], arrays['concentrations'], context)
    for start in range(0, len(arrays['t']), 64):
        stop = min(start+64, len(arrays['t']))
        scale = np.minimum(arrays['t'][start:stop, None], 1.)
        where = {**(context or {}), 'block': [start, stop],
                 'time_range': [float(arrays['t'][start]), float(arrays['t'][stop-1])]}
        expected = arrays['y'][-2:, start:stop].T
        _relationship(expected, arrays['boundary_accumulators'][start:stop],
                      'boundary_accumulators', where, {'accepted_accumulators': expected},
                      {'accepted_accumulators': array_identity(expected)})
        for key, coordinates in [('physical_z_faces', model.faces), ('physical_z_centers', model.xi)]:
            operands = {'scale': scale, 'coordinates': coordinates}
            before = {k: array_identity(v) for k, v in operands.items()}
            _relationship(scale*coordinates, arrays[key][start:stop], key, where, operands, before)


def verify_primary_archive(directory):
    """Verify preserved primary data only; never admit a full reference archive."""
    directory = Path(directory)
    receipt = json.loads((directory/'PRIMARY_INCOMPLETE.json').read_text())
    if (receipt['status'] != 'PRIMARY_ONLY_NOT_FULL_REFERENCE'
            or sha256(directory/'CAPTURE_METADATA.json') != receipt['capture_metadata_sha256']
            or sha256(directory/'PRIMARY_SOURCE_COMMITMENT.json') != receipt['source_commitment_sha256']):
        raise ValueError('Primary commitment identity mismatch')
    expected = json.loads((directory/'PRIMARY_SOURCE_COMMITMENT.json').read_text())
    if set(expected) != {f'segment-{j}' for j in range(len(receipt['segments']))}:
        raise ValueError('Primary segment set mismatch')
    for j, segment in enumerate(receipt['segments']):
        group = f'segment-{j}'
        if set(segment['arrays']) != set(PRIMARY_KEYS) or segment['capture_commitment'] != expected[group]:
            raise ValueError('Primary member/commitment mismatch')
        loaded = {}
        for key, rec in segment['arrays'].items():
            path = directory/f'{group}-{key}.npy'
            if (rec['file'] != path.name or rec['array'] != expected[group][key]
                    or sha256(path) != rec['sha256'] or payload_identity(path) != rec['array']):
                raise ValueError('Primary saved payload mismatch')
            value = np.load(path, allow_pickle=False, mmap_mode='r')
            if array_identity(value) != rec['array'] or not finite(value):
                raise ValueError('Primary loaded payload mismatch')
            loaded[key] = value
        if dense_chain(loaded) != segment['dense_source_chain_sha256']:
            raise ValueError('Primary dense chain mismatch')
    return receipt


def save_archive(directory, trajectory, metadata, complete=True, checkpoint_directory=None,
                 primary_readback=None):
    directory = Path(directory)
    directory.mkdir(exist_ok=False)
    model = trajectory.model
    write_json(directory/'WRITE_START.json', {'schema': SCHEMA, 'metadata': metadata})
    manifest = {'schema': SCHEMA, 'case': asdict(model.case),
                'settings': asdict(model.settings), 'metadata': metadata, 'segments': [],
                'geometry': {}, 'activation': 't_wet(z)=z; dry inactive; initial=1.388',
                'state_layout': 'y[:-2]=cell-major U=s*C amounts; last2=Jin,Jout; concentrations and accumulators stored separately',
                'transition': 't=1; identical end/start state; motion ends, discharge begins'}
    groups, prospective, primary_records = [], {}, {}
    for j, segment in enumerate(trajectory.segments):
        name = f'segment-{j}'
        arrays = {k: v for k, v in segment.items() if isinstance(v, np.ndarray)}
        source = {k: array_identity(v) for k, v in arrays.items()}
        if (set(arrays) != set(PRIMARY_KEYS) or source != segment.get('capture_commitment')
                or dense_chain(arrays) != segment['dense_source_chain_sha256']):
            raise ValueError('Captured primary source commitment/chain mismatch')
        info = {k: v for k, v in segment.items() if not isinstance(v, np.ndarray)}
        groups.append((name, info, arrays))
        prospective[name] = source
    # Capture metadata and prospective primary identities survive every later failure.
    write_json(directory/'CAPTURE_METADATA.json', {'metadata': metadata,
               'case': manifest['case'], 'settings': manifest['settings'],
               'segments': [info for _, info, _ in groups]})
    write_json(directory/'PRIMARY_SOURCE_COMMITMENT.json', prospective)
    for name, info, arrays in groups:
        records = {}
        for key in PRIMARY_KEYS:
            a, target = arrays[key], directory/f'{name}-{key}.npy'
            if checkpoint_directory is not None and key in ('t', 'y'):
                source = Path(checkpoint_directory)/target.name
                checkpoint = json.loads((Path(checkpoint_directory)/'checkpoint.json').read_text())
                rec = checkpoint['segments'][int(name.split('-')[1])]['arrays'][key]
                if (rec['array'] != prospective[name][key] or sha256(source) != rec['sha256']
                        or payload_identity(source) != rec['array']):
                    raise ValueError('Checkpoint archive member identity mismatch')
                os.link(source, target)
                if sha256(target) != rec['sha256'] or payload_identity(target) != rec['array']:
                    raise ValueError('Linked checkpoint identity mismatch')
                records[key] = rec
            else:
                records[key] = write_numeric(target, a, prospective[name][key],
                                             {'archive_group': name, 'component': key, 'archive_role': 'trajectory', 'phase': 'primary'})
        if prospective[name] != {key: array_identity(a) for key, a in arrays.items()}:
            raise ValueError('Source mutation across primary serialization')
        primary_records[name] = records
    write_json(directory/'PRIMARY_INCOMPLETE.json',
               {'status': 'PRIMARY_ONLY_NOT_FULL_REFERENCE', 'metadata': metadata,
                'source_commitment_sha256': sha256(directory/'PRIMARY_SOURCE_COMMITMENT.json'),
                'capture_metadata_sha256': sha256(directory/'CAPTURE_METADATA.json'),
                'segments': [{**info, 'arrays': primary_records[name]} for name, info, _ in groups]})
    sync_directory(directory)
    if primary_readback is not None:
        primary_readback(directory)
    else:
        verify_primary_archive(directory)
    # Only now construct redundant derivatives; scientific formulas/layout unchanged.
    for name, info, arrays in groups:
        source = prospective[name]
        arrays.update(concentrations=concentration_blocks(arrays['t'], arrays['y']),
                      boundary_accumulators=stable_copy(arrays['y'][-2:].T),
                      physical_z_faces=np.minimum(arrays['t'][:, None], 1.)*model.faces,
                      physical_z_centers=np.minimum(arrays['t'][:, None], 1.)*model.xi)
        if source != {k: array_identity(arrays[k]) for k in source}:
            raise ValueError('Source mutation during derived-array construction')
        _redundancy(model, arrays, {'archive_group': name, 'path': str(directory), 'phase': 'constructed'})
        for a in arrays.values():
            a.flags.writeable = False
    geometry = {'xi_faces': model.faces, 'xi': model.xi}
    for label, sphere in zip(('fines', 'boulders'), model.spheres):
        geometry.update({f'{label}_faces': sphere.faces, f'{label}_centers': sphere.r,
                         f'{label}_volumes': sphere.volume})
    groups.insert(0, ('geometry', {}, {k: stable_copy(v) for k, v in geometry.items()}))
    all_sources = {name: {key: array_identity(a) for key, a in arrays.items()}
                   for name, _, arrays in groups}
    for name, expected in prospective.items():
        if expected != {key: all_sources[name][key] for key in PRIMARY_KEYS}:
            raise ValueError('Primary source changed before derived write commitment')
    write_json(directory/'SOURCE_COMMITMENT.json', all_sources)
    for name, info, arrays in groups:
        records = dict(primary_records.get(name, {}))
        for key, a in arrays.items():
            if key not in records:
                records[key] = write_numeric(directory/f'{name}-{key}.npy', a, all_sources[name][key],
                                             {'archive_group': name, 'component': key, 'archive_role': 'trajectory', 'phase': 'derived'})
        if all_sources[name] != {key: array_identity(a) for key, a in arrays.items()}:
            raise ValueError('Source mutation across archive serialization')
        if name != 'geometry':
            _redundancy(model, arrays, {'archive_group': name, 'phase': 'source-after-write'})
            loaded = {key: np.load(directory/rec['file'], mmap_mode='r', allow_pickle=False)
                      for key, rec in records.items()}
            _redundancy(model, loaded, {'archive_group': name, 'phase': 'saved-readback'})
            if dense_chain(loaded) != info['dense_source_chain_sha256']:
                raise ValueError('Serialized dense capture chain mismatch')
            manifest['segments'].append({**info, 'arrays': records})
        else:
            manifest['geometry'] = {'arrays': records}
    manifest['source_commitment_sha256'] = sha256(directory/'SOURCE_COMMITMENT.json')
    if complete:
        if any(not seg['success'] or len(seg['t']) < 2 for seg in trajectory.segments):
            raise ValueError('Incomplete solver trajectory cannot publish success')
        write_json(directory/'validated-manifest.pending.json', manifest)
        os.link(directory/'validated-manifest.pending.json', directory/'manifest.json')
    else:
        manifest['status'] = 'INCOMPLETE_SOLVER_TRAJECTORY_NOT_QUALIFIED'
        write_json(directory/'INCOMPLETE_MANIFEST.json', manifest)
    sync_directory(directory)
    return manifest


def save_checkpoints(directory, model, results, metadata):
    """Accepted t/y only, before dense capture; commitments precede every write."""
    directory = Path(directory)
    directory.mkdir(exist_ok=False)
    expected = [{k: array_identity(getattr(result, k)) for k in ('t', 'y')}
                for _, result in results]
    write_json(directory/'SOURCE_COMMITMENT.json', expected)
    records = []
    for j, (moving, result) in enumerate(results):
        arrays = {k: write_numeric(directory/f'segment-{j}-{k}.npy', getattr(result, k), expected[j][k],
                                   {'archive_group': f'segment-{j}', 'component': k, 'archive_role': 'checkpoint'})
                  for k in ('t', 'y')}
        records.append({'moving': bool(moving), 'arrays': arrays})
    for j, (_, result) in enumerate(results):
        if expected[j] != {k: array_identity(getattr(result, k)) for k in ('t', 'y')}:
            raise ValueError('Accepted source changed across checkpoint writes')
    manifest = {'schema': 'grudeva-full-010-checkpoint-v1', 'metadata': metadata,
                'label': 'PROVISIONAL — NOT FULL_REFERENCE_QUALIFICATION',
                'case': asdict(model.case), 'settings': asdict(model.settings),
                'source_commitment_sha256': sha256(directory/'SOURCE_COMMITMENT.json'),
                'segments': records}
    write_json(directory/'checkpoint.json', manifest)
    sync_directory(directory)
    return manifest


def sync_directory(directory):
    descriptor = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def load_checkpoints(directory):
    """Diagnostic accepted states only; never admitted as a full trajectory."""
    directory = Path(directory)
    manifest = json.loads((directory/'checkpoint.json').read_text())
    if (manifest['schema'] != 'grudeva-full-010-checkpoint-v1'
            or sha256(directory/'SOURCE_COMMITMENT.json') != manifest['source_commitment_sha256']):
        raise ValueError('Checkpoint source identity mismatch')
    expected = json.loads((directory/'SOURCE_COMMITMENT.json').read_text())
    model = Model(Settings(**manifest['settings']), Case(**manifest['case']))
    segments = []
    if len(expected) != len(manifest['segments']):
        raise ValueError('Checkpoint segment count mismatch')
    for j, record in enumerate(manifest['segments']):
        if set(record['arrays']) != {'t', 'y'} or set(expected[j]) != {'t', 'y'}:
            raise ValueError('Checkpoint array set mismatch')
        arrays = {}
        for key, rec in record['arrays'].items():
            if rec['file'] != f'segment-{j}-{key}.npy':
                raise ValueError('Unsafe checkpoint member')
            path = directory/rec['file']
            if (rec['array'] != expected[j][key] or sha256(path) != rec['sha256']
                    or payload_identity(path) != rec['array']):
                raise ValueError('Checkpoint payload identity mismatch')
            arrays[key] = np.load(path, allow_pickle=False, mmap_mode='r')
            if array_identity(arrays[key]) != rec['array'] or not finite(arrays[key]):
                raise ValueError('Checkpoint loaded identity mismatch')
        t, y = arrays['t'], arrays['y']
        if (t.ndim != 1 or len(t) < 1 or y.shape != (model.n*model.width+2, len(t))
                or t.dtype != np.dtype('f8') or y.dtype != np.dtype('f8')
                or not np.all(np.diff(t) > 0)):
            raise ValueError('Invalid accepted checkpoint support')
        segments.append({**record, **arrays})
    return Trajectory(model, segments), manifest


def _load_v1(directory, manifest):
    model = Model(Settings(**manifest['settings']), Case(**manifest['case']))
    segments = []
    for record in [manifest['geometry'], *manifest['segments']]:
        name = record['file']
        if Path(name).name != name:
            raise ValueError('Unsafe archive path')
        path = directory/name
        if sha256(path) != record['sha256']:
            raise ValueError('Archive byte identity mismatch')
        with np.load(path, allow_pickle=False) as data:
            if set(data.files) != set(record['arrays']):
                raise ValueError('Archive array set mismatch')
            arrays = {}
            for key in data.files:
                a = data[key]
                if a.dtype.kind not in 'fiu' or array_identity(a) != record['arrays'][key]:
                    raise ValueError('Archive state identity mismatch')
                if not finite(a):
                    raise ValueError('Nonfinite archive state')
                arrays[key] = a
        if record is not manifest['geometry']:
            segments.append({**{k: v for k, v in record.items()
                                if k not in ('file', 'sha256', 'arrays')}, **arrays})
    return Trajectory(model, segments), manifest


def load_archive(directory):
    directory = Path(directory)
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest['schema'] == 'grudeva-full-010-v1':
        return _load_v1(directory, manifest)
    if manifest['schema'] != SCHEMA:
        raise ValueError('Unknown archive schema')
    if sha256(directory/'SOURCE_COMMITMENT.json') != manifest['source_commitment_sha256']:
        raise ValueError('Source commitment identity mismatch')
    commitments = json.loads((directory/'SOURCE_COMMITMENT.json').read_text())
    model = Model(Settings(**manifest['settings']), Case(**manifest['case']))
    segments = []
    for j, record in enumerate([manifest['geometry'], *manifest['segments']]):
        name = 'geometry' if j == 0 else f'segment-{j-1}'
        arrays = {}
        if set(record['arrays']) != set(commitments[name]):
            raise ValueError('Archive array set mismatch')
        for key, rec in record['arrays'].items():
            if Path(rec['file']).name != rec['file']:
                raise ValueError('Unsafe archive path')
            path = directory/rec['file']
            expected = commitments[name][key]
            if rec['array'] != expected or rec['order'] != 'C' or sha256(path) != rec['sha256']:
                raise ValueError('Archive source/file identity mismatch')
            if payload_identity(path) != expected:
                raise ValueError('Archive payload identity mismatch')
            a = np.load(path, allow_pickle=False, mmap_mode='r')
            if array_identity(a) != expected or not finite(a):
                raise ValueError('Archive loaded state identity mismatch')
            arrays[key] = a
        if j:
            if not record['success'] or len(arrays['t']) < 2:
                raise ValueError('Incomplete solver archive')
            if dense_chain(arrays) != record['dense_source_chain_sha256']:
                raise ValueError('Loaded dense capture chain mismatch')
            if record['capture_commitment'] != {key: commitments[name][key] for key in record['capture_commitment']}:
                raise ValueError('Captured/source commitment chain mismatch')
            _redundancy(model, arrays)
            segments.append({**{k: v for k, v in record.items() if k != 'arrays'}, **arrays})
        else:
            expected_geometry = {'xi_faces': model.faces, 'xi': model.xi}
            for label, sphere in zip(('fines', 'boulders'), model.spheres):
                expected_geometry.update({f'{label}_faces': sphere.faces, f'{label}_centers': sphere.r,
                                          f'{label}_volumes': sphere.volume})
            if set(arrays) != set(expected_geometry) or any(not _same_bits(arrays[k], v) for k, v in expected_geometry.items()):
                raise ValueError('Archive radial/axial geometry mismatch')
    return Trajectory(model, segments), manifest


def fv_weights(faces, points, left_zero=False, right_neumann=False):
    """Quadratic exact cell-average reconstruction on the physical support."""
    faces, points = np.asarray(faces), np.asarray(points)
    n = len(faces)-1
    weights = np.zeros((len(points), n))
    for i, x in enumerate(points):
        cell = min(n-1, max(0, np.searchsorted(faces, x)-1))
        center = (faces[cell]+faces[cell+1])/2
        scale = faces[cell+1]-faces[cell]
        if left_zero and cell == 0:
            indices = np.array([0, 1])
            a, b = (faces[indices]-faces[0])/scale, (faces[indices+1]-faces[0])/scale
            mat = np.array([(a+b)/2, (a*a+a*b+b*b)/3]).T
            u = (x-faces[0])/scale
            weights[i, indices] = np.linalg.solve(mat.T, [u, u*u])
        elif right_neumann and cell == n-1:
            indices = np.array([n-2, n-1])
            a, b = (faces[indices]-faces[-1])/scale, (faces[indices+1]-faces[-1])/scale
            mat = np.array([np.ones(2), (a*a+a*b+b*b)/3]).T
            u = (x-faces[-1])/scale
            weights[i, indices] = np.linalg.solve(mat.T, [1., u*u])
        else:
            indices = np.arange(max(0, min(n-3, cell-1)), max(0, min(n-3, cell-1))+3)
            a, b = (faces[indices]-center)/scale, (faces[indices+1]-center)/scale
            mat = np.array([np.ones(3), (a+b)/2, (a*a+a*b+b*b)/3]).T
            u = (x-center)/scale
            weights[i, indices] = np.linalg.solve(mat.T, [1., u, u*u])
    return weights


def radial_weights(sphere, points):
    """Quadratic in r², fitted to exact spherical shell averages."""
    faces, centers = sphere.faces, sphere.r
    weights = np.zeros((len(points), len(centers)))
    for j, r in enumerate(points):
        cell = np.searchsorted(centers, r)
        ids = np.arange(max(0, min(len(centers)-3, cell-1)),
                        max(0, min(len(centers)-3, cell-1))+3)
        a, b = faces[ids], faces[ids+1]
        # Center the r² basis to avoid cancellation near r=1 on graded meshes.
        origin, scale = centers[ids[1]]**2, b[-1]**2-a[0]**2
        nodes, gw = np.polynomial.legendre.leggauss(4)
        qr = ((a+b)[:, None]+(b-a)[:, None]*nodes)/2
        measure = (b-a)[:, None]/2 * gw * qr**2 / sphere.volume[ids, None]
        ucell = (qr**2-origin)/scale
        mat = np.array([np.ones(3), np.sum(measure*ucell, axis=1),
                        np.sum(measure*ucell**2, axis=1)]).T
        u = (r*r-origin)/scale
        weights[j, ids] = np.linalg.solve(mat.T, [1., u, u*u])
    return weights


def observe(trajectory, support):
    model = trajectory.model
    times, z, r = map(np.asarray, (support['times'], support['z'], support['r']))
    liquid = np.full((len(times), len(z)), np.nan)
    means = np.empty((len(times), len(z), 2))
    radial = np.empty((len(times), len(z), 2, len(r)))
    inventory, integrals, boundary = [], [], []
    wet = np.zeros_like(liquid, dtype=bool)
    outlet = np.full(len(times), np.nan)
    rw = [radial_weights(sphere, r) for sphere in model.spheres]
    for it, t in enumerate(times):
        y = trajectory.state(float(t))
        s=min(t,1.)
        state=model.split(y,t) if t>0 else None
        available = (z <= s) & (t > 0)
        wet[it] = available
        means[it] = model.case.initial
        radial[it] = model.case.initial
        if s > 0:
            wl = fv_weights(s*model.faces, z[available], True, True)
            wg = fv_weights(s*model.faces, z[available])
            liquid[it, available] = wl @ state[:, 0]
            flux, cout = liquid_flux(state[:, 0], s, t < 1, model.case.D_l)
            if t >= 1:
                outlet[it] = cout  # right-hand discharge limit at t=1
            boundary.append([flux[0], cout if t >= 1 else 0., cout, flux[-1]])
            for i, (sphere, sl) in enumerate(zip(model.spheres, model.slices)):
                grains = wg @ state[:, sl]
                means[it, available, i] = sphere.mean(grains)
                radial[it, available, i] = grains @ rw[i].T
                _, surface = sphere.transfer(grains, liquid[it, available])
                radial[it, :, i, -1][available] = surface
            # Exact newly wetted grain trace, distinct from every positive age.
            born = available & (z == t) & (t <= 1)
            means[it, born] = model.case.initial
            radial[it, born] = model.case.initial
        else:
            boundary.append([0., 0., 0., 0.])
        inventory.append(model.inventories(float(t), y))
        integrals.append(y[-2:])
    return {'times': times, 'z': z, 'r': r, 'liquid': liquid, 'wet': wet,
            'grain_means': means, 'grain_radial': radial, 'outlet': outlet,
            'inventories': np.array(inventory), 'integrals': np.array(integrals),
            'boundary_flux': np.array(boundary)}


def independent_inventories(model, t, y):
    """Independent Gaussian quadrature of actual piecewise-constant FV states."""
    if t==0:
        return np.array([0.,0.,0.,model.case.M0])
    state, s = model.split(y,t), min(t, 1.)
    x, w = np.polynomial.legendre.leggauss(2)
    axial_weight = np.diff(s * model.faces)
    amounts = [float(np.sum(axial_weight.astype(np.longdouble)*state[:, 0]))]
    for weight, sphere, sl in zip(model.case.weights, model.spheres, model.slices):
        a, b = sphere.faces[:-1], sphere.faces[1:]
        radii = ((a+b)[:, None]+(b-a)[:, None]*x)/2
        radial_weight = np.sum((b-a)[:, None]/2*w*radii**2, axis=1)*3
        total = np.sum(axial_weight.astype(np.longdouble)[:, None] *
                       state[:, sl] * radial_weight[None, :])
        amounts.append(float(weight * total))
    return np.r_[amounts, (1-s)*model.case.M0]


def boundary_quadrature(trajectory, order):
    x, w = np.polynomial.legendre.leggauss(order)
    model = trajectory.model
    tau=model.settings.startup
    initial=np.zeros(2)
    for point,weight in zip(tau*(x+1)/2,w):
        state=model.split(model.startup(point),point)
        initial[0]+=tau*weight/2*liquid_flux(state[:,0],point,True,model.case.D_l)[0][0]
    values = [initial.copy()]
    times = [model.settings.startup]
    total = initial.copy()
    for seg in trajectory.segments:
        for a, b in zip(seg['t'][:-1], seg['t'][1:]):
            value = np.zeros(2)
            for point, weight in zip((a+b)/2+(b-a)*x/2, w):
                state = model.split(trajectory.state(float(point)),point)
                s = point if seg['moving'] else 1.
                flux, cout = liquid_flux(state[:, 0], s, seg['moving'], model.case.D_l)
                value += weight * np.array([flux[0], 0 if seg['moving'] else cout])
            total += (b-a)/2*value
            values.append(total.copy())
            times.append(b)
    return np.array(times), np.array(values)
