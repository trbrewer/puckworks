"""Bounded fixed synthetic 007 comparison; never a full-mesh pytest campaign."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import multiprocessing as mp
import os
import pickle
from pathlib import Path
import platform
import subprocess
import time

import numpy as np
import scipy

from puckworks.models.pannusch2024 import common_past_contrast as cc, prefix_conditioned as pc, state_envelope as se, stateful_fv as sf
from tools.pannusch_prefix_conditioned_verification import generating_state, _child, _freeze_received, _write, _check_generation

TASK = 'MODEL-PANNUSCH2024-COMMON-PAST-CONTRAST-007'
EARLY = ((7., 10.), (10., 12.))
TARGET = (12., 17.)
BRANCH = 12.
EPSILON_KG = 1e-9
DELTA_KG = 1e-6
LEVELS = ((400, .02), (400, .01), (400, .005), (800, .02))


def fixture(n=400, h=.02):
    """Fixed NEW 007 histories and 006 original U construction; no evaluation."""
    times = (7., 12., 14.5, 17.)
    plans = tuple(sf.FVPlan(sf.TemperatureHistory.linear_celsius(times, temperatures),
        sf.FlowHistory(times, tuple(v*1e-6 for v in flows), 'constant'), (7., 17.),
        sf.FVSettings(cells=n, h_max_s=h)) for temperatures, flows in
        (((90, 90, 86, 94), (2., 1.5, 2.5)), ((90, 90, 94, 86), (2., 2.5, 1.5))))
    edges = np.linspace(0., sf.fv.ps.L, n+1)
    x = (edges[:-1]+edges[1:])/(2*sf.fv.ps.L)
    def state(c):
        return sf.FVChemicalState.from_cell_averages(solute='caffeine', grind=1.7, time_s=7.,
            edges_m=edges, liquid_kg_m3=c[0], fine_kg_m3=c[1], coarse_kg_m3=c[2])
    lower = state((.2+.5*x, .2+.4*x, .5+.3*x))
    upper = state((3+3*x, 8-3*x, 8+2*x))
    u = se.FVChemicalStateSet(lower, upper, (8e-5, 1.2e-4),
        '007_EXPLICIT_SYNTHETIC_ASSUMPTION_NOT_COFFEE_PRIOR',
        ((8e-6, 3e-5), (1e-5, 5e-5), (2e-5, 8e-5)))
    return (*plans, u)


def _archive_value(directory, label, value):
    """Full owner-retained object, including failed/nonfinite native output.

    Pickle is an archival format only; consumers must verify its indexed hash
    before loading this owner-created file. No arrays are inferred from hashes.
    """
    data = pickle.dumps(value, protocol=5)
    path = directory/(label+'.pickle')
    temporary = path.with_suffix('.tmp')
    temporary.write_bytes(data); temporary.replace(path)
    _write(directory/(label+'.json'), dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
        format='PYTHON_PICKLE_5_COMPLETE_OBJECT', source_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (Path(cc.__file__), Path(pc.__file__), Path(se.__file__), Path(sf.__file__), Path(sf.fv.__file__))},
        environment=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
            threads={k: os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS')})))
    return dict(archive_sha256=hashlib.sha256(data).hexdigest(), content_identity=sf._hash(value))


def _load_checked_forward(directory, packet):
    """Use the complete child archive as transport; verify bytes AND object content.

    Large arrays never cross the unchecked multiprocessing pickle pipe. A digest
    failure is retained and fails closed; there is no tolerance or retry.
    """
    data = (directory/'before-transport.pickle').read_bytes()
    if hashlib.sha256(data).hexdigest() != packet['archive_sha256']:
        raise RuntimeError('FORWARD_ARCHIVE_TRANSPORT_CHECKSUM_MISMATCH')
    value = pickle.loads(data)
    if sf._hash(value) != packet['content_identity']:
        raise RuntimeError('FORWARD_DESERIALIZED_CONTENT_MISMATCH')
    return value


class Budget:
    """One task receipt, using the existing Git-common-directory accounting pattern.

    POSIX campaign tool. Each native call runs in a separate child with an
    external deadline; native hangs cannot suppress Python signal handling.
    """
    def __init__(self, evidence_dir, *, correction=None, dependencies=None):
        self.evidence = Path(evidence_dir).resolve()
        self.evidence.mkdir(parents=True, exist_ok=True)
        common = Path(subprocess.check_output(['git', 'rev-parse', '--git-common-dir'], text=True).strip()).resolve()
        self.path = common/'model-pannusch2024-common-past-contrast-007-budget.json'
        self.lock = open(str(self.path)+'.lock', 'a')
        fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.data = json.loads(self.path.read_text()) if self.path.exists() else dict(
            task=TASK, evidence_dir=str(self.evidence), executions=[], wall_s=0.)
        if self.data['evidence_dir'] != str(self.evidence):
            self.lock.close()
            raise ValueError('BUDGET_CANNOT_RESET_BY_CHANGING_DIRECTORY')
        if any(row['status'] == 'RUNNING' for row in self.data['executions']):
            self.lock.close()
            raise ValueError('INTERRUPTED_EXECUTION_REQUIRES_ACCOUNTING')
        self.correction = correction
        self.output = self.evidence
        if correction is not None:
            if correction not in ('007-prefix-diagnostic-v1', '007-joint-witness-v1', '007-transport-validation-v1') or not dependencies:
                raise ValueError('NAMED_CORRECTION_AND_EXACT_DEPENDENCIES_REQUIRED')
            if not self.data['executions']:
                raise ValueError('CORRECTION_REQUIRES_EXISTING_CAMPAIGN')
            previous = self.data.setdefault('corrections', [])
            if any(r['identifier'] == correction for r in previous):
                raise ValueError('CORRECTION_ALREADY_ATTEMPTED')
            self.output = self.evidence/'corrections'/correction
            self.output.mkdir(parents=True, exist_ok=False)
            previous.append(dict(identifier=correction, dependencies=dependencies,
                                 starting_executions=len(self.data['executions']), starting_wall_s=self.data['wall_s']))
        self.prior_wall, self.start = self.data['wall_s'], time.monotonic()

    def save(self):
        self.data['wall_s'] = self.prior_wall+time.monotonic()-self.start
        text = json.dumps(self.data, sort_keys=True, indent=2, allow_nan=False)+'\n'
        tmp = self.path.with_suffix('.tmp'); tmp.write_text(text); tmp.replace(self.path)
        public = {k: v for k, v in self.data.items() if k != 'evidence_dir'}
        (self.output/'resources.json').write_text(json.dumps(public, sort_keys=True, indent=2, allow_nan=False)+'\n')

    def run(self, label, kind, units, callback, *, deadline_s=None, correction=None, forward_inputs=None):
        self.save()
        correction = self.correction if correction is None else correction
        if correction != self.correction:
            raise ValueError('CORRECTION_DEPENDENCIES_NOT_REGISTERED')
        if self.correction and kind == 'response':
            raise ValueError('CORRECTION_REUSES_EXISTING_RESPONSES')
        if self.correction and kind == 'forward' and forward_inputs is None:
            raise ValueError('COMPLETE_FORWARD_INPUTS_REQUIRED')
        if kind not in ('response', 'forward', 'lp'):
            raise ValueError('UNKNOWN_NUMERICAL_CALL')
        if type(units) is not int or units != (2 if kind == 'response' else 1 if kind == 'forward' else 0):
            raise ValueError('INVALID_PROPAGATION_RESERVATION')
        rows = self.data['executions']
        if sum(r['charged_propagations'] for r in rows)+units > 80:
            raise RuntimeError('PROPAGATION_LIMIT')
        if sum(r['kind'] == 'lp' for r in rows)+(kind == 'lp') > 160:
            raise RuntimeError('LP_LIMIT')
        if any(r['label'] == label for r in rows):
            raise RuntimeError('REPEAT_REQUIRES_NAMED_CORRECTION')
        remaining = 1800-self.data['wall_s']
        if remaining <= 0:
            raise RuntimeError('AGGREGATE_WALL_LIMIT')
        ceiling = 30. if kind == 'lp' else 120.
        timeout = min(ceiling, remaining, ceiling if deadline_s is None else deadline_s)
        if timeout <= 0:
            raise ValueError('POSITIVE_EXTERNAL_DEADLINE_REQUIRED')
        row = dict(label=label, kind=kind, charged_propagations=units, status='RUNNING', correction=correction)
        rows.append(row); self.save()
        archive = worker = parent = child = actions = None
        archive_created = False
        start = time.monotonic()
        try:
            context = mp.get_context('fork')
            parent, child = context.Pipe(duplex=False)
            actions = context.Value('q', 0, lock=False)
            if kind == 'forward':
                archive = self.output/f'{len(rows):03d}-{label}'
                archive.mkdir()
                archive_created = True
                _archive_value(archive, 'inputs', forward_inputs)
                row['archive'] = str(archive.relative_to(self.evidence))
                original_callback = callback
                def callback():
                    try:
                        value = original_callback()
                        return _archive_value(archive, 'before-transport', value)
                    except BaseException as exc:
                        _write(archive/'failure.json', dict(exception=type(exc).__name__, reason=str(exc)))
                        raise
            worker = context.Process(target=_child, args=(child, callback, actions))
            worker.start(); child.close()
            if not parent.poll(timeout):
                worker.kill(); worker.join()
                raise TimeoutError('EXTERNAL_NATIVE_CALL_DEADLINE')
            status, value, peak = parent.recv()
            worker.join(timeout=max(0., timeout-(time.monotonic()-start)))
            if worker.is_alive():
                worker.kill(); worker.join()
                raise TimeoutError('EXTERNAL_NATIVE_CALL_DEADLINE')
            row['peak_rss_kib'] = peak
            if status != 'OK':
                raise RuntimeError(value)
            if archive is not None:
                row['checked_transport_packet'] = value
                value = _load_checked_forward(archive, value)
            row['status'] = 'RETURNED'
            row['actual_response_passes'] = getattr(value, 'response_passes', 0)
            row['forward_calls'] = int(kind == 'forward')
            row['returned_status'] = str(getattr(value, 'status', 'RETURNED'))
            if archive is not None:
                _archive_value(archive, 'after-transport', value)
            _freeze_received(value)
            if archive is not None:
                _archive_value(archive, 'after-freeze', value)
                if sf._hash(value) != row['checked_transport_packet']['content_identity']:
                    raise RuntimeError('FORWARD_IMMUTABLE_FREEZE_CONTENT_MISMATCH')
            return value
        except BaseException as exc:
            row['status'] = 'FAILED'; row['failure'] = type(exc).__name__+':'+str(exc)
            raise
        finally:
            if worker is not None and worker.is_alive():
                worker.kill(); worker.join()
            if parent is not None:
                parent.close(); child.close()
            if archive_created:
                row['archive_index'] = {p.name: dict(bytes=p.stat().st_size,
                    sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(archive.iterdir()) if p.is_file()}
                _write(archive/'index.json', row['archive_index'])
            row['exponential_actions'] = 0 if actions is None else actions.value
            row['wall_s'] = time.monotonic()-start
            self.save()



def _outer_marginal(poly, response):
    lo, hi = pc._coefficient_bounds(response.weights, response.coefficient_allowances)
    evidence = tuple(pc._solve(poly, c, response.settings) for c in (lo, -hi))
    interval = None
    if all(e.status == 'CHECKED' for e in evidence):
        interval = (evidence[0].checked_dual_lower_kg, -evidence[1].checked_dual_lower_kg)
    return dict(outer_interval_kg=interval, status='OUTER_ONLY_NOT_REPLAYED_OR_CLAIMED_ATTAINED',
                evidence=pc._json_value(evidence, False, False))


def sensitivity(levels):
    rows = []
    for i, j, name in ((0, 1, 'timestep-.02-.01'), (1, 2, 'timestep-.01-.005'), (0, 3, 'mesh-N400-N800')):
        for query in ('unconditioned', 'conditioned'):
            a, b = levels[i][query], levels[j][query]
            row = dict(comparison=name, query=query,
                interpretation='DISCRETIZATION_SENSITIVITY_NOT_CONTINUUM_CERTIFICATE',
                compatibility=(a['compatibility'], b['compatibility']),
                decisions=(a['decision'], b['decision']), qualification=(a['bounds'], b['bounds']))
            if a['outer_interval_kg'] is not None and b['outer_interval_kg'] is not None:
                x, y = a['outer_interval_kg'], b['outer_interval_kg']
                row['endpoint_changes_kg'] = [pc._rounded(pc._q(v)-pc._q(u)) for u, v in zip(x, y)]
                row['width_change_kg'] = pc._rounded(pc._q(y[1])-pc._q(y[0])-pc._q(x[1])+pc._q(x[0]))
            if a['bounds'] == b['bounds'] == 'QUALIFIED':
                for sense in ('minimum', 'maximum'):
                    x, y = a[sense]['interval_kg'], b[sense]['interval_kg']
                    row[sense+'_change_bracket_kg'] = (pc._rounded(pc._q(y[0])-pc._q(x[1]), -1),
                                                       pc._rounded(pc._q(y[1])-pc._q(x[0]), 1))
            rows.append(row)
    return rows


def execute(budget):
    """One fixed campaign. Every native attempt is charged before launch."""
    evidence = budget.evidence
    if budget.data['executions']:
        raise RuntimeError('CAMPAIGN_ALREADY_STARTED_USE_RETAINED_EVIDENCE')
    a, b, u = fixture()
    generator = generating_state(u)
    paths = (Path(cc.__file__), Path(pc.__file__), Path(se.__file__), Path(sf.__file__), Path(__file__))
    record = dict(task=TASK, disposition='IMPLEMENTED_QUALIFICATION_INCOMPLETE', levels=[],
        code_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        PHYSICAL_VALIDATION='NOT_ESTABLISHED', orientation=cc.ORIENTATION,
        environment=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
            threads={k: os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS')}),
        reused_response_calls=0, fresh_response_calls=0)
    _write(evidence/'synthetic-inputs-full.json', pc._json_value(dict(original_U=u, generating_state=generator,
                                                                  plan_a=a, plan_b=b), True, False))
    original_pc_lp, original_se_lp, original_forward = pc.linprog, se.linprog, sf.simulate_stateful_fv
    lp_index = forward_index = 0
    level_label = 'generator'
    def lp(*args, **kwargs):
        nonlocal lp_index
        lp_index += 1
        return budget.run(f'{level_label}-LP-{lp_index:03d}', 'lp', 0, lambda: original_pc_lp(*args, **kwargs))
    def forward(**kwargs):
        nonlocal forward_index
        forward_index += 1
        return budget.run(f'{level_label}-forward-{forward_index:02d}', 'forward', 1,
                          lambda: original_forward(**kwargs), forward_inputs=kwargs)
    pc.linprog = se.linprog = lp
    sf.simulate_stateful_fv = forward
    try:
        generated = forward(plan=a, initial_state=generator, observation_times_s=(7., 10., 12.),
                            fraction_windows_s=EARLY, stop_time_s=BRANCH)
        _check_generation(generated)
        _write(evidence/'generator-full.json', pc._json_value(generated, True, True))
        centers = tuple(f.solute_kg for f in generated.fractions)
        d = .01*u.inventory_scale_kg
        bands = tuple((max(0., s-d), s+d) for s in centers)
        freeze = dict(centers_kg=centers, bands_kg=bands, half_width_kg=d,
            label='SYNTHETIC_TEST_ASSUMPTION_NOT_ASSAY_PRECISION', original_U_identity=u.identity_sha256,
            generator_state_identity=generator.identity_sha256, generation_plan_identity=a.identity_sha256,
            generator_windows=EARLY, generator_stop_s=BRANCH, epsilon_kg=EPSILON_KG, delta_kg=DELTA_KG,
            target_window_s=TARGET)
        _write(evidence/'frozen-bands.json', freeze)  # Before ANY future response.
        freeze_hash = hashlib.sha256((evidence/'frozen-bands.json').read_bytes()).hexdigest()
        record.update(frozen_bands=freeze, frozen_bands_sha256=freeze_hash)
        for n, h in LEVELS:
            level_label = f'N{n}-h{h:g}'
            pa, pb = (sf.FVPlan(p.temperature_history, p.flow_history, p.t_span_s,
                               sf.FVSettings(cells=n, h_max_s=h)) for p in (a, b))
            responses = []
            for index, (plan, window) in enumerate(((pa, EARLY[0]), (pa, EARLY[1]), (pa, TARGET), (pb, TARGET))):
                native = budget.run(f'{level_label}-response-{index}', 'response', 2,
                    lambda p=plan, w=window: se.build_delivery_response(p, solute='caffeine', grind=1.7, window_s=w))
                record['fresh_response_calls'] += 1
                _write(evidence/f'{level_label}-response-{index}.json', pc._json_value(native, True, True))
                responses.append(native if n == 400 else pc.pull_back_equal_children(native, u))
            ra, rb = responses[-2:]
            obs = tuple(pc.FVFractionObservation(f'early-{j+1}', r, band,
                'SYNTHETIC_FROZEN_BAND_SHA256:'+freeze_hash) for j, (r, band) in enumerate(zip(responses, bands)))
            row = dict(label=level_label, cells=n, h_s=h,
                mapping='NATIVE' if n == 400 else 'EXPLICIT_EQUAL_CHILD_PULLBACK_AND_LIFT')
            for name, observations in (('unconditioned', ()), ('conditioned', obs)):
                kw = dict(branch_time_s=BRANCH, epsilon_kg=EPSILON_KG, delta_kg=DELTA_KG,
                          comparison_basis='MATCHED_COLLECTED_VOLUME')
                query = (cc.bound_common_past_contrast(pc.condition_on_fractions(u, pa, observations), ra, rb, **kw)
                    if n == 400 else cc.bound_mapped_common_past_contrast(u, ra, rb, observations=observations, **kw))
                result = cc.replay_common_past_extrema(query)
                (evidence/f'{level_label}-{name}-full.json').write_text(result.to_json(include_arrays=True, include_timing=True)+'\n')
                row[name] = json.loads(result.to_json())
                poly = result.core.outer if result.core is not None else pc._base_polytope(u)
                row[name+'_supporting_marginals'] = dict(A=_outer_marginal(poly, ra), B=_outer_marginal(poly, rb))
            record['levels'].append(row)
            _write(evidence/'results.json', record)
            if hashlib.sha256((evidence/'frozen-bands.json').read_bytes()).hexdigest() != freeze_hash:
                raise RuntimeError('FROZEN_BANDS_CHANGED')
        record['sensitivity'] = sensitivity(record['levels'])
        if all(row[name]['bounds'] == 'QUALIFIED' for row in record['levels'] for name in ('unconditioned', 'conditioned')):
            record['disposition'] = 'REPRESENTATIVE_FIXED_OPERATOR_QUERIES_QUALIFIED'
    except BaseException as exc:
        record['termination'] = type(exc).__name__+':'+str(exc)
        raise
    finally:
        pc.linprog, se.linprog, sf.simulate_stateful_fv = original_pc_lp, original_se_lp, original_forward
        record.update(lp_invocations=lp_index, forward_invocations=forward_index)
        _write(evidence/'results.json', record)
        budget.save()
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    parser.add_argument('--correction', choices=('007-prefix-diagnostic-v1', '007-joint-witness-v1', '007-transport-validation-v1'))
    args = parser.parse_args(argv)
    if any(os.environ.get(k) != '1' for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS')):
        parser.error('All BLAS/OpenMP thread settings must be 1')
    saved = dependencies = None
    if args.correction:
        from tools import pannusch_common_past_correction as correction_tools
        saved = correction_tools.verified_inputs(args.output)
        dependencies = dict(artifacts=json.loads((correction_tools.DOCS/'EXTERNAL_EVIDENCE_INDEX.json').read_text())['artifacts'],
            source_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                (Path(cc.__file__), Path(pc.__file__), Path(se.__file__), Path(sf.__file__), Path(__file__), Path(correction_tools.__file__))})
    if args.correction == '007-transport-validation-v1':
        dependencies['correction_index_sha256'] = correction_tools.sha(correction_tools.DOCS/'CORRECTION_EXTERNAL_EVIDENCE_INDEX.json')
    budget = Budget(args.output, correction=args.correction, dependencies=dependencies)
    try:
        if args.correction == '007-prefix-diagnostic-v1':
            result = correction_tools.prefix_diagnostic(saved, budget)
        elif args.correction == '007-joint-witness-v1':
            result = correction_tools.correct_witnesses(saved, budget)
        elif args.correction == '007-transport-validation-v1':
            result = correction_tools.validate_archived_transport(saved, budget)
        else:
            result = execute(budget)
        print(result['disposition'])
        return 0 if result['disposition'] == 'REPRESENTATIVE_FIXED_OPERATOR_QUERIES_QUALIFIED' else 1
    except Exception as exc:
        print(type(exc).__name__+':'+str(exc))
        return 1
    finally:
        budget.lock.close()


if __name__ == '__main__':
    raise SystemExit(main())
