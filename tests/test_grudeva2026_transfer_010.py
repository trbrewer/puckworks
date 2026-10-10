"""Opaque byte fixtures only: no solver, arrays, or retained evidence mutations."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import platform
import shutil
import struct
import subprocess
import sys
import zipfile

import pytest

COMMAND = Path(__file__).resolve().parents[1]/'tools/diagnose_grudeva2026_transfer_010.py'
SPEC = importlib.util.spec_from_file_location('transfer_010', COMMAND)
d = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(d)


def fixture():
    # Nontrivial bytes plus both signed-zero encodings, without float conversion.
    payload = bytes(range(256))*4 + bytes.fromhex('00000000000000000000000000000080')
    text = b"{'descr': '<f8', 'fortran_order': False, 'shape': (130,), }"
    text += b' '*(117-len(text))+b'\n'
    return b'\x93NUMPY\x01\x00'+struct.pack('<H', len(text))+text+payload


def expected(raw):
    return {'payload_sha256': hashlib.sha256(raw[128:]).hexdigest(),
            'member_sha256': hashlib.sha256(raw).hexdigest(), 'member_bytes': len(raw)}


@pytest.mark.parametrize('chunk', [1, 7, 127, 128, 129, 511, 4096])
def test_independent_hash_domains_and_short_reads(chunk):
    raw = fixture(); domains = d.Domains()
    for offset in range(0, len(raw), chunk): domains.update(raw[offset:offset+chunk])
    result = domains.finish()
    assert all(result[k] == v for k, v in expected(raw).items())
    assert result['length_matches_header'] and result['header_bytes'] == 128


@pytest.mark.parametrize('bad', [b'garbage', fixture().replace(b"'<f8'", b"'|O8'"),
                                fixture().replace(b'False', b'True '), fixture()[:20]])
def test_parser_rejects_unsafe_or_incomplete(bad):
    with pytest.raises(ValueError): d.header(bad)


@pytest.mark.parametrize('chunk', [7, 256, 4096])
def test_valid_transfer_and_fresh_process(tmp_path, chunk):
    raw = fixture(); e = d.Evidence(tmp_path/'record'); target = tmp_path/'target.npy'
    with target.open('xb') as dst:
        result = d.transfer(io.BytesIO(raw), dst, e, expected(raw), chunk)
    fresh = d.fresh_check(target, result['spool'], result['commitments'], e)
    assert fresh['status'] == 'PASS' and fresh['numeric_library_imports'] == []
    assert target.read_bytes() == raw == Path(result['spool']).read_bytes()
    assert not e.failures
    assert d.Evidence.finish(e, result)['status'] == 'PASS'


class Destination:
    def __init__(self, file, mode): self.file = file; self.mode = mode; self.once = True
    def __getattr__(self, name): return getattr(self.file, name)
    def write(self, block):
        if self.mode == 'short': return self.file.write(block[:-1])
        result = self.file.write(block)
        if self.mode == 'post_buffer' and self.once:
            block[-1] ^= 1; self.once = False
        if self.mode == 'destination' and self.once:
            self.file.flush()
            with Path(self.file.name).open('r+b') as f:
                f.seek(len(block)-1); f.write(bytes([block[-1] ^ 1]))
            self.once = False
        return result


@pytest.mark.parametrize('mode,stage', [('short','write_return_count'),
                                     ('post_buffer','post_write_buffer'),
                                     ('destination','immediate_destination_after_flush')])
def test_write_boundaries_and_complete_witness(tmp_path, mode, stage):
    class Mutable(io.BytesIO):
        def read(self, n): return bytearray(super().read(n))
    raw = fixture(); e = d.Evidence(tmp_path/'record')
    with (tmp_path/'target.npy').open('xb') as dst:
        if mode == 'short':
            with pytest.raises(OSError, match='Short write'):
                d.transfer(Mutable(raw), Destination(dst, mode), e, expected(raw), 256)
        else: d.transfer(Mutable(raw), Destination(dst, mode), e, expected(raw), 256)
    assert stage in [f['stage'] for f in e.failures]
    assert (e.path/'FIRST_FAILURE.json').exists()
    assert e.finish({})['status'] == 'FAIL'
    for path in e.path.glob('witness-*.json'):
        i = path.stem.split('-')[1]; record = json.loads(path.read_text())
        a = (e.path/f'witness-{i}-prior.bin').read_bytes()
        b = (e.path/f'witness-{i}-current.bin').read_bytes()
        assert record['differing_bytes'] == sum(x != y for x,y in zip(a,b))+abs(len(a)-len(b))


def test_source_change_between_read_and_write(tmp_path, monkeypatch):
    def corrupt_copy(src, dst, length):
        while block := src.read(length):
            changed = bytearray(block); changed[-1] ^= 1; dst.write(changed)
    monkeypatch.setattr(d.shutil, 'copyfileobj', corrupt_copy)
    e = d.Evidence(tmp_path/'record'); raw = fixture()
    with (tmp_path/'target.npy').open('xb') as dst:
        d.transfer(io.BytesIO(raw), dst, e, expected(raw), 256)
    assert e.failures[0]['stage'] == 'pre_write_buffer'
    assert e.failures[0]['differing_bytes'] == 1
    e.finish({})


def test_known_mismatch_survives_secondary_spool_read_failure(tmp_path, monkeypatch):
    original = d.read_exact_at
    calls = 0
    def fail_secondary(*args):
        nonlocal calls
        calls += 1
        if calls == 2: raise OSError('injected secondary witness read failure')
        return original(*args)
    def corrupt_copy(src, dst, length):
        while block := src.read(length):
            changed = bytearray(block); changed[-1] ^= 1; dst.write(changed)
    monkeypatch.setattr(d, 'read_exact_at', fail_secondary)
    monkeypatch.setattr(d.shutil, 'copyfileobj', corrupt_copy)
    e = d.Evidence(tmp_path/'record'); raw = fixture()
    with (tmp_path/'target.npy').open('xb') as dst:
        d.transfer(io.BytesIO(raw), dst, e, expected(raw), 256)
    primary = json.loads((e.path/'FIRST_FAILURE.json').read_text())
    assert primary['stage'] == 'pre_write_buffer' and primary['expected'] != primary['observed']
    assert 'differing_bytes' not in primary
    assert any('secondary witness read' in x for x in e.secondary)
    assert e.finish({})['status'] == 'FAIL'


def test_multiple_appended_chunks_have_distinct_correct_offsets(tmp_path, monkeypatch):
    monkeypatch.setattr(d, 'CHUNK', 128)
    source, target = tmp_path/'source.npy', tmp_path/'target.npy'
    raw = fixture(); source.write_bytes(raw); target.write_bytes(raw+b'!'*400)
    e = d.Evidence(tmp_path/'record'); d.pair(source, target, e)
    offsets = []
    for f in e.path.glob('witness-*-offsets.tsv'):
        offsets += [int(line.split('\t')[0]) for line in f.read_text().splitlines()[1:]]
    assert sorted(offsets) == list(range(len(raw), len(raw)+400))
    assert e.finish({})['status'] == 'FAIL'


@pytest.mark.parametrize('mode', ['truncation', 'stale_expected', 'changed_source'])
def test_source_admission_failures(tmp_path, mode):
    raw = fixture(); supplied = raw; wanted = expected(raw)
    if mode == 'truncation': supplied = raw[:-8]
    if mode == 'stale_expected': wanted['payload_sha256'] = '0'*64
    if mode == 'changed_source': supplied = raw[:-1]+bytes([raw[-1]^1])
    e = d.Evidence(tmp_path/'record')
    with (tmp_path/'target.npy').open('xb') as dst:
        d.transfer(io.BytesIO(supplied), dst, e, wanted, 256)
    assert any(x['stage'].startswith('decoded_source:') for x in e.failures)
    if mode == 'truncation': assert any('length_matches_header' in x['stage'] for x in e.failures)
    assert e.finish({})['status'] == 'FAIL'


def test_destination_changed_after_close_fresh_process_exact_offsets(tmp_path):
    raw = fixture(); e = d.Evidence(tmp_path/'record'); target = tmp_path/'target.npy'
    with target.open('xb') as dst: result = d.transfer(io.BytesIO(raw), dst, e, expected(raw), 256)
    changed = bytearray(raw)
    for i in (145, 146, 1000): changed[i] ^= 1
    target.write_bytes(changed)
    fresh = d.fresh_check(target, result['spool'], result['commitments'], e)
    assert fresh['status'] == 'FAIL'
    witnesses = list((e.path/'fresh-reader').glob('witness-*.json'))
    assert sum(json.loads(p.read_text())['differing_bytes'] for p in witnesses) == 3
    # A separate interpreter re-reads actual retained blocks and independently reproduces offsets.
    script = """import json, pathlib, sys
p=pathlib.Path(sys.argv[1]); offsets=[]
for f in p.glob('witness-*.json'):
 r=json.loads(f.read_text()); i=f.stem.split('-')[1]
 a=(p/f'witness-{i}-prior.bin').read_bytes(); b=(p/f'witness-{i}-current.bin').read_bytes()
 offsets += [r['member_offset']+k for k,(x,y) in enumerate(zip(a,b)) if x!=y]
assert sorted(offsets)==[145,146,1000], offsets
"""
    p = subprocess.run([sys.executable, '-c', script, str(e.path/'fresh-reader')], capture_output=True)
    assert p.returncode == 0, p.stderr
    assert e.finish({})['status'] == 'FAIL'


@pytest.mark.parametrize('stage', ['essential', 'witness', 'event', 'result'])
def test_secondary_evidence_failure_preserves_primary(tmp_path, monkeypatch, capsys, stage):
    e = d.Evidence(tmp_path/'record'); original = d.put_json
    def fail(path, value):
        if (stage == 'essential' and path.name == 'FIRST_FAILURE.json' or
            stage == 'witness' and path.name.startswith('witness-') or
            stage == 'result' and path.name == 'RESULT.json'):
            raise OSError('deliberate evidence fixture failure')
        original(path, value)
    monkeypatch.setattr(d, 'put_json', fail)
    if stage == 'event': e.log.close()
    e.mismatch('fixture_boundary', 'expected', 'observed', offset=7, prior=b'ab', current=b'aB')
    result = e.finish({})
    assert result['status'] == 'FAIL' and result['secondary_errors']
    assert result['failures'][0]['stage'] == 'fixture_boundary'
    if stage != 'essential': assert json.loads((e.path/'FIRST_FAILURE.json').read_text())['stage'] == 'fixture_boundary'
    else: assert 'PRIMARY_TRANSFER_FAILURE' in capsys.readouterr().err


def test_truncated_fresh_process_failure_record(tmp_path):
    source, target = tmp_path/'source.npy', tmp_path/'target.npy'
    source.write_bytes(fixture()); target.write_bytes(fixture()[:-17])
    process = subprocess.run([sys.executable, str(COMMAND), 'pair', '--spool', str(source),
                              '--target', str(target), '--output', str(tmp_path/'record')], capture_output=True)
    assert process.returncode == 1
    result = json.loads((tmp_path/'record/RESULT.json').read_text())
    assert result['failures'][0]['stage'] == 'plain_file_bytes'
    assert result['failures'][0]['differing_bytes'] == 17
    assert not result['destination']['length_matches_header']


@pytest.mark.parametrize('row', ['A', 'B', 'C'])
def test_actual_command_rows_on_opaque_fixture(tmp_path, row):
    needed = ['sha256sum'] + (['dd', 'strace'] if row == 'B' else ['unzip'] if row == 'C' else [])
    if any(shutil.which(name) != '/usr/bin/'+name for name in needed):
        pytest.skip('Bound system diagnostic tools unavailable on this QA platform')
    raw = fixture(); source = tmp_path/'source.zip'; opaque = tmp_path/'opaque.npy'
    with zipfile.ZipFile(source, 'x', compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr('D.npy', raw)
    opaque.write_bytes(raw)
    inputs = {'source': str(source), 'opaque_bad_fixture': str(opaque)}
    d.put_json(tmp_path/'inputs.json', inputs)
    plan = {'executables': {}, 'command_sha256': hashlib.sha256(COMMAND.read_bytes()).hexdigest(),
            'private_inputs_sha256': hashlib.sha256((tmp_path/'inputs.json').read_bytes()).hexdigest(),
            'environment': {'python': sys.version, 'platform': platform.platform(),
                            'destination_st_dev': tmp_path.stat().st_dev},
            'input_stats': {k: d.file_stat(v) for k,v in inputs.items()},
            'source': {'zip_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                       'zip_member': {'file_size': len(raw)}, 'domains': expected(raw)},
            'opaque': {'domains': expected(raw)}}
    d.put_json(tmp_path/'plan.json', plan)
    process = subprocess.run([sys.executable, str(COMMAND), row, '--plan', str(tmp_path/'plan.json'),
                              '--inputs', str(tmp_path/'inputs.json'), '--output', str(tmp_path/'record')],
                             capture_output=True)
    assert process.returncode == 0, (process.stdout, process.stderr)
    result = json.loads((tmp_path/'record/RESULT.json').read_text())
    assert result['status'] == 'PASS' and result['numeric_library_imports'] == []
    if row == 'C': assert result['exits'] == {'unzip': 0, 'whole_sha256sum': 0, 'payload_sha256sum': 0}


def test_independent_stream_mismatch_keeps_all_changed_offsets(tmp_path):
    if any(shutil.which(n) != '/usr/bin/'+n for n in ['sha256sum','unzip']):
        pytest.skip('Bound independent decoder unavailable')
    raw = fixture(); changed = bytearray(raw)
    for i in [145, 310, 1100]: changed[i] ^= 1
    source = tmp_path/'changed-fixture.zip'
    with zipfile.ZipFile(source, 'x', compression=zipfile.ZIP_DEFLATED) as z: z.writestr('D.npy', changed)
    a = tmp_path/'A'; a.mkdir(); (a/'decoded-member.bin').write_bytes(raw)
    d.put_json(a/'RESULT.json', {'status':'PASS','fresh_reader':{'status':'PASS'},'decoded':expected(raw)})
    e = d.Evidence(tmp_path/'C')
    result = d.row_c({'source':str(source)}, {'source':{'domains':expected(raw),
                      'zip_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}}, e)
    assert result['exits'] == {'unzip':0,'whole_sha256sum':0,'payload_sha256sum':0}
    failure = e.failures[0]
    assert failure['stage'] == 'independent_decode_vs_checked_A_spool' and failure['differing_bytes'] == 3
    assert [int(x.split('\t')[0]) for x in (e.path/'witness-0-offsets.tsv').read_text().splitlines()[1:]] == [145,310,1100]
    assert e.finish({})['status'] == 'FAIL'
