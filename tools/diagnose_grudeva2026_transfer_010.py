#!/usr/bin/env python3
"""010 byte-transfer isolation. Standard library only; never admits a reference."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import struct
import subprocess
import sys
import time
import zipfile

CHUNK = 4 * 1024**2


def digest(data):
    return hashlib.sha256(data).hexdigest()


def stamp():
    return time.time_ns()


def put_json(path, value):
    with Path(path).open('x') as f:
        json.dump(value, f, indent=2, sort_keys=True, allow_nan=False)
        f.write('\n'); f.flush(); os.fsync(f.fileno())


def file_stat(path):
    s = Path(path).stat()
    return {k: getattr(s, k) for k in ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns')}


def header(data):
    """Bounded parser for this case's simple little-endian f8 C-order NPY.

    No eval/literal_eval, array loader, pickle or floating-point conversion.
    """
    if data[:8] != b'\x93NUMPY\x01\x00' or len(data) < 10:
        raise ValueError('Expected NPY version 1 header')
    n = struct.unpack('<H', data[8:10])[0]
    if n > 4096 or len(data) < 10+n:
        raise ValueError('Incomplete or oversized NPY header')
    raw = data[:10+n]
    m = re.fullmatch(rb"\{'descr': '<f8', 'fortran_order': False, 'shape': \(([0-9, ]+)\), \} *\n", raw[10:])
    if not m:
        raise ValueError('Unsupported NPY dtype/order/header; objects never accepted')
    shape = [int(x.strip()) for x in m[1].split(b',') if x.strip()]
    if not shape or len(shape) > 8:
        raise ValueError('Unsupported NPY shape')
    return {'header_bytes': len(raw), 'header_sha256': digest(raw), 'header_hex': raw.hex(),
            'dtype': '<f8', 'order': 'C', 'shape': shape, 'payload_bytes': 8*math.prod(shape)}


class Domains:
    def __init__(self):
        self.whole = hashlib.sha256(); self.payload = hashlib.sha256()
        self.n = 0; self.meta = None; self.prefix = bytearray()

    def update(self, block):
        self.whole.update(block)
        old = self.n; self.n += len(block)
        if self.meta is None:
            self.prefix.extend(block[:max(0, 4106-len(self.prefix))])
            if len(self.prefix) >= 10:
                size = 10+struct.unpack('<H', self.prefix[8:10])[0]
                if size > 4106:
                    raise ValueError('Oversized NPY header')
                if len(self.prefix) >= size:
                    self.meta = header(bytes(self.prefix))
                    # Earlier short reads may already contain payload bytes.
                    self.payload.update(self.prefix[size:min(old, len(self.prefix))])
        if self.meta is not None:
            self.payload.update(block[max(0, self.meta['header_bytes']-old):])

    def finish(self):
        if self.meta is None:
            raise ValueError('Truncated NPY header')
        return {**self.meta, 'member_bytes': self.n, 'member_sha256': self.whole.hexdigest(),
                'payload_sha256': self.payload.hexdigest(),
                'length_matches_header': self.n == self.meta['header_bytes']+self.meta['payload_bytes']}


class Evidence:
    def __init__(self, directory):
        self.path = Path(directory); self.path.mkdir(exist_ok=False)
        self.failures = []; self.secondary = []
        self.log = (self.path/'events.jsonl').open('x')

    def event(self, record):
        try:
            self.log.write(json.dumps({'time_ns': stamp(), **record}, sort_keys=True)+'\n')
            self.log.flush()
        except Exception as exc:
            self.secondary.append(f'event: {type(exc).__name__}: {exc}')
            print('UNPERSISTED_EVENT', json.dumps(record), file=sys.stderr, flush=True)

    def mismatch(self, stage, expected, observed, offset=None, prior=None, current=None):
        record = {'stage': stage, 'expected': expected, 'observed': observed,
                  'member_offset': offset, 'time_ns': stamp(),
                  'prior_bytes': ('pending secondary retained-block read' if callable(prior) else
                                  'supplied retained byte block' if prior is not None else
                                  'not available; digest alone is not prior bytes')}
        index = len(self.failures); self.failures.append(record)
        # Essential primary incident precedes any fallible witness enrichment.
        try:
            put_json(self.path/('FIRST_FAILURE.json' if index == 0 else f'failure-{index}.json'), record)
        except BaseException as exc:
            self.secondary.append(f'essential {index}: {type(exc).__name__}: {exc}')
            print('PRIMARY_TRANSFER_FAILURE', json.dumps(record), file=sys.stderr, flush=True)
        try:
            if callable(prior):
                prior = prior()
                record['prior_bytes'] = 'retained byte block read after primary incident persisted'
            if prior is not None and current is not None:
                for name, value in (('prior', prior), ('current', current)):
                    with (self.path/f'witness-{index}-{name}.bin').open('xb') as f:
                        f.write(value); f.flush(); os.fsync(f.fileno())
                count = 0; first = None
                with (self.path/f'witness-{index}-offsets.tsv').open('x') as f:
                    f.write('member_offset\tprior_byte\tcurrent_byte\n')
                    for k in range(max(len(prior), len(current))):
                        a = prior[k] if k < len(prior) else None
                        b = current[k] if k < len(current) else None
                        if a != b:
                            count += 1
                            if first is None: first = k
                            f.write(f'{(offset or 0)+k}\t{a}\t{b}\n')
                    f.flush(); os.fsync(f.fileno())
                record.update(differing_bytes=count, first_member_byte=None if first is None else (offset or 0)+first,
                              witness_kind='OBSERVED_BYTE_DIFFERENCE' if count else 'NO_CURRENT_BYTE_DIFFERENCE',
                              prior_sha256=digest(prior), current_sha256=digest(current))
                put_json(self.path/f'witness-{index}.json', record)
        except BaseException as exc:
            self.secondary.append(f'witness {index}: {type(exc).__name__}: {exc}')
        self.event({'failure_index': index, **record})

    def compare(self, stage, expected, observed, **witness):
        if expected != observed:
            self.mismatch(stage, expected, observed, **witness)
        return expected == observed

    def finish(self, detail):
        try:
            self.log.flush(); os.fsync(self.log.fileno()); self.log.close()
        except Exception as exc:
            self.secondary.append(f'event close: {type(exc).__name__}: {exc}')
        value = {'status': 'FAIL' if self.failures or self.secondary else 'PASS',
                 'failures': self.failures, 'secondary_errors': self.secondary,
                 'solver_calls': 0, 'numeric_library_imports': sorted(set(sys.modules)&{'numpy', 'scipy', 'puckworks'}),
                 **detail}
        try:
            put_json(self.path/'RESULT.json', value)
        except Exception as exc:
            self.secondary.append(f'result: {type(exc).__name__}: {exc}')
            value['status'] = 'FAIL'
            print('UNPERSISTED_RESULT', json.dumps(value), file=sys.stderr, flush=True)
        return value


def scan(path, chunk=CHUNK):
    domains = Domains()
    with Path(path).open('rb') as f:
        while block := f.read(chunk): domains.update(block)
    return domains.finish()


def check_domains(evidence, actual, expected, stage):
    for name, value in expected.items():
        evidence.compare(stage+':'+name, value, actual.get(name))
    evidence.compare(stage+':length_matches_header', True, actual['length_matches_header'])


def read_exact_at(fd, length, offset):
    out = bytearray()
    while len(out) < length:
        part = os.pread(fd, length-len(out), offset+len(out))
        if not part: break
        out.extend(part)
    return bytes(out)


def verify_pieces(target, spool, commitments, evidence, stage):
    domains = Domains(); count = 0
    with Path(target).open('rb') as dst, Path(spool).open('rb') as src:
        with Path(commitments).open() as records:
            for line in records:
                row = json.loads(line); offset, size = row['offset'], row['bytes']
                prior = src.read(size); current = dst.read(size)
                evidence.compare(stage+':retained_decoded_chunk', row['sha256'], digest(prior), offset=offset)
                evidence.compare(stage+':destination_chunk', row['sha256'], digest(current),
                                 offset=offset, prior=prior, current=current)
                domains.update(current); count += 1
        evidence.compare(stage+':trailing_destination_bytes', b''.hex(), dst.read(1).hex())
        evidence.compare(stage+':trailing_spool_bytes', b''.hex(), src.read(1).hex())
    return {'chunks': count, **domains.finish()}


def transfer(stream, destination, evidence, expected, chunk=CHUNK):
    """Actual shutil.copyfileobj call with read/write taps and retained raw chunks."""
    domains = Domains(); rows = 0; offset = 0; latest = None
    spool_path = evidence.path/'decoded-member.bin'; records_path = evidence.path/'prospective.jsonl'
    with spool_path.open('xb+') as spool, records_path.open('x') as records:
        class ReadTap:
            def read(self, n):
                nonlocal latest, rows
                before = stream.tell() if hasattr(stream, 'tell') else None
                block = stream.read(n)
                if not block: return block
                commitment = {'offset': offset, 'bytes': len(block), 'sha256': digest(block),
                              'time_ns': stamp(), 'read_requested': n, 'source_tell_before': before,
                              'source_tell_after': stream.tell() if hasattr(stream, 'tell') else None}
                records.write(json.dumps(commitment, sort_keys=True)+'\n'); records.flush()
                # Retain exact decoded bytes separately, with their own checked write.
                written = spool.write(block); spool.flush()
                evidence.compare('decoded_spool_write_count', len(block), written, offset=offset)
                stored = read_exact_at(spool.fileno(), len(block), offset)
                evidence.compare('decoded_spool_identity', commitment['sha256'], digest(stored),
                                 offset=offset, prior=block, current=stored)
                evidence.compare('decoded_buffer_after_retention', commitment['sha256'], digest(block),
                                 offset=offset, prior=stored, current=block)
                domains.update(block); latest = commitment; rows += 1
                return block

        class WriteTap:
            def write(self, block):
                nonlocal offset
                pre = digest(block)
                evidence.compare('pre_write_buffer', latest['sha256'], pre, offset=offset,
                                 prior=lambda: read_exact_at(spool.fileno(), len(block), offset), current=block)
                start = stamp(); logical_before = destination.tell(); fd_before = os.lseek(destination.fileno(), 0, os.SEEK_CUR)
                returned = destination.write(block)
                post = digest(block); ended = stamp()
                evidence.compare('write_return_count', len(block), returned, offset=offset)
                evidence.compare('post_write_buffer', pre, post, offset=offset,
                                 prior=lambda: read_exact_at(spool.fileno(), len(block), offset), current=block)
                logical_after = destination.tell(); fd_after = os.lseek(destination.fileno(), 0, os.SEEK_CUR)
                flush_return = destination.flush()
                with Path(destination.name).open('rb', buffering=0) as reader:
                    got = read_exact_at(reader.fileno(), len(block), offset)
                immediate = digest(got)
                evidence.compare('immediate_destination_after_flush', latest['sha256'], immediate,
                                 offset=offset, prior=block, current=got)
                evidence.event({'chunk': rows-1, 'offset': offset, 'requested': len(block), 'returned': returned,
                                'decoded': latest['sha256'], 'pre_write': pre, 'post_write_buffer': post,
                                'immediate_destination': immediate, 'write_start_ns': start, 'write_end_ns': ended,
                                'logical_before': logical_before, 'logical_after': logical_after,
                                'fd_before': fd_before, 'fd_after': fd_after, 'flush_return': flush_return,
                                'destination_fd': destination.fileno(), 'blocking': os.get_blocking(destination.fileno())})
                offset += len(block)
                if returned != len(block):
                    raise OSError('Short write observed; original copyfileobj ignores its return value')
                return returned

        shutil.copyfileobj(ReadTap(), WriteTap(), length=chunk)
        spool.flush(); records.flush(); os.fsync(spool.fileno()); os.fsync(records.fileno())
    source = domains.finish(); check_domains(evidence, source, expected, 'decoded_source')
    destination.flush()
    after_flush = verify_pieces(destination.name, spool_path, records_path, evidence, 'after_final_flush')
    sync_start = stamp(); sync_return = os.fsync(destination.fileno())
    after_sync = verify_pieces(destination.name, spool_path, records_path, evidence, 'after_fsync')
    return {'decoded': source, 'chunks': rows, 'after_flush': after_flush, 'after_fsync': after_sync,
            'ordered_prospective_records_sha256': digest(records_path.read_bytes()),
            'fsync': {'start_ns': sync_start, 'return': sync_return, 'end_ns': stamp()},
            'spool': str(spool_path), 'commitments': str(records_path)}


def command(argv, log):
    with Path(log).open('xb') as f:
        result = subprocess.run(argv, stdout=f, stderr=subprocess.STDOUT)
    return {'argv': argv, 'exit_code': result.returncode, 'log': Path(log).name}


def system_hash(path):
    p = subprocess.run(['/usr/bin/sha256sum', str(path)], capture_output=True, text=True)
    if p.returncode: raise OSError(p.stderr)
    return p.stdout.split()[0]


def fresh_check(target, spool, records, evidence):
    folder = evidence.path/'fresh-reader'
    p = subprocess.run([sys.executable, __file__, 'check', '--target', str(target), '--spool', str(spool),
                        '--records', str(records), '--output', str(folder)], capture_output=True, text=True)
    evidence.event({'stage': 'fresh_reader_exit', 'exit_code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr})
    evidence.compare('fresh_reader_exit', 0, p.returncode)
    return json.loads((folder/'RESULT.json').read_text()) if (folder/'RESULT.json').exists() else {'status': 'UNAVAILABLE'}


def row_a(inputs, plan, e):
    source = Path(inputs['source']); before = file_stat(source)
    expected = plan['source']; got = system_hash(source)
    e.compare('source_zip_file_admission', expected['zip_sha256'], got)
    if got != expected['zip_sha256']: return {'admission': 'FAILED'}
    target = e.path/'destination.npy'
    with zipfile.ZipFile(source) as archive, archive.open('D.npy') as src, target.open('xb') as dst:
        info = archive.getinfo('D.npy')
        for name, value in expected['zip_member'].items():
            e.compare('zip_member:'+name, value, getattr(info, name))
        if e.failures: return {'admission': 'FAILED'}
        e.event({'stage': 'descriptors', 'zip_fd': archive.fp.fileno(), 'zip_fd_offset': archive.fp.tell(),
                 'source_type': type(src).__name__, 'destination_type': type(dst).__name__,
                 'destination_stat': file_stat(target), 'destination_blocking': os.get_blocking(dst.fileno()),
                 'zip_member': expected['zip_member'], 'destination_mode': dst.mode,
                 'source_seekable': src.seekable(), 'source_readable': src.readable()})
        result = transfer(src, dst, e, expected['domains'])
        result['zip_crc_at_eof'] = {'actual': src._running_crc, 'expected': src._expected_crc, 'eof': src._eof}
        e.compare('ZIP_CRC', src._expected_crc, src._running_crc)
        e.compare('ZIP_EOF', True, src._eof)
    e.event({'stage': 'destination_close', 'status': 'returned normally', 'time_ns': stamp()})
    result['fresh_reader'] = fresh_check(target, result['spool'], result['commitments'], e)
    result['source_stat_before'] = before; result['source_stat_after'] = file_stat(source)
    e.compare('source_stat_stability', before, file_stat(source))
    return result


def row_b(inputs, plan, e):
    source = Path(inputs['opaque_bad_fixture']); before = file_stat(source)
    prior = scan(source); check_domains(e, prior, plan['opaque']['domains'], 'opaque_source_admission')
    if e.failures: return {'admission': 'FAILED'}
    target = e.path/'opaque-copy.npy'
    argv = ['/usr/bin/strace', '-c', '-e', 'trace=read,write,copy_file_range,sendfile,fsync,fdatasync,ioctl',
            '-o', str(e.path/'dd-syscalls.txt'), '/usr/bin/dd', f'if={source}', f'of={target}',
            f'bs={CHUNK}', 'iflag=fullblock', 'conv=excl,fsync']
    process = command(argv, e.path/'dd.log'); e.compare('dd_exit', 0, process['exit_code'])
    child = subprocess.run([sys.executable, __file__, 'pair', '--target', str(target), '--spool', str(source),
                            '--output', str(e.path/'fresh-reader')], capture_output=True, text=True)
    e.compare('fresh_reader_exit', 0, child.returncode)
    e.event({'stage': 'fresh_reader_exit', 'exit_code': child.returncode, 'stderr': child.stderr, 'stdout': child.stdout})
    result = json.loads((e.path/'fresh-reader/RESULT.json').read_text())
    if 'source' not in result:
        return {'role': 'OPAQUE_BYTE_FIXTURE_NOT_SCIENTIFIC_RECOVERY', 'dd': process,
                'fresh_reader': result, 'source_before': prior, 'after_copy_identity': 'UNAVAILABLE'}
    e.compare('opaque_source_payload_stability', prior['payload_sha256'], result['source']['payload_sha256'])
    e.compare('opaque_source_whole_stability', prior['member_sha256'], result['source']['member_sha256'])
    e.compare('source_stat_stability', before, file_stat(source))
    return {'role': 'OPAQUE_BYTE_FIXTURE_NOT_SCIENTIFIC_RECOVERY', 'source_before': prior,
            'dd': process, 'fresh_reader': result, 'source_stat_before': before, 'source_stat_after': file_stat(source)}


def row_c(inputs, plan, e):
    source = Path(inputs['source']); before = file_stat(source)
    # An optional, already checked A spool localizes stream differences. It is
    # a diagnostic comparison input, never a replacement for the original SHA.
    spool_path = e.path.parent/'A/decoded-member.bin'
    spool_receipt = e.path.parent/'A/RESULT.json'
    contrast = None
    contrast_domains = Domains()
    if spool_receipt.exists():
        receipt = json.loads(spool_receipt.read_text())
        if (receipt.get('status') == 'PASS' and receipt.get('fresh_reader', {}).get('status') == 'PASS'
                and receipt.get('decoded', {}).get('payload_sha256') == plan['source']['domains']['payload_sha256']):
            contrast = spool_path.open('rb')
    e.event({'stage': 'C_chunk_contrast', 'available': contrast is not None,
             'receipt_sha256': digest(spool_receipt.read_bytes()) if spool_receipt.exists() else None})
    with (e.path/'unzip.stderr').open('xb') as log:
        unzip = subprocess.Popen(['/usr/bin/unzip', '-p', str(source), 'D.npy'], stdout=subprocess.PIPE, stderr=log)
        whole = subprocess.Popen(['/usr/bin/sha256sum'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        payload = subprocess.Popen(['/usr/bin/sha256sum'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        domains = Domains(); count = 0
        try:
            while block := unzip.stdout.read(CHUNK):
                old = domains.n; domains.update(block); count += 1
                if contrast is not None:
                    prior = contrast.read(len(block))
                    contrast_domains.update(prior)
                    e.compare('independent_decode_vs_checked_A_spool', digest(prior), digest(block),
                              offset=old, prior=prior, current=block)
                whole.stdin.write(block)
                payload.stdin.write(block[max(0, domains.meta['header_bytes']-old):])
            whole.stdin.close(); payload.stdin.close()
            whole_hash = whole.stdout.read().decode().split()[0]
            payload_hash = payload.stdout.read().decode().split()[0]
            exits = {'unzip': unzip.wait(), 'whole_sha256sum': whole.wait(), 'payload_sha256sum': payload.wait()}
            if contrast is not None:
                e.compare('C_spool_trailing_bytes', '', contrast.read(1).hex())
                check_domains(e, contrast_domains.finish(), plan['source']['domains'], 'C_spool_identity_reverified')
        finally:
            if contrast is not None: contrast.close()
            for process in (unzip, whole, payload):
                if process.poll() is None: process.kill(); process.wait()
            e.event({'stage': 'independent_process_exits', 'unzip': unzip.returncode,
                     'whole_sha256sum': whole.returncode, 'payload_sha256sum': payload.returncode})
        actual = domains.finish(); check_domains(e, actual, plan['source']['domains'], 'independent_decoded_source')
        e.compare('independent_whole_hasher', actual['member_sha256'], whole_hash)
        e.compare('independent_payload_hasher', plan['source']['domains']['payload_sha256'], payload_hash)
        for name, code in exits.items(): e.compare(name+'_exit', 0, code)
    final_zip = system_hash(source)
    e.compare('source_zip_file_after_independent_decode', plan['source']['zip_sha256'], final_zip)
    e.compare('source_stat_stability', before, file_stat(source))
    return {'decoded': actual, 'GNU_whole_sha256': whole_hash, 'GNU_payload_sha256': payload_hash,
            'exits': exits, 'chunks': count, 'source_zip_sha256_after': final_zip,
            'source_stat_before': before, 'source_stat_after': file_stat(source)}


def pair(source, target, e):
    a, b = Domains(), Domains(); offset = 0
    with Path(source).open('rb') as src, Path(target).open('rb') as dst:
        while True:
            prior, current = src.read(CHUNK), dst.read(CHUNK)
            if not prior and not current: break
            e.compare('plain_file_bytes', digest(prior), digest(current), offset=offset, prior=prior, current=current)
            a.update(prior); b.update(current); offset += max(len(prior), len(current))
    return {'source': a.finish(), 'destination': b.finish()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('row', choices=['A', 'B', 'C', 'check', 'pair'])
    for name in ('plan', 'inputs', 'output', 'target', 'spool', 'records'):
        p.add_argument('--'+name, type=Path, required=name == 'output')
    args = p.parse_args(); e = Evidence(args.output); start = stamp()
    try:
        if args.row == 'check':
            result = verify_pieces(args.target, args.spool, args.records, e, 'independently_reopened')
        elif args.row == 'pair': result = pair(args.spool, args.target, e)
        else:
            plan = json.loads(args.plan.read_text()); inputs = json.loads(args.inputs.read_text())
            for path, expected in plan['executables'].items():
                if digest(Path(path).read_bytes()) != expected: raise ValueError('Executable identity changed: '+path)
            if digest(Path(__file__).read_bytes()) != plan['command_sha256']: raise ValueError('Diagnostic command changed')
            if digest(args.inputs.read_bytes()) != plan['private_inputs_sha256']: raise ValueError('Input binding changed')
            if sys.version != plan['environment']['python'] or platform.platform() != plan['environment']['platform']:
                raise ValueError('Environment identity changed')
            if file_stat(args.output)['st_dev'] != plan['environment']['destination_st_dev']:
                raise ValueError('Destination device changed')
            for key in ('source', 'opaque_bad_fixture'):
                if file_stat(inputs[key]) != plan['input_stats'][key]: raise ValueError('Input metadata changed: '+key)
            e.event({'stage': 'START', 'row': args.row, 'plan_sha256': digest(args.plan.read_bytes()),
                     'python': sys.version, 'pid': os.getpid(), 'destination_stat': file_stat(args.output)})
            result = {'A': row_a, 'B': row_b, 'C': row_c}[args.row](inputs, plan, e)
        value = e.finish({'row': args.row, 'started_ns': start, 'ended_ns': stamp(), **result})
    except BaseException as exc:
        e.mismatch('exception', 'normal completion', f'{type(exc).__name__}: {exc}')
        value = e.finish({'row': args.row, 'started_ns': start, 'ended_ns': stamp(), 'incomplete': True})
    print(json.dumps({'row': args.row, 'status': value['status'], 'failure_count': len(e.failures)}), flush=True)
    return 0 if value['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
