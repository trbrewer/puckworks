"""Narrow 009 wrapper: current-base integration and unchanged 008 admission only."""
from __future__ import annotations

import fcntl
import os
import subprocess
import threading
import time

from . import grudeva2026_publication_reconciliation_009 as score
from . import grudeva2026_matched_comparison_008_io as admission

obs, READ, require = admission.obs, admission.READ, score.require
BASE = dict(head='ab28bd1d20b4fec43d6023a15bc628ee9f0bebcc',
            tree='2aced72fda1c8413d572f803319b7899b9dcb3e5',
            parents=['37f62d80ce972141b515b48c893244780e6dd097',
                     '0ec0dfce30b49a8bd8b6143a5807f20cf0121b32'])
PRIOR = 'docs/analysis/model_grudeva2026_matched_comparison_008/'
PRIOR_CONTRACT_SHA = '4f657f041145cf42916a9f37c4788d290d0b8bac47783c233c6c76be29d81e7c'
PRIOR_BINDINGS_SHA = '4416225b0f04fa34ee6b04cdacdd5a0e9b8df50a09ed0a2feb2e49fb503903e4'
WORKFLOWS = {'paper3-evidence', 'generated-artifacts', 'scientific-baseline',
             'experience', 'notebook-smoke', 'packaging', 'quick-pr'}
POLICY = dict(
    time_matching=dict(absolute_allowance=score.TIME_ATOL, relative_allowance=0,
                       uniqueness='exactly one retained sample within allowance; no interpolation'),
    depth_matching=dict(absolute_allowance=0, relative_allowance=0, uniqueness='exactly one exact physical z'),
    masks=dict(authority='verification.publication_comparison / 001 and 002 publication contracts',
               figure3='closed [min(model_front,reference_front)-.008,max(model_front,reference_front)+.008]',
               figure4='closed [min(model_arrival,publication_arrival)-.025,max(model_arrival,publication_arrival)+.025]',
               t6_4='reference-side z=1 mask boundary only; no fourth measured front or score',
               wetting='retained qualified liquid and outlet; 0 before first drip, 1 until desaturation exit; retained event sides',
               grain_age_mask=False, post_exit_override=False, availability_before_exclusion=True),
    fields=dict(figure3_concentration='observations[i].liquid_profile[j]',
                figure3_front='records[i][1]', figure4_concentration='records[i][2]',
                figure4_arrival='arrival; bound desaturation_exit event sides',
                production='005 qualified raw-state diagnostic profile; never legacy Result.liquid_profiles',
                comparator='004 qualified retained conservative profile'),
    units=dict(time='t_dim/(phi_T*L/q_app)', depth='z_dim/L', concentration='c_l/c_sat',
               inventory='phi_T*L*A*c_sat (provenance only; not rescored)'),
    aggregation=dict(acceptance='inclusive <= at full stored precision',
                     counts='requested=included+excluded+unavailable; 31 per input, 124 total',
                     maxima='included qualified only; report all exact ties in fixture order',
                     completeness='all required rows available and every family has included support',
                     failures='preserved separately even in incomplete families',
                     shared='same target, both qualified and included, same-sign residuals both exceeding limit',
                     primary='P0/C0; shared witness => corroborated even if incomplete elsewhere; otherwise incomplete, agreement, or mixed',
                     refinements='P1/C1 separately; all-four intersection diagnostics never replace headlines',
                     mixed='different method/family verdicts, failures without shared witness or changed primary/refinement shared targets or residual directions; retain shared findings',
                     extraction='pixel bounds separate; no Gaussian weighting or enlarged limits'),
    arithmetic=dict(identity='(P-reference)-(C-reference)=P-C', epsilon_multiplier=score.IDENTITY_ULPS,
                    scale='max(1,abs(P),abs(C),abs(reference),abs(P-reference),abs(C-reference),abs(P-C))',
                    claim='arithmetic accounting only'),
    exit_codes={'0': 'complete publication agreement for all inputs',
                '2': 'complete assessment with expected scientific disagreement; not implementation failure',
                '3': 'incomplete admission or support; retain demonstrated qualified failures',
                '1': 'implementation, contract or operational failure'})


def integration(receipt):
    require(receipt['selected_base'] == BASE and receipt['pull_request'] == 330,
            '009 requires actual #330 selected-base integration, not #329 or PR head')
    runs = receipt['workflow_runs']
    require(len(runs) == 7 and {r['name'] for r in runs} == WORKFLOWS, 'integration workflow coverage')
    require(len({r['id'] for r in runs}) == 7, 'duplicate integration run')
    for r in runs:
        require(r['head_sha'] == BASE['head'] and r['event'] == 'push'
                and r['status'] == 'completed' and r['conclusion'] == 'success'
                and r['run_attempt'] >= 1, 'exact-merge integration not passing')
        jobs = r['jobs_evidence']['jobs']
        require(jobs and len(jobs) == r['jobs_evidence']['total_count']
                and len({j['id'] for j in jobs}) == len(jobs), 'incomplete/duplicate integration jobs')
        require(all(j['head_sha'] == BASE['head'] and j['run_attempt'] == r['run_attempt']
                    and j['status'] == 'completed' and j['conclusion'] == 'success' for j in jobs),
                'integration job not passing on exact merge/attempt')
    return receipt


def check_contract(contract):
    require(contract['task'] == score.TASK and contract['base'] == BASE, 'wrong 009 task/base')
    require(contract['policy'] == POLICY and contract['limits'] == score.LIMITS, 'publication policy differs')
    require(contract['fixture'] == dict(file=score.FIXTURE, sha256=score.FIXTURE_SHA), 'wrong fixture identity')
    require(obs.sha(score.ROOT/score.FIXTURE) == score.FIXTURE_SHA, 'fixture changed')
    fixture = READ(score.ROOT/score.FIXTURE)
    require(contract['targets'] == score.targets(fixture), 'target coordinates/order/units/curve differ')
    require(contract['target_counts'] == score.COUNTS and contract['requested_rows'] == 124, 'wrong coverage')
    require(obs.sha(score.ROOT/PRIOR/'CONTRACT.json') == PRIOR_CONTRACT_SHA, '008 authority changed')
    old = READ(score.ROOT/PRIOR/'CONTRACT.json')
    require(contract['inputs'] == old['inputs'] and contract['canonical_physics'] == old['canonical_physics'],
            'original input or canonical mapping changed')
    require(contract['environment'] == old['environment'] == obs.environment(), 'environment differs')
    require(contract['prior_authorities'] == {
        PRIOR+'CONTRACT.json': PRIOR_CONTRACT_SHA,
        PRIOR+'EVIDENCE_BINDINGS.json': PRIOR_BINDINGS_SHA},
        'prior authority identities differ')
    for group in (old['sources'], old['implementation'], contract['prior_authorities'],
                  contract['sources'], contract['implementation']):
        for path, digest in group.items():
            require(obs.sha(score.ROOT/path) == digest, 'changed bound source: '+path)
    require(contract['physical_validation'] == 'NOT_ESTABLISHED'
            and contract['target_role'] == 'PUBLIC_NUMERICAL_REFERENCE_COMPARISON / TARGET_EXPOSED',
            'claim boundary changed')
    return old, fixture


def check_review(review, contract, contract_sha):
    require(review['passed'] and review['nonhuman'] and review['contract_sha256'] == contract_sha
            and review['implementation'] == contract['implementation'],
            'independent pre-scoring audit missing/mismatched')


def execute(args):
    # Import utility functions only; never invoke the predecessor runner, wrapper,
    # qualification, certification, observation regeneration or 008 comparison.
    from tools.grudeva2026_fine_baseline_qualification_007_invoke import capacity, append, utc, safety_reasons
    lock = open(args.output.parent/'009.lock', 'a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        args.output.mkdir(parents=False, exist_ok=False)
    except BaseException:
        lock.close()
        raise
    write = admission.qualification.write_new
    ledger = args.output/'ledger.jsonl'
    start = time.monotonic()
    state, outputs = 'IMPLEMENTATION_OR_CONTRACT_FAILURE', {}
    stop, unsafe = threading.Event(), []
    append(ledger, dict(event='start', utc=utc(), pid=os.getpid(), task=score.TASK,
                        production_simulations=0, comparator_simulations=0,
                        qualification_campaigns=0, fits=0))

    def monitor():
        previous = None
        while not stop.wait(30):
            snap = capacity(args.output)
            append(args.output/'monitor.jsonl', snap)
            if previous is not None:
                unsafe.extend(safety_reasons(snap, previous))
            previous = snap

    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()
    try:
        snap = capacity(args.output)
        append(args.output/'monitor.jsonl', snap)
        require(not safety_reasons(snap), 'machine safety margin unavailable')
        contract_sha = obs.sha(args.contract)
        contract = READ(args.contract)
        write(args.output/'contract.json', contract)
        old, fixture = check_contract(contract)
        require(obs.sha(args.integration) == contract['integration_sha256'], 'integration receipt identity differs')
        ci = integration(READ(args.integration))
        base_info = subprocess.check_output(['git', 'show', '-s', '--format=%H %T %P', BASE['head']],
                                            cwd=score.ROOT, text=True).strip().split()
        require(base_info == [BASE['head'], BASE['tree'], *BASE['parents']], 'actual selected base differs')
        subprocess.run(['git', 'merge-base', '--is-ancestor', BASE['head'], 'HEAD'], cwd=score.ROOT, check=True)
        check_review(READ(args.review), contract, contract_sha)
        write(args.output/'review.json', READ(args.review))
        write(args.output/'integration.json', ci)
        expected = READ(score.ROOT/PRIOR/'EVIDENCE_BINDINGS.json')['verified_numerical_contents']
        inputs, admissions = {}, {}
        for identity in score.INPUTS:
            require(not unsafe, 'persistent machine pressure: '+str(unsafe))
            try:
                loader = admission.admit_production if identity.startswith('P') else admission.admit_comparator
                run, receipt = loader(identity, args.evidence, old)
                require(receipt == expected[identity], 'admission differs from original 008 evidence binding')
                inputs[identity], admissions[identity] = run, receipt
            except (OSError, ValueError, KeyError, TypeError) as exc:
                admissions[identity] = dict(qualified=False, reason=str(exc),
                                            evidence_access='UNAVAILABLE' if isinstance(exc, OSError) else 'PRESENT_NOT_ADMITTED')
            append(args.output/'progress.jsonl', dict(input=identity, qualified=admissions[identity]['qualified'], utc=utc()))
        write(args.output/'admissions.json', admissions)
        # Recheck bound sources immediately before scoring and after it.
        check_contract(contract)
        require(obs.sha(args.contract) == contract_sha and not unsafe, 'contract changed or machine unsafe')
        result = score.assess(inputs, admissions, fixture)
        result.update(contract_sha256=contract_sha, pre_scoring_review_sha256=obs.sha(args.review),
                      integration_sha256=obs.sha(args.integration), execution='COMPLETED',
                      evidence_access='AVAILABLE' if len(inputs) == 4 else 'SEE_ADMISSIONS',
                      software_correctness='SEPARATE_QA_RECEIPT', integration='PASS',
                      new_production_simulations=0, new_comparator_simulations=0,
                      new_qualification_campaigns=0, fits=0)
        check_contract(contract)
        require(obs.sha(args.contract) == contract_sha, 'contract changed during score')
        write(args.output/'results.json', result)
        state = 'COMPLETED'
        outputs = {p.name: obs.sha(p) for p in args.output.glob('*.json')}
        return result
    except BaseException as exc:
        write(args.output/'failure.json', dict(type=type(exc).__name__, reason=str(exc)))
        raise
    finally:
        stop.set()
        thread.join()
        append(ledger, dict(event='end', utc=utc(), status=state,
                            elapsed_seconds=time.monotonic()-start, capacity=capacity(args.output),
                            outputs=outputs, production_simulations=0, comparator_simulations=0,
                            qualification_campaigns=0, fits=0))
        lock.close()
