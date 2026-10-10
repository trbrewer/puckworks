"""Bounded 010 recovered-anchor admission and direct runtime verification.

Standard-library imports only. The scientific runner supplies its existing
bundle validator; this module never integrates or recomputes anchor audits.
"""
import base64
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

AUTHORIZATION = 'OWNER AUTHORIZATION — COMPLETE THE REMAINING 010 QUALIFICATION'
MATRIX_SHA256 = '092269b20b88d413abbfb1350240d32ab869e985cf1825ef1f28f73462e667d3'
DOC = 'docs/analysis/model_grudeva2026_full_reference_010'


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        while block := stream.read(4*1024**2):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def metadata_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def checked(record):
    raw = Path(record['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != record['sha256']:
        raise ValueError('Bound recovery record changed: '+record['path'])
    return json.loads(raw)


def verify_runtime(root, binding):
    """Current bytes via two explicit RECORD paths, never package discovery."""
    spec = binding['runtime']
    if (sys.version != binding['environment']['python']
            or Path(sys.executable).resolve() != Path(spec['python']).resolve()
            or digest(sys.executable) != binding['executable']['python_sha256']):
        raise ValueError('Current interpreter identity differs from binding')
    installed, record_hashes = {}, {}
    for name in ('numpy', 'scipy'):
        record = Path(spec['records'][name])
        raw = record.read_bytes()
        record_hashes[name] = hashlib.sha256(raw).hexdigest()
        if record_hashes[name] != binding['environment']['distribution_records'][name]:
            raise ValueError('Resolved dependency RECORD changed: '+name)
        entries = {}
        for rel, identity, length in csv.reader(io.StringIO(raw.decode())):
            if not identity:
                continue
            mode, encoded = identity.split('=', 1)
            expected = base64.urlsafe_b64decode(encoded+'='*((-len(encoded)) % 4)).hex()
            path = Path(spec['site'])/rel
            actual = digest(path)
            if (mode != 'sha256' or actual != expected
                    or (length and path.stat().st_size != int(length))):
                raise ValueError('Current numerical dependency bytes differ: '+str(path))
            entries[rel] = actual
        installed[name] = {'files':len(entries), 'sha256':hashlib.sha256(
            json.dumps(entries, sort_keys=True).encode()).hexdigest()}
    executable = {'python_sha256':digest(sys.executable), 'installed_files':installed}
    environment = {**binding['environment'], 'python':sys.version,
                   'platform':platform.platform(), 'distribution_records':record_hashes,
                   'bdf_sha256':digest(spec['bdf']),
                   'threads':{k:os.environ.get(k) for k in binding['environment']['threads']}}
    if executable != binding['executable'] or environment != binding['environment']:
        raise ValueError('Current direct executable/environment identity mismatch')
    for path, expected in binding['implementation'].items():
        if digest(Path(root)/path) != expected:
            raise ValueError('Remaining-campaign implementation changed: '+path)
    for path, expected in binding['adapter_files'].items():
        if digest(Path(root)/path) != expected:
            raise ValueError('Remaining-campaign adapter changed: '+path)
    return {'environment':environment, 'executable':executable,
            'method':'Current resolved-file checks; no distribution discovery',
            'environment_health':'UNRESOLVED'}


def load_binding(root, matrix=None, campaign=None):
    root = Path(root)
    binding = read(root/DOC/'REMAINING.json')
    frozen = read(root/DOC/'MATRIX.json')
    if (binding['authorization'] != AUTHORIZATION
            or digest(root/DOC/'MATRIX.json') != MATRIX_SHA256
            or binding['original_matrix_sha256'] != MATRIX_SHA256
            or binding['original_implementation'] != frozen['implementation']
            or (matrix is not None and matrix != frozen)):
        raise ValueError('Remaining-campaign original matrix/authorization mismatch')
    order = ['repeat']+[r for r in frozen['row_order'] if r not in ('anchor', 'repeat')]
    if binding['new_row_order'] != order or len(set(order)) != 13:
        raise ValueError('Exactly thirteen original non-anchor rows required')
    if (set(binding['implementation']) != set(frozen['implementation'])
            or set(binding['starting_implementation']) != set(frozen['implementation'])):
        raise ValueError('Scientific source guard set changed')
    changed = {p for p in binding['implementation']
               if binding['implementation'][p] != binding['starting_implementation'][p]}
    if changed != {'tools/run_grudeva2026_full_reference_010.py'}:
        raise ValueError('Only the declared runner admission/reporting delta is allowed')
    for name, expected in binding['reused_documents'].items():
        if Path(name).name != name or digest(root/DOC/name) != expected:
            raise ValueError('Reused scientific/recovery document changed: '+name)
    previous = read(root/DOC/'RECOVERY.json')
    if binding['starting_implementation'] != previous['implementation']:
        raise ValueError('Starting scientific implementation differs from reviewed recovery')
    summary = read(root/DOC/'BYTE_RECOVERY.json')
    records = binding['recovered_anchor']['records']
    published = {'admission':'numerical-postprocess/RECOVERED_REPRESENTATION.json',
                 'results':'numerical-postprocess/NUMERICAL_RESULTS_RECOVERED.json',
                 'fresh_bundles':'numerical-postprocess/BUNDLE_FRESH_READ.json',
                 'provenance':'RECOVERED_BYTES.json', 'byte_recovery':'BYTE_RECOVERY_COMPLETE.json'}
    if any(records[k]['sha256'] != summary['key_receipts'][name] for k,name in published.items()):
        raise ValueError('Anchor receipts differ from published reviewed recovery')
    if records['original_source']['sha256'] != summary['byte_recovery']['original_commitment_sha256']:
        raise ValueError('Anchor original prospective source identity changed')
    review = checked(records['review'])
    if (review['candidate_commit'] != binding['starting_reviewed_head']
            or review['disposition'] != 'PASS_FOR_RECOVERED_ANCHOR_RESULTS_WITH_INCOMPLETE_FULL_REFERENCE_QUALIFICATION'):
        raise ValueError('Recovered-anchor scoped review missing or stale')
    if campaign is not None and hashlib.sha256(str(Path(campaign).resolve()).encode()).hexdigest() != binding['evidence_directory_identity']:
        raise ValueError('Remaining campaign requires its exclusive bound directory')
    verify_runtime(root, binding)
    return binding


def anchor_records(binding, matrix):
    """Resolve actual admitted records, without manufacturing an old schema."""
    spec = binding['recovered_anchor']
    records = {key:checked(value) for key,value in spec['records'].items()}
    ck, end = records['checkpoint'], records['solver_end']
    admission, fidelity, stats = records['admission'], records['fidelity'], records['results']
    if (spec['row'] != 'anchor' or end['row'] != 'anchor' or end['status'] != 'COMPLETE'
            or ck['case'] != matrix['case'] or ck['settings'] != matrix['rows']['anchor']
            or spec['support_sha256'] != metadata_digest(matrix['support'])):
        raise ValueError('Recovered anchor row/case/settings/support mismatch')
    if (admission['status'] != 'ADMITTED_FOR_ORIGINAL_OBSERVATIONS_AND_AUDITS_BY_REVIEWED_EQUIVALENT_CHECK'
            or admission['original_write_succeeded'] is not False
            or admission['original_source_commitment_sha256'] != spec['records']['original_source']['sha256']
            or admission['fidelity_sha256'] != spec['records']['fidelity']['sha256']
            or fidelity['status'] != 'PASS_EQUIVALENT_COMMITTED_COEFFICIENT_EVALUATION'
            or fidelity['required_support_times'] != len(matrix['support']['times'])
            or records['fresh_bundles']['results_sha256'] != spec['records']['results']['sha256']
            or records['fresh_bundles']['status'] != 'PASS'
            or not all(stats['gates'].values())):
        raise ValueError('Recovered anchor admission/fidelity/audit identity mismatch')
    plan, original = records['byte_plan'], records['original_source']
    expected_set = {(g,k) for g, arrays in original.items() for k in arrays}
    if (len(plan['members']) != 28
            or {(r['group'],r['member']) for r in plan['members']} != expected_set):
        raise ValueError('Recovered anchor member set mismatch')
    for row in plan['members']:
        if row['expected'] != original[row['group']][row['member']]:
            raise ValueError('Recovered payload expectation differs from original source')
    for j in range(2):
        for key in ('t', 'y'):
            if original[f'segment-{j}'][key] != ck['segments'][j]['arrays'][key]['array']:
                raise ValueError('Recovered anchor accepted checkpoint lineage mismatch')
    return records


def verify_anchor_bytes(root, binding, campaign):
    """Separate stdlib reader; stderr and actual exit survive a child crash."""
    spec = binding['recovered_anchor']
    destination = Path(tempfile.mkdtemp(prefix='anchor-byte-read-', dir=campaign))
    command = [binding['runtime']['python'], '-I', '-S', '-X', 'faulthandler',
               str(Path(root)/'tools/verify_grudeva2026_recovery_bytes_010.py'),
               '--plan',spec['records']['byte_plan']['path'], '--output',str(destination/'checked')]
    with (destination/'stdout.log').open('xb') as out, (destination/'stderr.log').open('xb') as err:
        result = subprocess.run(command, stdout=out, stderr=err)
        for stream in (out,err):
            stream.flush(); os.fsync(stream.fileno())
    with (destination/'exit.json').open('x') as stream:
        json.dump({'command':command,'exit_code':result.returncode},stream,indent=2)
        stream.flush(); os.fsync(stream.fileno())
    if result.returncode:
        raise RuntimeError('Recovered-anchor byte reader failed; no retry: '+str(destination))
    receipt = read(destination/'checked/RESULT.json')
    if receipt['status'] != 'PASS' or receipt['members_verified'] != 28:
        raise ValueError('Recovered-anchor byte admission incomplete')
    return str(destination)


def anchor_stats(root, campaign, binding, matrix, validate_bundle, validate_support, full_archive=True):
    records = anchor_records(binding, matrix)
    if full_archive:
        verify_anchor_bytes(root, binding, campaign)
    path = Path(binding['recovered_anchor']['records']['results']['path']).parent
    stats = records['results']
    for name, record in stats['bundles'].items():
        validate_bundle(path/name, record)
    validate_support(path/'observations.npz', matrix['support'])
    return {**stats, 'settings':matrix['rows']['anchor'],
            'gates':{**stats['gates'], 'archive_evaluation':True},
            'recovery':{'admission':records['admission'],
                        'basis':'Reviewed equivalent committed-coefficient fidelity; original live-source unavailable',
                        'original_work_counters':'UNAVAILABLE', 'new_solver_executions':0},
            'archive':{'observation_bundle':stats['bundles']['observations.npz'],
                       'diagnostic_bundle':stats['bundles']['diagnostics.npz']}}
