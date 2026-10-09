"""008 identity-bound admission and durable offline execution, without solvers."""
from __future__ import annotations

import fcntl
import gc
import os
import threading
import time
from pathlib import Path

import numpy as np

from . import grudeva2026_matched_comparison_008 as score
from . import grudeva2026_baseline_observation_005 as obs
from . import grudeva2026_baseline_observation_005_report as observation_report
from . import grudeva2026_bed_accuracy_004_report as comparator_report
from . import grudeva2026_fine_baseline_qualification_007 as qualification
from . import grudeva2026_replay_reassessment_007 as reassess
from . import grudeva2026_replay_certificate_007 as certificate

require = score.require
ROOT = score.ROOT
QDOC = qualification.DOCS
CDOC = ROOT/'docs/analysis/model_grudeva2026_bed_accuracy_004'
READ = comparator_report.read


def bound(root, item):
    path = (root/item['file']).resolve()
    require(not Path(item['file']).is_absolute() and path.is_relative_to(root.resolve()),
            'unsafe artifact path')
    require(obs.sha(path) == item['sha256'], 'artifact hash mismatch: '+item['file'])
    return READ(path)


def check_contract(contract):
    require(contract['task'] == score.TASK and contract['pairs'] == [list(p) for p in score.PAIRS],
            'wrong task or primary/secondary pair identities')
    require(contract['limits'] == score.LIMITS and contract['sign'] == 'PRODUCTION_MINUS_COMPARATOR',
            'wrong comparison policy')
    require(contract['normalization'] == 'phi_T*L*A*c_sat' and contract['units'] == 'dimensionless',
            'wrong units or normalization')
    require(contract['support'] == score.support_identity(), 'wrong support identities')
    require(contract['parameters'] == READ(QDOC/'PLAN.json')['parameters'], 'wrong physics')
    require(contract['canonical_physics'] == score.CANONICAL_PHYSICS, 'wrong canonical mapping')
    saved_support = bound(score.DOCS, contract['support_file'])
    t, z = score.support()
    require(saved_support == dict(times=t.tolist(), z=z.tolist(), history_z=list(obs.HISTORY_Z)),
            'exact requested support arrays differ')
    require(contract['environment'] == obs.environment(), 'runtime compatibility mismatch')
    require(contract['exit_codes'] == score.EXIT_CODES, 'exit-code contract differs')
    for group in ('sources', 'implementation'):
        for path, digest in contract[group].items():
            require(obs.sha(ROOT/path) == digest, 'changed source or qualification record: '+path)
    require(set(contract['inputs']) == {'P0', 'P1', 'C0', 'C1'}, 'wrong input set')


def accepted_qualification(root):
    accounting = READ(QDOC/'REPLAY_ACCOUNTING.json')
    require(accounting['all_new_starts_closed'], '007 replay accounting not closed')
    for name, ledger in accounting['ledgers'].items():
        require(ledger['closed'] and not ledger['unresolved']
                and obs.sha(root/name/'ledger.jsonl') == ledger['ledger_sha256'],
                '007 replay ledger differs from accepted closed record')
    result = READ(QDOC/'REPLAY_RESULTS.json')
    require(result['disposition'] == qualification.QUALIFIED and all(result['qualification_gates'].values()),
            'final 007 qualification unavailable')
    full = bound(root, result['full_external_result'])
    require(full['disposition'] == qualification.QUALIFIED and all(full['qualification_gates'].values()),
            'external 007 qualification unavailable')
    require(full['reassessment'] == result['reassessment'], 'qualification reassessment mismatch')
    return result, full


def certificate_admission(meta, metadata_hash, analysis, analysis_hash, observations_hash, cert, final):
    """Verify the accepted certificate composition; never assert certified=True.

    The caller hash-binds all these objects to the immutable accepted 007 records.
    No certificate is recomputed, and diagnostic-origin labels stay intact.
    """
    require(final['disposition'] == qualification.QUALIFIED and all(final['qualification_gates'].values()),
            'qualification is incomplete')
    require(cert['passed'] and cert['analysis_sha256'] == analysis_hash
            == final['reassessment']['analysis_sha256'], 'certificate/analysis mismatch')
    require(analysis['assessment'] == 'DIAGNOSTIC_ONLY'
            and analysis['replay_admission'] == 'UNRESOLVED_ORIGINAL_FAILURE_PRESERVED',
            'diagnostic origin was rewritten')
    require(analysis['metadata_sha256'] == metadata_hash
            and analysis['observations_sha256'] == observations_hash, 'observation binding mismatch')
    require(set(analysis['gates']) == qualification.GATES and all(analysis['gates'].values()),
            'diagnostic observation audit incomplete')
    capture = cert['captures']['combined']
    require(capture['passed'] and capture['metadata_sha256'] == metadata_hash, 'wrong certified capture')
    require(len(capture['segments']) == len(meta['segments']) == 3, 'certificate segment coverage')
    for i in range(3):
        admitted, original = capture['segments'][i], meta['segments'][i]
        live = original['live_replay']
        require(admitted['segment'] == i and admitted['passed'] and admitted['event_gate']
                and admitted['live_offline_fidelity'] and live['allowance_fraction'] <= 1
                and live['event_state_error'] <= reassess.THRESHOLD
                and admitted['original_accepted_error'] == live['accepted_state_error'],
                'certificate does not admit original segment')
        if i == 2:
            require(not admitted['original_accepted_gate'] and admitted['coordinate_certificate'] is True
                    and original['capture_outcome'] == original['numerical_replay'] == 'FAILED'
                    and 'unavailable_reason' in original, 'historical replay failure not preserved')
        else:
            require(admitted['original_accepted_gate'] and certificate.replay_admission(live)
                    and original['capture_outcome'] == original['numerical_replay'] == 'PASS',
                    'ordinary segment admission failed')
    return dict(qualified=True, observation_origin=analysis['assessment'],
                admission='ACCEPTED_007_CERTIFICATE', original_failed_metadata_preserved=True,
                analysis_sha256=analysis_hash, observations_sha256=observations_hash,
                metadata_sha256=metadata_hash)


def admit_production(identity, parent, contract):
    root = parent/'grudeva2026-fine-baseline-qualification-007'
    prior = parent/'grudeva2026-spatial-resolution-006'
    historical = parent/'grudeva2026-baseline-observation-005'
    plan = READ(QDOC/'PLAN.json')
    result, final = accepted_qualification(root)
    item = contract['inputs'][identity]
    require(item['controls'] == qualification.ROWS['baseline_512' if identity == 'P0' else 'combined'],
            'production configuration differs')
    if identity == 'P0':
        require(item['metadata'] == plan['reuse']['metadata']
                and item['observations'] == plan['reuse']['observations'], 'P0 replaced by another capture')
        meta = qualification.baseline_inputs(prior, historical, plan, arrays=True)
        require(all(meta[k] == item[k] for k in ('task', 'row', 'attempt'))
                and meta['matrix_sha256'] == item['plan_sha256'], 'production origin differs')
        run = bound(prior, item['observations'])
        prior_result = READ(ROOT/'docs/analysis/model_grudeva2026_spatial_resolution_006/RESULTS.json')
        require(run['controls'] == qualification.BASE and run['audits'] == prior_result['candidate_audits'],
                'P0 observation/audit mismatch')
        gates = observation_report.numeric_gates(run, meta)
        require(gates == final['baseline_gates'] and all(gates.values()), 'P0 qualification receipt mismatch')
        receipt = dict(qualified=True, admission='ORIGINAL_006_CAPTURE_QUALIFIED_BY_007',
                       metadata_sha256=item['metadata']['sha256'],
                       observations_sha256=item['observations']['sha256'])
    else:
        correction = READ(QDOC/'REPLAY_ADMISSION_CORRECTION.json')
        original, _ = reassess.verify(root, correction)
        path, meta = reassess.combined_input(root, original)
        require(all(meta[k] == item[k] for k in ('task', 'row', 'attempt'))
                and meta['matrix_sha256'] == item['plan_sha256'], 'production origin differs')
        require(item['metadata']['sha256'] == obs.sha(path)
                and item['metadata']['file'] == str(path.relative_to(root)), 'P1 capture substituted')
        analysis = bound(root, correction['analysis'])
        cert = bound(root, item['certificate'])
        require(item['certificate']['sha256'] == result['reassessment']['certificate_sha256'],
                'accepted certificate identity differs')
        receipt = certificate_admission(meta, obs.sha(path), analysis, correction['analysis']['sha256'],
                                        item['observations']['sha256'], cert, final)
        trajectory = reassess.DiagnosticTrajectory(path)
        try:
            require(trajectory.horizon == 8. and trajectory.arrival is not None,
                    'combined trajectory coverage unavailable')
        finally:
            trajectory.close()
        run = bound(root, item['observations'])
        require(run['controls'] == qualification.ROWS['combined'] and run['audits'] == analysis['audits'],
                'P1 observation/audit mismatch')
    require(not score.event_reasons(run), 'production event admission failed')
    score.aligned(run)
    receipt.update(task=meta['task'], row=meta['row'], attempt=meta['attempt'],
                   controls=meta['controls'], plan_sha256=meta['matrix_sha256'],
                   environment=meta['environment'], sources=meta['sources'],
                   named_arrays_verified=True, qualification_sha256=obs.sha(QDOC/'REPLAY_RESULTS.json'),
                   segments=[dict(file=s['file'], sha256=s['sha256'],
                                  array_manifest_sha256=obs.digest(s['array_manifest']),
                                  receipt_sha256=s['receipt_sha256'],
                                  original_numerical_replay=s['numerical_replay']) for s in meta['segments']])
    return run, receipt


def admit_comparator(identity, parent, contract):
    root = parent/'model-grudeva2026-bed-accuracy-004'
    plan, final = READ(CDOC/'MATRIX.json'), READ(CDOC/'RESULTS.json')
    require(final['qualified'] and final['disposition'] == comparator_report.QUALIFIED,
            '004 final qualification unavailable')
    require(final['matrix_sha256'] == obs.sha(CDOC/'MATRIX.json'), '004 matrix binding mismatch')
    require(plan['scientific_sources'] == comparator_report.scientific_sources(), '004 sources changed')
    for path, digest in plan['verification_sources'].items():
        require(obs.sha(ROOT/path) == digest, '004 qualified observer changed')
    require(obs.sha(root/'environment.json') == final['environment_sha256'], '004 environment changed')
    require(obs.sha(root/'invocations.jsonl') == final['raw_ledger_sha256'], '004 accounting changed')
    resources, starts, ends = comparator_report.resource_audit(root)
    require(resources == final['resources'], '004 accounting does not close')
    row = 'normal' if identity == 'C0' else 'combined'
    item = contract['inputs'][identity]
    expected = plan['runs'][row]
    require(item['task'] == final['task'] and item['row'] == row and item['attempt'] == expected['attempt']
            and item['controls'] == comparator_report.controls(row)
            and item['matrix_sha256'] == final['matrix_sha256'], 'comparator origin/configuration differs')
    require(item['observations'] == dict(file=expected['file'], sha256=final['runs'][row]['artifact_sha256']),
            'wrong comparator row/artifact')
    run = bound(root, item['observations'])
    start, end = starts[expected['attempt']], ends[expected['attempt']]
    require(start['kind'] == 'full' and end['exit_code'] == 2
            and end['artifact_sha256'] == item['observations']['sha256'], 'comparator attempt binding mismatch')
    require(start['source_hashes']['puckworks/analysis/grudeva2026_bed_accuracy_004.py'] == run['source_sha256'],
            'comparator executed source mismatch')
    # The unchanged safe reader/audit checks actual states, alignment, event
    # sides, coordinates, physical inventories and saved cup semantics.
    audit = comparator_report.audit_run(run, comparator_report.controls(row))
    require(dict(audit, artifact_sha256=item['observations']['sha256']) == final['runs'][row],
            'comparator numerical records differ from qualified receipt')
    require(audit['passed'], 'comparator audit not qualified')
    return run, dict(qualified=True, admission='QUALIFIED_004_FINAL', task=final['task'],
                     row=row, attempt=expected['attempt'], controls=run['controls'],
                     observations_sha256=item['observations']['sha256'], matrix_sha256=final['matrix_sha256'],
                     environment_sha256=final['environment_sha256'], sources=plan['scientific_sources'],
                     qualification_sha256=obs.sha(CDOC/'RESULTS.json'),
                     lineage='Permission-attributed adapted reference; not untouched author execution')


def integration(receipt):
    expected = {'paper3-evidence', 'generated-artifacts', 'scientific-baseline',
                'experience', 'notebook-smoke', 'packaging', 'quick-pr'}
    runs = receipt['workflow_runs']
    require(len(runs) == 7 and {r['name'] for r in runs} == expected, 'integration workflow coverage')
    compact = []
    for run in runs:
        require(run['head_sha'] == '37f62d80ce972141b515b48c893244780e6dd097'
                and run['event'] == 'push' and run['status'] == 'completed'
                and run['conclusion'] == 'success', 'exact-merge integration not passing')
        jobs = run['jobs_evidence']['jobs']
        require(jobs and len(jobs) == run['jobs_evidence']['total_count'], 'incomplete integration jobs')
        require(all(j['head_sha'] == run['head_sha'] and j['run_attempt'] == run['run_attempt']
                    and j['status'] == 'completed' and j['conclusion'] == 'success' for j in jobs),
                'integration job not passing')
        compact.append({k: run[k] for k in ('id', 'run_attempt', 'name', 'head_sha', 'event', 'status', 'conclusion')}
                       | dict(jobs=[{k: j[k] for k in ('id', 'name', 'head_sha', 'run_attempt', 'conclusion')}
                                    for j in jobs]))
    return compact


def intersection_diagnostic(details):
    """Same-coordinate diagnostic only; it does not replace any pair verdict."""
    if len(details) != 4:
        return dict(status='UNAVAILABLE', reason='all four pairs are required')
    t, z = score.support()
    out = {}
    for name in score.LIMITS:
        shared = np.logical_and.reduce([d[name]['selected'] for d in details])
        rows = []
        for d in details:
            x = d[name]
            coords = {}
            if name not in ('arrival', 'activation'):
                coords['times'] = t
            if name in ('activation', 'liquid_profiles', 'grain_profiles'):
                coords['z'] = z
            if name == 'grain_histories':
                coords['z'] = obs.HISTORY_Z
            row, _ = score.metric(x['production'], x['comparator'], shared, True,
                                  score.LIMITS[name], **coords)
            rows.append(row)
        out[name] = dict(included=int(shared.sum()), pairs=rows,
                         support_sha256=obs.digest(shared.tolist()))
    return dict(status='DIAGNOSTIC_ONLY', families=out)


def execute(args):
    # Reuse only machine monitoring and durable append helpers, never an old
    # campaign invocation or quota/deadline enforcement path.
    from tools.grudeva2026_fine_baseline_qualification_007_invoke import capacity, append, utc
    args.output.mkdir(parents=True, exist_ok=False)
    ledger = args.output/'ledger.jsonl'
    lock = open(args.output.parent/'008.lock', 'a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    start = time.monotonic()
    stop = threading.Event()
    state = 'IMPLEMENTATION_OR_CONTRACT_FAILURE'
    outputs = {}
    append(ledger, dict(event='start', utc=utc(), pid=os.getpid(), task=score.TASK,
                        contract_sha256=obs.sha(args.contract), environment=obs.environment(),
                        capacity=capacity(args.output), production_simulations=0, comparator_simulations=0))

    def monitor():
        while not stop.wait(30):
            append(args.output/'monitor.jsonl', capacity(args.output))

    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()
    try:
        contract = READ(args.contract)
        # Retain exactly what this attempt binds, including unsuccessful setup.
        qualification.write_new(args.output/'contract.json', contract)
        snapshot = args.output/'implementation'
        snapshot.mkdir()
        for name, expected in contract['implementation'].items():
            data = (ROOT/name).read_bytes()
            (snapshot/Path(name).name).write_bytes(data)
            require(obs.sha(snapshot/Path(name).name) == expected, 'implementation snapshot mismatch')
        check_contract(contract)
        ci = integration(READ(args.integration))
        if not args.admission_only:
            require(args.review is not None, 'pre-scoring audit required')
            review = READ(args.review)
            require(review['passed'] and review['nonhuman'] and review['contract_sha256'] == obs.sha(args.contract)
                    and review['implementation'] == contract['implementation'], 'independent pre-scoring audit missing/mismatched')
        inputs, admissions = {}, {}
        for identity in ('P0', 'P1', 'C0', 'C1'):
            try:
                loader = admit_production if identity.startswith('P') else admit_comparator
                inputs[identity], admissions[identity] = loader(identity, args.evidence, contract)
                append(args.output/'progress.jsonl', dict(input=identity, admission='QUALIFIED', utc=utc()))
            except (OSError, ValueError, KeyError, TypeError) as exc:
                admissions[identity] = dict(qualified=False, reason=str(exc),
                                            evidence_access='UNAVAILABLE' if isinstance(exc, OSError) else 'PRESENT_NOT_ADMITTED')
        qualification.write_new(args.output/'admissions.json', admissions)
        if args.admission_only:
            state = 'COMPLETED'
            outputs = {'admissions.json': obs.sha(args.output/'admissions.json')}
            return dict(execution='ADMISSION_ONLY', complete=len(inputs) == 4,
                        qualified_inputs=list(inputs), cross_method_scores=0)
        pairs, details = [], []
        for name, p, c in score.PAIRS:
            if p in inputs and c in inputs:
                result, arrays = score.compare(inputs[p], inputs[c])
                details.append(arrays)
                np.savez_compressed(args.output/(p+'-'+c+'.npz'),
                                    **{family+'__'+k: v for family, values in arrays.items() for k, v in values.items()})
            else:
                result = score.unavailable_pair('input admission unavailable: '+', '.join(x for x in (p, c) if x not in inputs))
            result.update(pair=name, production=p, comparator=c)
            pairs.append(result)
            qualification.write_new(args.output/(p+'-'+c+'.json'), result)
            append(args.output/'progress.jsonl', dict(pair=name, disposition=result['disposition'], utc=utc()))
        result = dict(task=score.TASK, pairs=pairs, inputs=admissions,
                      disposition=score.task_disposition(pairs), complete=all(p['complete'] for p in pairs),
                      primary_disposition=pairs[0]['disposition'], integration=dict(status='PASS', runs=ci),
                      software_qa='SEPARATE_QA_RECEIPT', evidence_access='AVAILABLE' if len(inputs) == 4 else 'SEE_ADMISSIONS',
                      execution='COMPLETED', contract_sha256=obs.sha(args.contract),
                      pre_scoring_review_sha256=obs.sha(args.review),
                      intersection=intersection_diagnostic(details), physical_validation='NOT_ESTABLISHED',
                      new_production_simulations=0, new_comparator_simulations=0)
        check_contract(contract)
        qualification.write_new(args.output/'results.json', result)
        state = 'COMPLETED'
        outputs = {p.name: obs.sha(p) for p in args.output.iterdir() if p.suffix in ('.json', '.npz')}
        return result
    except BaseException as exc:
        qualification.write_new(args.output/'failure.json', dict(type=type(exc).__name__, reason=str(exc)))
        raise
    finally:
        stop.set()
        thread.join()
        gc.collect()
        append(ledger, dict(event='end', utc=utc(), pid=os.getpid(), status=state,
                            elapsed_seconds=time.monotonic()-start, capacity=capacity(args.output),
                            outputs=outputs, production_simulations=0, comparator_simulations=0))
        lock.close()
