"""Separately invoked, bounded 005 verification; never a CI full-mesh test.

Source-derived results: Pannusch/Schmieder, Mendeley 10.17632/y2tz67f6ry.1,
CC-BY-NC-3.0, separately from first-party code licensing.
"""
from __future__ import annotations

import argparse
from dataclasses import fields, is_dataclass
import fcntl
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

import numpy as np

from puckworks.models.pannusch2024 import stateful_fv as sf

TASK = "MODEL-PANNUSCH2024-STATE-ENVELOPE-005"


def fixture(n=400, h=.02):
    """The one predeclared synthetic case; no source observation reads."""
    settings = sf.FVSettings(cells=n, h_max_s=h)
    a = sf.FVPlan(sf.TemperatureHistory.linear_celsius((7, 11, 17), (80, 96, 87)),
                  sf.FlowHistory((7, 10, 17), (1.2e-6, 2.7e-6, 1.8e-6), 'linear'),
                  (7, 17), settings)
    b = sf.FVPlan(sf.TemperatureHistory.linear_celsius((7, 9.5, 17), (96, 84, 92)),
                  sf.FlowHistory((7, 17), (2.16e-6,), 'constant'), (7, 17), settings)
    edges = np.linspace(0, .015, n+1)
    x = (edges[:-1]+edges[1:])/(2*.015)
    lower = np.array([.2+.5*x, .2+.4*x, .5+.3*x])
    upper = np.array([3+3*x, 8-3*x, 8+2*x])

    def state(c):
        return sf.FVChemicalState.from_cell_averages(solute='caffeine', grind=1.7,
            time_s=7., edges_m=edges, liquid_kg_m3=c[0], fine_kg_m3=c[1], coarse_kg_m3=c[2])
    return a, b, state(lower), state(upper), state((lower+upper)/2)


class Budget:
    """One small persistent task receipt, anchored in the Git common directory."""

    def __init__(self, evidence_dir):
        self.evidence = Path(evidence_dir).resolve()
        self.evidence.mkdir(parents=True, exist_ok=True)
        common = Path(subprocess.check_output(
            ['git', 'rev-parse', '--git-common-dir'], text=True).strip()).resolve()
        self.path = common / 'model-pannusch2024-state-envelope-005-budget.json'
        self.lock = open(str(self.path)+'.lock', 'a')
        fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.data = (json.loads(self.path.read_text()) if self.path.exists() else
                     dict(task=TASK, evidence_dir=str(self.evidence), executions=[], wall_s=0.))
        if self.data['evidence_dir'] != str(self.evidence):
            raise ValueError('BUDGET_CANNOT_RESET_BY_CHANGING_DIRECTORY')
        if any(r['status'] == 'RUNNING' for r in self.data['executions']):
            raise ValueError('INTERRUPTED_EXECUTION_REQUIRES_EXPLICIT_ACCOUNTING')

    def save(self):
        tmp = self.path.with_suffix('.tmp')
        tmp.write_text(json.dumps(self.data, sort_keys=True, indent=2, allow_nan=False)+'\n')
        tmp.replace(self.path)
        public = {k: v for k, v in self.data.items() if k != 'evidence_dir'}
        (self.evidence/'resources.json').write_text(
            json.dumps(public, sort_keys=True, indent=2, allow_nan=False)+'\n')

    def run(self, label, units, callback, *, correction=None):
        used = sum(r['large_executions'] for r in self.data['executions'])
        if used+units > (32 if correction else 28):
            raise RuntimeError('AGGREGATE_EXECUTION_LIMIT')
        if not correction and any(r['label'] == label for r in self.data['executions']):
            raise RuntimeError('REPEAT_REQUIRES_NAMED_CORRECTION_ACCOUNTING')
        remaining = 1800-self.data['wall_s']
        if remaining <= 0:
            raise RuntimeError('AGGREGATE_NUMERICAL_WALL_LIMIT')
        row = dict(label=label, large_executions=units, correction=correction, status='RUNNING')
        self.data['executions'].append(row)
        self.save()
        start = time.monotonic()
        old_handler = signal.getsignal(signal.SIGALRM)

        def expired(*_):
            raise TimeoutError('NUMERICAL_WALL_LIMIT')
        signal.signal(signal.SIGALRM, expired)
        signal.setitimer(signal.ITIMER_REAL, min(120., remaining))
        try:
            result = callback()
            row['status'] = 'RETURNED'
            if hasattr(result, 'exponential_applications'):
                row['exponential_actions'] = int(result.exponential_applications)
            if hasattr(result, 'response_passes'):
                row['response_passes'] = result.response_passes
            if hasattr(result, 'forward_status') or isinstance(result, sf.StatefulFVResult):
                row['forward_calls'] = 1
            if hasattr(result, 'optimization_calls'):
                row['optimization_calls'] = result.optimization_calls
            if isinstance(result, dict) and 'optimization_calls' in result:
                row['optimization_calls'] = result['optimization_calls']
            return result
        except BaseException as exc:
            row['status'] = 'FAILED'
            row['exception_type'] = type(exc).__name__
            raise
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0.)
            signal.signal(signal.SIGALRM, old_handler)
            row['wall_s'] = time.monotonic()-start
            row['peak_rss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            self.data['wall_s'] += row['wall_s']
            self.save()


def benchmark(budget, label):
    a, _, _, _, state = fixture()
    result = budget.run(label, 1, lambda: sf.simulate_stateful_fv(plan=a,
        initial_state=state, observation_times_s=(7., 17.), fraction_windows_s=((7., 17.),)))
    record = dict(plan_identity=a.identity_sha256, state_identity=state.identity_sha256,
        status=result.status, reason=result.reason, integration_complete=result.integration_complete,
        delivery_kg=result.fractions[0].solute_kg,
        exponential_actions=result.exponential_applications, elapsed_wall_s=result.elapsed_wall_s)
    (budget.evidence/(label+'.json')).write_text(json.dumps(record, sort_keys=True, indent=2)+'\n')
    if result.status != 'COMPLETE' or not result.integration_complete:
        raise RuntimeError('MANDATORY_FORWARD_BENCHMARK_FAILED')
    return record


def compact(value):
    """Keep bulky arrays, full trajectories and nondeterministic timings outside Git."""
    if isinstance(value, sf.FVChemicalState):
        return dict(identity=value.identity_sha256, inventory_kg=value.inventory_kg)
    if isinstance(value, np.ndarray):
        return dict(shape=list(value.shape), sha256=hashlib.sha256(value.tobytes()).hexdigest())
    if is_dataclass(value):
        return {f.name: compact(getattr(value, f.name)) for f in fields(value)
                if f.name != 'elapsed_wall_s'}
    if isinstance(value, (tuple, list)):
        return [compact(x) for x in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def sensitivity(u, weights, allowances, settings):
    from puckworks.models.pannusch2024 import state_envelope as se
    extrema = [se._optimize(u, weights, allowances, s, settings) for s in ('minimum', 'maximum')]
    lo, hi = extrema
    interval = (max(0., hi.interval_kg[0], -lo.interval_kg[1]),
                max(0., hi.interval_kg[1], -lo.interval_kg[0]))
    good = all(e.status == 'OPTIMIZATION_QUALIFIED' and e.gap_kg <= 1e-9 for e in extrema)
    return dict(status='QUALIFIED_FIXED_OPERATOR_DIFFERENCE' if good else 'NUMERICALLY_UNRESOLVED',
        maximum_absolute_difference_interval_kg=interval,
        optimization_calls=sum(e.optimization.calls for e in extrema),
        minimum=compact(lo), maximum=compact(hi),
        interpretation='WHOLE_ORIGINAL_SET_SENSITIVITY_NOT_A_CONTINUUM_ERROR_BOUND')


def lift_transpose(vector):
    """Only the predeclared two-child equal-mass lift, not a remeshing API."""
    return np.asarray(vector).reshape(3, -1, 2).mean(axis=2).ravel()


def execute(budget):
    from puckworks.models.pannusch2024 import state_envelope as se
    baseline = json.loads((budget.evidence/'baseline-forward.json').read_text())
    if baseline['status'] != 'COMPLETE':
        raise RuntimeError('GREEN_FORWARD_BASELINE_REQUIRED')
    a, b, lo, hi, _ = fixture()
    u = se.FVChemicalStateSet(lo, hi, (8e-5, 1.2e-4), 'PREDECLARED_SYNTHETIC_U_005',
        ((8e-6, 3e-5), (1e-5, 5e-5), (2e-5, 8e-5)))
    results = dict(task=TASK, disposition='INCOMPLETE', PHYSICAL_VALIDATION='NOT_ESTABLISHED',
        default_h_s=.02, epsilon_kg=1e-9, delta_kg=1e-6, queries={}, temporal_levels=[], temporal=[], mesh=[],
        source_code_sha256=se._source_code(), state_set_identity=u.identity_sha256,
        observation_window_s=(7., 17.), source_species='caffeine', grind=1.7,
        historical_004=dict(resolved_temporal_decrease='FAIL', disposition='IMPLEMENTED_QUALIFICATION_INCOMPLETE'))

    def save():
        (budget.evidence/'RESULTS.json').write_text(json.dumps(results, sort_keys=True, indent=2, allow_nan=False)+'\n')

    def build(label, p):
        r = budget.run(label, 2, lambda: se.build_delivery_response(p, solute='caffeine', window_s=(7., 17.)))
        if r.weights is not None:
            np.savez_compressed(budget.evidence/(label+'.npz'), weights=r.weights, allowances=r.coefficient_allowances)
        if r.status != 'RESPONSE_QUALIFIED':
            raise RuntimeError(label+':'+r.termination)
        return r

    def query(label, ra, rb=None):
        q = budget.run(label+'-optimization', 0, lambda:
            se.bound_delivery(u, ra, epsilon_kg=1e-9) if rb is None else
            se.contrast_deliveries(u, ra, rb, epsilon_kg=1e-9, delta_kg=1e-6,
                                  comparison_basis='MATCHED_COLLECTED_VOLUME'))
        results['queries'][label] = json.loads(q.to_json())
        save()
        if q.numerical_status != 'WITNESS_REPLAY_REQUIRED':
            raise RuntimeError(label+':'+q.termination)
        return q

    def replays(label, q):
        receipts = []
        for e in (q.minimum, q.maximum):
            np.savez_compressed(budget.evidence/(label+'-'+e.sense+'-witness.npz'),
                masses_kg=e.witness.masses_kg,
                liquid_kg_m3=e.witness.state.liquid_cell_average_kg_m3,
                fine_kg_m3=e.witness.state.fine_cell_average_kg_m3,
                coarse_kg_m3=e.witness.state.coarse_cell_average_kg_m3)
            group = []
            for j, r in enumerate(q.responses):
                receipt = budget.run(label+'-'+e.sense+'-plan-'+str(j), 1,
                    lambda: se.replay_witness(u, r, e.witness))
                group.append(receipt)
            receipts.append(tuple(group))
        q = se.qualify_envelope(q, minimum_replays=receipts[0], maximum_replays=receipts[1])
        results['queries'][label] = json.loads(q.to_json())
        save()
        if q.numerical_status != 'NUMERICALLY_QUALIFIED':
            raise RuntimeError(label+':'+q.termination)

    try:
        ra, rb = build('A-N400-h020', a), build('B-N400-h020', b)
        qa, qb, qc = query('A', ra), query('B', rb), query('A-minus-B', ra, rb)
        for label, q in (('A', qa), ('B', qb), ('A-minus-B', qc)):
            replays(label, q)
        def level(h, queries):
            results['temporal_levels'].append(dict(h_s=h, is_default=h == .02,
                role='PRIMARY_REPLAYED' if h == .02 else 'SENSITIVITY_ONLY_UNREPLAYED_CANDIDATES',
                functionals={label: dict(outer_delivery_interval_kg=q.outer_delivery_interval_kg,
                    minimum_interval_kg=q.minimum.interval_kg, maximum_interval_kg=q.maximum.interval_kg,
                    minimum_gap_kg=q.minimum.gap_kg, maximum_gap_kg=q.maximum.gap_kg,
                    minimum_optimizer_status=q.minimum.status, maximum_optimizer_status=q.maximum.status)
                    for label, q in zip(('A', 'B', 'A-minus-B'), queries)}))
            save()
        level(.02, (qa, qb, qc))
        responses = {(.02, 'A'): ra, (.02, 'B'): rb}
        for h, name in ((.01, '010'), (.005, '005')):
            plans = fixture(h=h)[:2]
            for label, p in zip(('A', 'B'), plans):
                responses[h, label] = build(label+'-N400-h'+name, p)
            ar, br = responses[h, 'A'], responses[h, 'B']
            finer_queries = [budget.run(label+'-h'+name+'-sensitivity-optimization', 0, callback)
                for label, callback in (
                    ('A', lambda: se.bound_delivery(u, ar, epsilon_kg=1e-9)),
                    ('B', lambda: se.bound_delivery(u, br, epsilon_kg=1e-9)),
                    ('A-minus-B', lambda: se.contrast_deliveries(u, ar, br, epsilon_kg=1e-9,
                        delta_kg=1e-6, comparison_basis='MATCHED_COLLECTED_VOLUME')))]
            level(h, finer_queries)
            if any(q.numerical_status != 'WITNESS_REPLAY_REQUIRED' for q in finer_queries):
                raise RuntimeError('TEMPORAL_LEVEL_OPTIMIZATION_FAILED')
        # Each functional difference is optimized over the entire SAME U.
        for coarse, fine in ((.02, .01), (.01, .005)):
            differences, errors = [], []
            for label in ('A', 'B'):
                c, f = responses[coarse, label], responses[fine, label]
                differences.append(c.weights-f.weights)
                errors.append(c.coefficient_allowances+f.coefficient_allowances+
                              2*se.EPS*(np.abs(c.weights)+np.abs(f.weights)))
            for label, w, e in zip(('A', 'B', 'A-minus-B'),
                    (*differences, differences[0]-differences[1]),
                    (*errors, errors[0]+errors[1]+2*se.EPS*(np.abs(differences[0])+np.abs(differences[1])))):
                row = budget.run('temporal-'+str(coarse)+'-'+label, 0,
                                 lambda: sensitivity(u, w, e, ra.settings))
                results['temporal'].append(dict(coarse_h_s=coarse, fine_h_s=fine, functional=label, **row))
                save()
                if row['status'] != 'QUALIFIED_FIXED_OPERATOR_DIFFERENCE':
                    raise RuntimeError('WHOLE_SET_TEMPORAL_OPTIMIZATION_FAILED')
        differences, errors = [], []
        for label, p, coarse in zip(('A', 'B'), fixture(n=800)[:2], (ra, rb)):
            fine = build(label+'-N800-h020', p)
            projected = lift_transpose(fine.weights)
            differences.append(coarse.weights-projected)
            errors.append(coarse.coefficient_allowances+lift_transpose(fine.coefficient_allowances)
                          +4*se.EPS*(np.abs(coarse.weights)+lift_transpose(np.abs(fine.weights))))
        for label, w, e in zip(('A', 'B', 'A-minus-B'),
                (*differences, differences[0]-differences[1]),
                (*errors, errors[0]+errors[1]+2*se.EPS*(np.abs(differences[0])+np.abs(differences[1])))):
            row = budget.run('mesh-'+label, 0, lambda: sensitivity(u, w, e, ra.settings))
            results['mesh'].append(dict(functional=label, lift='EQUAL_MASS_TO_TWO_CHILD_CELLS_PER_PHASE', **row))
            save()
            if row['status'] != 'QUALIFIED_FIXED_OPERATOR_DIFFERENCE':
                raise RuntimeError('WHOLE_SET_MESH_OPTIMIZATION_FAILED')
        final = benchmark(budget, 'final-forward')
        if any(final[k] != baseline[k] for k in ('plan_identity', 'state_identity', 'delivery_kg')):
            raise RuntimeError('UNCHANGED_FORWARD_REPEAT_FAILED')
        repeat = build('A-N400-h020-timing-repeat', a)
        repeat_query = query('A-timing-repeat', repeat)
        if not np.array_equal(repeat.weights, ra.weights) or repeat_query.outer_delivery_interval_kg != qa.outer_delivery_interval_kg:
            raise RuntimeError('RESPONSE_OR_ENVELOPE_REPEAT_FAILED')
        results['disposition'] = 'DECLARED_NUMERICAL_VERIFICATION_PASSED_SOFTWARE_AND_HOSTED_CI_SEPARATE'
    except BaseException as exc:
        results['termination'] = type(exc).__name__+':'+str(exc)
        save()
        raise
    save()
    print(results['disposition'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('baseline', 'execute'))
    parser.add_argument('--evidence-dir', required=True)
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    for name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
        if os.environ.get(name) != '1':
            parser.error(name+' must be 1')
    if not args.worker:
        # An independent parent kills a stuck native call at the remaining hard
        # aggregate deadline. The child receipt remains RUNNING and blocks reset.
        evidence = Path(args.evidence_dir)
        receipt = evidence/'resources.json'
        used = json.loads(receipt.read_text())['wall_s'] if receipt.exists() else 0.
        remaining = 1800-used
        if remaining <= 0:
            raise RuntimeError('AGGREGATE_NUMERICAL_WALL_LIMIT')
        subprocess.run([sys.executable, '-m', 'tools.pannusch_state_envelope_verification',
                        *sys.argv[1:], '--worker'], check=True, timeout=remaining)
        return
    budget = Budget(args.evidence_dir)
    if args.operation == 'baseline':
        print(json.dumps(benchmark(budget, 'baseline-forward'), sort_keys=True))
    else:
        execute(budget)


if __name__ == '__main__':
    main()
