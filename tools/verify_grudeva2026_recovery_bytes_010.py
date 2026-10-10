#!/usr/bin/env python3
"""010 exact-content byte verification only; no scientific environment imports.

Invoke with the identified interpreter's -I -S -X faulthandler flags. Reuses
the frozen transfer checker's evidence writer; its bounded NPY parser is
adapted only for the additional |i1 dtype. Never admits a scientific archive.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import sys
import types

CHUNK = 4 * 1024**2
HELPER_SHA256 = 'f233c54193f9c1308948d16d82af2488a36258e43ec47df1f5d537c428ead507'
HELPER = Path(__file__).with_name('diagnose_grudeva2026_transfer_010.py')
_source = HELPER.read_bytes()
if hashlib.sha256(_source).hexdigest() != HELPER_SHA256:
    raise ValueError('Frozen standard-library evidence helper identity mismatch')
helper = types.ModuleType('reviewed_transfer_byte_utilities_010')
helper.__file__ = str(HELPER)
exec(compile(_source, str(HELPER), 'exec'), helper.__dict__)


def file_hash(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        while block := stream.read(CHUNK):
            result.update(block)
    return result.hexdigest()


def header(data):
    """Same strict NPY-v1/C-order grammar as the frozen checker, plus |i1."""
    if data[:8] != b'\x93NUMPY\x01\x00' or len(data) < 10:
        raise ValueError('Expected NPY version 1 header')
    n = struct.unpack('<H', data[8:10])[0]
    if n > 4096 or len(data) < 10+n:
        raise ValueError('Incomplete or oversized NPY header')
    raw = data[:10+n]
    match = re.fullmatch(
        rb"\{'descr': '(<f8|\|i1)', 'fortran_order': False, 'shape': \(([0-9]+,|[0-9]+(?:, [0-9]+)+,?)\), \} *\n",
        raw[10:])
    if not match:
        raise ValueError('Unsupported NPY dtype/order/header; objects never accepted')
    shape = [int(x.strip()) for x in match[2].split(b',') if x.strip()]
    if not shape or len(shape) > 8:
        raise ValueError('Unsupported NPY shape')
    dtype = match[1].decode('ascii')
    return {'header_bytes': len(raw), 'header_sha256': helper.digest(raw),
            'header_hex': raw.hex(), 'dtype': dtype, 'order': 'C', 'shape': shape,
            'payload_bytes': (8 if dtype == '<f8' else 1)*math.prod(shape)}


def scan(path):
    """One bounded read, keeping complete-file and numeric-payload hashes apart."""
    whole, payload = hashlib.sha256(), hashlib.sha256()
    before = helper.file_stat(path)
    with Path(path).open('rb') as stream:
        prefix = stream.read(10)
        if len(prefix) != 10:
            raise ValueError('Truncated NPY prefix')
        length = struct.unpack('<H', prefix[8:10])[0]
        if length > 4096:
            raise ValueError('Oversized NPY header')
        raw = prefix+stream.read(length)
        meta = header(raw)
        whole.update(raw)
        size = len(raw)
        while block := stream.read(CHUNK):
            whole.update(block)
            payload.update(block)
            size += len(block)
    return {**meta, 'member_bytes': size, 'member_sha256': whole.hexdigest(),
            'payload_sha256': payload.hexdigest(),
            'length_matches_header': size == meta['header_bytes']+meta['payload_bytes'],
            'before': before, 'after': helper.file_stat(path),
            'links': Path(path).stat().st_nlink}


def verify_member(evidence, row, index):
    """Persist expected/observed identities before reporting failure; never retry."""
    path = Path(row['source'])
    try:
        actual = scan(path)
    except Exception as error:
        evidence.mismatch(str(path)+':read', row, {'error': type(error).__name__, 'message': str(error)})
        return False
    observed = {'dtype': actual['dtype'], 'shape': actual['shape'], 'sha256': actual['payload_sha256']}
    checks = {'numeric_identity': observed == row['expected'],
              'C_order': actual['order'] == 'C',
              'payload_length': actual['length_matches_header'],
              'stable_source': actual['before'] == actual['after']}
    if 'file_sha256' in row:
        checks['complete_file_identity'] = row['file_sha256'] == actual['member_sha256']
    record = {'member': row, 'observed': actual, 'checks': checks,
              'complete_file_identity': ('PASS' if checks['complete_file_identity'] else 'FAIL')
              if 'file_sha256' in row else 'NOT_BOUND',
              'status': 'PASS_BYTES_ONLY' if all(checks.values()) else 'FAIL',
              'finiteness': 'NOT_EVALUATED_BY_BYTE_CHECKER'}
    if not all(checks.values()):
        # Existing utility saves FIRST_FAILURE before any optional enrichment.
        evidence.mismatch(str(path)+':byte_admission', row, record)
    helper.put_json(evidence.path/f'member-{index:02d}.json', record)
    print(record['status'], row['group'], row['member'], flush=True)
    return all(checks.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    evidence = helper.Evidence(args.output)
    plan_bytes = args.plan.read_bytes()
    detail = {'scope': 'BYTE_VERIFICATION_ONLY_NOT_SCIENTIFIC_ADMISSION',
              'command': [sys.executable, *sys.orig_argv[1:]], 'python': sys.version,
              'executable': sys.executable, 'resolved_executable': str(Path(sys.executable).resolve()),
              'executable_sha256': file_hash(sys.executable),
              'checker_sha256': file_hash(__file__), 'helper_sha256': HELPER_SHA256,
              'plan_sha256': helper.digest(plan_bytes), 'pid': os.getpid(),
              'isolated': sys.flags.isolated, 'no_site': sys.flags.no_site,
              'faulthandler': sys._xoptions.get('faulthandler', False), 'members_verified': 0}
    try:
        if not (sys.flags.isolated and sys.flags.no_site and 'faulthandler' in sys._xoptions):
            raise ValueError('Required -I -S -X faulthandler invocation missing')
        plan = json.loads(plan_bytes)
        for key in ('executable_sha256', 'checker_sha256', 'helper_sha256', 'python'):
            if detail[key] != plan[key]:
                raise ValueError('Execution identity mismatch: '+key)
        for record in plan['records']:
            if file_hash(record['path']) != record['sha256']:
                raise ValueError('Bound record changed: '+record['path'])
        records = {record['path']: record['sha256'] for record in plan['records']}
        if plan['source_commitment'] not in records:
            raise ValueError('Original source commitment must be a bound record')
        original_bytes = Path(plan['source_commitment']).read_bytes()
        if helper.digest(original_bytes) != records[plan['source_commitment']]:
            raise ValueError('Original source commitment changed before parsing')
        original = json.loads(original_bytes)
        helper.put_json(evidence.path/'START.json', detail)
        for index, row in enumerate(plan['members']):
            if row['expected'] != original[row['group']][row['member']]:
                raise ValueError('Expected identity differs from original commitment')
            if not verify_member(evidence, row, index):
                break
            detail['members_verified'] += 1
        for record in plan['records']:
            if file_hash(record['path']) != record['sha256']:
                raise ValueError('Bound record changed after scan: '+record['path'])
        if file_hash(args.plan) != detail['plan_sha256']:
            raise ValueError('Plan changed after parsing')
        if detail['members_verified'] != len(plan['members']) and not evidence.failures:
            raise ValueError('Incomplete member verification')
    except Exception as error:
        evidence.mismatch('byte_verification_exception', 'successful bounded byte verification',
                          {'type': type(error).__name__, 'message': str(error)})
    detail['forbidden_imports'] = sorted(set(sys.modules) & {
        'numpy', 'scipy', 'puckworks', 'importlib.metadata',
        'tools.run_grudeva2026_full_reference_010'})
    if detail['forbidden_imports']:
        evidence.mismatch('forbidden_imports', [], detail['forbidden_imports'])
    return 0 if evidence.finish(detail)['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
