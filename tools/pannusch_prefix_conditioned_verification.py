"""Separate bounded 006 synthetic campaign; never invoked at full mesh in pytest.

Source-derived results: Pannusch/Schmieder, 10.17632/y2tz67f6ry.1,
CC-BY-NC-3.0, separate from first-party software licensing.
"""
from __future__ import annotations

import argparse
from dataclasses import fields, is_dataclass
import fcntl
import hashlib
import json
import math
import multiprocessing as mp
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time

import numpy as np
import scipy

from puckworks.models.pannusch2024 import prefix_conditioned as pc, state_envelope as se, stateful_fv as sf

TASK = 'MODEL-PANNUSCH2024-PREFIX-CONDITIONED-006'
EARLY = ((7., 10.), (10., 12.))
TARGET = (12., 17.)
EPSILON_KG = 1e-9


def fixture(n=400, h=.02):
    """Copy ONLY 005 history A and U. No observations or future evaluations."""
    plan = sf.FVPlan(sf.TemperatureHistory.linear_celsius((7, 11, 17), (80, 96, 87)),
        sf.FlowHistory((7, 10, 17), (1.2e-6, 2.7e-6, 1.8e-6), 'linear'),
        (7, 17), sf.FVSettings(cells=n, h_max_s=h))
    edges = np.linspace(0., .015, n+1)
    x = (edges[:-1]+edges[1:])/(2*.015)
    def state(c):
        return sf.FVChemicalState.from_cell_averages(solute='caffeine', grind=1.7, time_s=7.,
            edges_m=edges, liquid_kg_m3=c[0], fine_kg_m3=c[1], coarse_kg_m3=c[2])
    lower, upper = state(np.array([.2+.5*x, .2+.4*x, .5+.3*x])), state(np.array([3+3*x, 8-3*x, 8+2*x]))
    u = se.FVChemicalStateSet(lower, upper, (8e-5, 1.2e-4), '005_EXPLICIT_SYNTHETIC_U_REUSED_006',
        ((8e-6, 3e-5), (1e-5, 5e-5), (2e-5, 8e-5)))
    return plan, u


def generating_state(u):
    """Deterministic interior construction from U alone, not an inferred state.

    Interpolate each phase between its original lower/upper fields to reach
    the midpoint of its feasible phase inventory interval; interpolate phase
    targets toward their feasible lower/upper values to reach the total midpoint.
    """
    n = len(u.lower_masses_kg)//3
    low = np.array([math.fsum(u.lower_masses_kg[j*n:(j+1)*n]) for j in range(3)])
    high = np.array([math.fsum(u.upper_masses_kg[j*n:(j+1)*n]) for j in range(3)])
    pl = np.maximum(low, np.array(u.phase_inventory_kg)[:, 0])
    ph = np.minimum(high, np.array(u.phase_inventory_kg)[:, 1])
    phase = (pl+ph)/2
    total = sum(u.total_inventory_kg)/2
    direction = ph if total > sum(phase) else pl
    if sum(phase) != total:
        phase += (total-sum(phase))/(sum(direction)-sum(phase))*(direction-phase)
    fraction = (phase-low)/(high-low)
    c = se._concentrations(u.lower).reshape(3, n)+fraction[:, None]*(
        se._concentrations(u.upper)-se._concentrations(u.lower)).reshape(3, n)
    state = sf.FVChemicalState.from_cell_averages(solute=u.lower.solute, grind=u.lower.grind,
        time_s=u.lower.time_s, edges_m=u.lower.edges_m,
        liquid_kg_m3=c[0], fine_kg_m3=c[1], coarse_kg_m3=c[2])
    mass = se._concentrations(state)*u.capacities_m3
    if not pc._residuals(pc._base_polytope(u), mass).feasible:
        raise RuntimeError('SYNTHETIC_GENERATOR_NOT_IN_U')
    return state


def _freeze_received(obj):
    """Pickle transports arrays; restore immutable byte-backed storage on receipt."""
    if is_dataclass(obj):
        se._seal(obj)
        for f in fields(obj):
            _freeze_received(getattr(obj, f.name))
    elif isinstance(obj, (tuple, list)):
        for v in obj:
            _freeze_received(v)


def _child(pipe, callback, actions):
    original_se, original_fv = se.expm_multiply, sf.fv.expm_multiply
    def counted_se(*a, **kw):
        actions.value += 1
        return original_se(*a, **kw)
    def counted_fv(*a, **kw):
        actions.value += 1
        return original_fv(*a, **kw)
    se.expm_multiply, sf.fv.expm_multiply = counted_se, counted_fv
    try:
        value = callback()
        pipe.send(('OK', value, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
    except BaseException as exc:
        pipe.send(('ERROR', type(exc).__name__+':'+str(exc), resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
    finally:
        pipe.close()


class Budget:
    """One task receipt, using the existing Git-common-directory accounting pattern.

    POSIX campaign tool. Each native call runs in a separate child with an
    external deadline; native hangs cannot suppress Python signal handling.
    """
    def __init__(self, evidence_dir):
        self.evidence = Path(evidence_dir).resolve()
        self.evidence.mkdir(parents=True, exist_ok=True)
        common = Path(subprocess.check_output(['git', 'rev-parse', '--git-common-dir'], text=True).strip()).resolve()
        self.path = common/'model-pannusch2024-prefix-conditioned-006-budget.json'
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
        self.prior_wall, self.start = self.data['wall_s'], time.monotonic()

    def save(self):
        self.data['wall_s'] = self.prior_wall+time.monotonic()-self.start
        text = json.dumps(self.data, sort_keys=True, indent=2, allow_nan=False)+'\n'
        tmp = self.path.with_suffix('.tmp'); tmp.write_text(text); tmp.replace(self.path)
        public = {k: v for k, v in self.data.items() if k != 'evidence_dir'}
        (self.evidence/'resources.json').write_text(json.dumps(public, sort_keys=True, indent=2, allow_nan=False)+'\n')

    def run(self, label, kind, units, callback, *, deadline_s=None, correction=None):
        self.save()
        if kind not in ('response', 'forward', 'lp'):
            raise ValueError('UNKNOWN_NUMERICAL_CALL')
        if type(units) is not int or units != (2 if kind == 'response' else 1 if kind == 'forward' else 0):
            raise ValueError('INVALID_PROPAGATION_RESERVATION')
        rows = self.data['executions']
        if sum(r['charged_propagations'] for r in rows)+units > 64:
            raise RuntimeError('PROPAGATION_LIMIT')
        if sum(r['kind'] == 'lp' for r in rows)+(kind == 'lp') > 160:
            raise RuntimeError('LP_LIMIT')
        if any(r['label'] == label for r in rows) and correction is None:
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
        context = mp.get_context('fork')
        parent, child = context.Pipe(duplex=False)
        actions = context.Value('q', 0, lock=False)
        worker = context.Process(target=_child, args=(child, callback, actions))
        start = time.monotonic()
        try:
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
            row['status'] = 'RETURNED'
            row['actual_response_passes'] = getattr(value, 'response_passes', 0)
            row['forward_calls'] = int(kind == 'forward')
            row['returned_status'] = str(getattr(value, 'status', 'RETURNED'))
            _freeze_received(value)
            return value
        except BaseException as exc:
            row['status'] = 'FAILED'; row['failure'] = type(exc).__name__+':'+str(exc)
            raise
        finally:
            if worker.is_alive():
                worker.kill(); worker.join()
            parent.close(); child.close()
            row['exponential_actions'] = actions.value
            row['wall_s'] = time.monotonic()-start
            self.save()


def _write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n')


def _check_generation(generated):
    if (generated.status not in ('COMPLETE', 'PLANNED_STOP') or not generated.integration_complete
            or generated.actual_end_s != 12. or len(generated.fractions) != 2
            or any(s != 'SUPPORTED' for s in generated.observation_status)
            or any(f.solute_kg is None or f.status not in
                   ('VALID_NUMERICAL_ZERO', 'NUMERICAL_ONLY_ACCURACY_NOT_ASSESSED')
                   for f in generated.fractions)):
        raise RuntimeError('SYNTHETIC_EARLY_GENERATION_FAILED')


def execute(budget, *, resume_generation_status_correction=False):
    evidence = budget.evidence
    correction = None
    if resume_generation_status_correction:
        rows = budget.data['executions']
        previous = json.loads((evidence/'results.json').read_text())
        if (len(rows) != 1 or rows[0]['label'] != 'generator-forward-01'
                or rows[0].get('returned_status') != 'PLANNED_STOP'
                or previous.get('termination') != 'RuntimeError:SYNTHETIC_EARLY_GENERATION_FAILED'
                or (evidence/'frozen-bands.json').exists()
                or (evidence/'generation-status-failure.json').exists()):
            raise RuntimeError('CORRECTION_REQUIRES_EXACT_PRE_BOUND_STATUS_FAILURE')
        _write(evidence/'generation-status-failure.json', previous)
        correction = 'PLANNED_STOP_STATUS_HANDLING_NO_NUMERICAL_CHANGE'
    plan, u = fixture()
    generator = generating_state(u)  # Chosen solely from U BEFORE any propagation.
    code_paths = [Path(pc.__file__), Path(__file__)]
    record = dict(task=TASK, disposition='IMPLEMENTED_QUALIFICATION_INCOMPLETE', levels=[],
        code_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in code_paths},
        fixture_authority='005 VERIFICATION.md history A and U only',
        fixture_authority_sha256=hashlib.sha256(Path('docs/analysis/model_pannusch2024_state_envelope_005/VERIFICATION.md').read_bytes()).hexdigest(),
        environment=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
            threads={k: os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS')}),
        PHYSICAL_VALIDATION='NOT_ESTABLISHED', allowance_contract=pc.CONTRACT)
    _write(evidence/'synthetic-inputs-full.json', pc._json_value(dict(original_U=u, generating_state=generator), True, False))
    _write(evidence/'results.json', record)
    original_pc_lp, original_se_lp = pc.linprog, se.linprog
    original_forward = sf.simulate_stateful_fv
    lp_index = forward_index = 0
    level_label = 'generator'
    def counted_lp(*args, **kw):
        nonlocal lp_index
        lp_index += 1
        return budget.run(f'{level_label}-LP-{lp_index:03d}', 'lp', 0, lambda: original_pc_lp(*args, **kw))
    def counted_forward(**kw):
        nonlocal forward_index
        forward_index += 1
        return budget.run(f'{level_label}-forward-{forward_index:02d}', 'forward', 1,
                          lambda: original_forward(**kw), correction=correction if level_label == 'generator' else None)
    pc.linprog = se.linprog = counted_lp
    sf.simulate_stateful_fv = counted_forward
    try:
        generated = counted_forward(plan=plan, initial_state=generator,
            observation_times_s=(7., 10., 12.), fraction_windows_s=EARLY, stop_time_s=12.)
        _check_generation(generated)
        centers = tuple(f.solute_kg for f in generated.fractions)
        d = .01*u.inventory_scale_kg
        bands = tuple((max(0., s-d), s+d) for s in centers)
        freeze = dict(centers_kg=centers, half_width_kg=d, bands_kg=bands,
            original_U_identity=u.identity_sha256, generating_state_identity=generator.identity_sha256,
            generation_plan_identity=plan.identity_sha256, generator_fraction_windows=EARLY,
            target_window=TARGET, epsilon_kg=EPSILON_KG, label='SYNTHETIC_TEST_ASSUMPTION_NOT_ASSAY_PRECISION',
            generating_exponential_actions=generated.exponential_applications)
        _write(evidence/'frozen-bands.json', freeze)  # BEFORE any target response/LP.
        freeze_hash = hashlib.sha256((evidence/'frozen-bands.json').read_bytes()).hexdigest()
        record['frozen_bands'] = freeze; record['frozen_bands_sha256'] = freeze_hash
        for n, h in ((400, .02), (400, .01), (400, .005), (800, .02)):
            level_label = f'N{n}-h{h:g}'
            current = sf.FVPlan(plan.temperature_history, plan.flow_history, plan.t_span_s,
                                sf.FVSettings(cells=n, h_max_s=h))
            responses = []
            for j, window in enumerate((*EARLY, TARGET)):
                native = budget.run(f'{level_label}-response-{j}', 'response', 2,
                    lambda w=window: se.build_delivery_response(current, solute='caffeine', grind=1.7, window_s=w))
                responses.append(native if n == 400 else pc.pull_back_equal_children(native, u))
            observations = tuple(pc.FVFractionObservation(f'early-{j+1}', r, band,
                'SYNTHETIC_FROZEN_BAND_SHA256:'+freeze_hash) for j, (r, band) in enumerate(zip(responses, bands)))
            conditioned = pc.condition_on_fractions(u, current, observations)
            query = pc.bound_future_delivery(conditioned, responses[-1], epsilon_kg=EPSILON_KG)
            result = pc.replay_conditioned_extrema(query)
            (evidence/(level_label+'-full.json')).write_text(result.to_json(include_arrays=True, include_timing=True)+'\n')
            compact = json.loads(result.to_json())
            record['levels'].append(dict(label=level_label, cells=n, h_s=h, result=compact,
                mapping='NATIVE_COARSE' if n == 400 else 'EXPLICIT_EQUAL_CHILD_PULLBACK_AND_LIFT_REPLAY'))
            _write(evidence/'results.json', record)
            if hashlib.sha256((evidence/'frozen-bands.json').read_bytes()).hexdigest() != freeze_hash:
                raise RuntimeError('FROZEN_BANDS_CHANGED')
        sensitivity = []
        levels = record['levels']
        for i, j, label in ((0, 1, 'temporal-.02-.01'), (1, 2, 'temporal-.01-.005'), (0, 3, 'mesh-N400-N800')):
            left, right = levels[i]['result'], levels[j]['result']
            row = dict(comparison=label, interpretation='DISCRETIZATION_SENSITIVITY_NOT_CONTINUUM_CERTIFICATE',
                compatibility=(left['compatibility'], right['compatibility']),
                qualification=(left['bounds'], right['bounds']))
            if all(v['conditioned_outer_interval_kg'] is not None for v in (left, right)):
                row['outer_endpoint_change_kg'] = [b-a for a, b in zip(left['conditioned_outer_interval_kg'], right['conditioned_outer_interval_kg'])]
                row['outer_width_change_kg'] = right['conditioned_width_kg']-left['conditioned_width_kg']
            if all(v['bounds'] == 'QUALIFIED' for v in (left, right)):
                for sense in ('minimum', 'maximum'):
                    a, b = left[sense]['interval_kg'], right[sense]['interval_kg']
                    row[sense+'_change_bracket_kg'] = (pc._rounded(pc._q(b[0])-pc._q(a[1]), -1),
                                                       pc._rounded(pc._q(b[1])-pc._q(a[0]), 1))
                row['status'] = 'QUALIFIED_FIXED_OPERATOR_ENDPOINT_COMPARISON_ONLY'
            else:
                row['status'] = 'SENSITIVITY_UNRESOLVED'
            sensitivity.append(row)
        record['sensitivity'] = sensitivity
        record['disposition'] = ('REPRESENTATIVE_FIXED_OPERATOR_QUALIFIED' if levels[0]['result']['bounds'] == 'QUALIFIED'
                                 else 'IMPLEMENTED_QUALIFICATION_INCOMPLETE')
    except BaseException as exc:
        record['termination'] = type(exc).__name__+':'+str(exc)
        raise
    finally:
        pc.linprog, se.linprog, sf.simulate_stateful_fv = original_pc_lp, original_se_lp, original_forward
        record['lp_invocations'] = lp_index
        record['forward_invocations'] = forward_index
        _write(evidence/'results.json', record)
        budget.save()
    print(record['disposition'])



def _restore_native(data):
    """Rehydrate retained full arrays, then verify the ORIGINAL native identity."""
    p = data['plan']; t = p['temperature_history']; q = p['flow_history']; m = data['model']
    plan = sf.FVPlan(sf.TemperatureHistory(tuple(t['times_s']), tuple(t['temperatures_K']), t['kind']),
        sf.FlowHistory(tuple(q['times_s']), tuple(q['flows_m3_s']), q['kind']),
        tuple(p['t_span_s']), sf.FVSettings(**p['settings']))
    model = sf.FVChemicalState.from_cell_averages(solute=m['solute'], grind=m['grind'], time_s=m['time_s'],
        edges_m=m['edges_m'], liquid_kg_m3=m['liquid_cell_average_kg_m3'],
        fine_kg_m3=m['fine_cell_average_kg_m3'], coarse_kg_m3=m['coarse_cell_average_kg_m3'])
    arguments = {f.name: data[f.name] for f in fields(se.FVDeliveryResponse) if f.init}
    arguments.update(plan=plan, model=model, settings=se.FVEnvelopeSettings(**data['settings']))
    for name in ('weights', 'coefficient_allowances'):
        arguments[name] = None if data[name] is None else np.array(data[name])
    response = se.FVDeliveryResponse(**arguments)
    response.validate()
    if (response.identity_sha256 != data['identity_sha256'] or plan.identity_sha256 != p['identity_sha256']
            or model.identity_sha256 != m['identity_sha256']):
        raise RuntimeError('RETAINED_NATIVE_RESPONSE_IDENTITY_MISMATCH')
    return response


def resume_repair_correction(budget):
    """One bounded correction: reuse native responses and bands, recheck witnesses.

    No response or generating trajectory is repeated. The failed four-level
    evidence is retained. All new LPs and witness trajectories share the receipt.
    """
    evidence = budget.evidence
    previous_bytes = (evidence/'results.json').read_bytes()
    previous = json.loads(previous_bytes)
    freeze_bytes = (evidence/'frozen-bands.json').read_bytes()
    freeze = json.loads(freeze_bytes)
    if (len(previous['levels']) != 4 or previous['disposition'] != 'IMPLEMENTED_QUALIFICATION_INCOMPLETE'
            or budget.data.get('joint_repair_correction_started')
            or hashlib.sha256(freeze_bytes).hexdigest() != previous['frozen_bands_sha256']):
        raise RuntimeError('CORRECTION_REQUIRES_RETAINED_FOUR_LEVEL_WITNESS_FAILURE')
    budget.data['joint_repair_correction_started'] = True; budget.save()
    unused, u = fixture()
    if u.identity_sha256 != freeze['original_U_identity']:
        raise RuntimeError('ORIGINAL_U_CHANGED')
    record = dict(previous, levels=[], disposition='IMPLEMENTED_QUALIFICATION_INCOMPLETE',
        correction='JOINT_BOUNDARY_RECONSTRUCTION_AND_SEARCH_SET_SEPARATION',
        previous_result_sha256=hashlib.sha256(previous_bytes).hexdigest(),
        reused_native_response_identities=[],
        code_sha256={Path(f).name: hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in (pc.__file__, __file__)})
    record.pop('sensitivity', None)
    original_pc_lp, original_se_lp, original_forward = pc.linprog, se.linprog, sf.simulate_stateful_fv
    lp_index = forward_index = 0
    label = ''
    def lp(*args, **kwargs):
        nonlocal lp_index
        lp_index += 1
        return budget.run(f'repair-{label}-LP-{lp_index:03d}', 'lp', 0,
                          lambda: original_pc_lp(*args, **kwargs), correction=record['correction'])
    def forward(**kwargs):
        nonlocal forward_index
        forward_index += 1
        return budget.run(f'repair-{label}-forward-{forward_index:02d}', 'forward', 1,
                          lambda: original_forward(**kwargs), correction=record['correction'])
    pc.linprog = se.linprog = lp; sf.simulate_stateful_fv = forward
    try:
        for old in previous['levels']:
            label = old['label']
            full = json.loads((evidence/(label+'-full.json')).read_text())
            data = [o['response'] for o in full['conditioned_set']['observations']]+[full['target']]
            native = [_restore_native(d.get('native', d)) for d in data]
            record['reused_native_response_identities'].extend(r.identity_sha256 for r in native)
            responses = native if old['cells'] == 400 else [pc.pull_back_equal_children(r, u) for r in native]
            observations = tuple(pc.FVFractionObservation(o['label'], r, tuple(band), o['provenance'])
                for o, r, band in zip(full['conditioned_set']['observations'], responses, freeze['bands_kg']))
            query = pc.bound_future_delivery(pc.condition_on_fractions(u, native[0].plan, observations),
                                            responses[-1], epsilon_kg=EPSILON_KG)
            if query.conditioned_outer_interval_kg != tuple(old['result']['conditioned_outer_interval_kg']):
                raise RuntimeError('CORRECTION_CHANGED_CHECKED_OUTER_ENDPOINTS')
            result = pc.replay_conditioned_extrema(query)
            (evidence/('corrected-'+label+'-full.json')).write_text(result.to_json(include_arrays=True, include_timing=True)+'\n')
            record['levels'].append(dict(label=label, cells=old['cells'], h_s=old['h_s'],
                mapping=old['mapping'], result=json.loads(result.to_json())))
            _write(evidence/'corrected-results.json', record)
        sensitivity = []
        levels = record['levels']
        for i, j, name in ((0, 1, 'temporal-.02-.01'), (1, 2, 'temporal-.01-.005'), (0, 3, 'mesh-N400-N800')):
            left, right = levels[i]['result'], levels[j]['result']
            row = dict(comparison=name, interpretation='DISCRETIZATION_SENSITIVITY_NOT_CONTINUUM_CERTIFICATE',
                compatibility=(left['compatibility'], right['compatibility']), qualification=(left['bounds'], right['bounds']))
            a, b = left['conditioned_outer_interval_kg'], right['conditioned_outer_interval_kg']
            row['outer_endpoint_change_kg'] = [y-x for x, y in zip(a, b)]
            row['outer_width_change_kg'] = right['conditioned_width_kg']-left['conditioned_width_kg']
            if all(r['bounds'] == 'QUALIFIED' for r in (left, right)):
                for sense in ('minimum', 'maximum'):
                    a, b = left[sense]['interval_kg'], right[sense]['interval_kg']
                    row[sense+'_change_bracket_kg'] = (pc._rounded(pc._q(b[0])-pc._q(a[1]), -1),
                                                       pc._rounded(pc._q(b[1])-pc._q(a[0]), 1))
                row['status'] = 'QUALIFIED_FIXED_OPERATOR_ENDPOINT_COMPARISON_ONLY'
            else:
                row['status'] = 'SENSITIVITY_UNRESOLVED'
            sensitivity.append(row)
        record['sensitivity'] = sensitivity
        record['disposition'] = ('REPRESENTATIVE_FIXED_OPERATOR_QUALIFIED'
                                if levels[0]['result']['bounds'] == 'QUALIFIED' else 'IMPLEMENTED_QUALIFICATION_INCOMPLETE')
    except BaseException as exc:
        record['termination'] = type(exc).__name__+':'+str(exc)
        raise
    finally:
        pc.linprog, se.linprog, sf.simulate_stateful_fv = original_pc_lp, original_se_lp, original_forward
        record['correction_lp_invocations'] = lp_index; record['correction_forward_invocations'] = forward_index
        _write(evidence/'corrected-results.json', record); budget.save()
    print(record['disposition'])

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-dir', required=True)
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--resume-generation-status-correction', action='store_true',
                        help='One reserved correction of the pre-bound PLANNED_STOP harness rejection.')
    parser.add_argument('--resume-joint-repair-correction', action='store_true',
                        help='One reserved repair correction reusing the retained responses and bands.')
    args = parser.parse_args()
    if args.resume_joint_repair_correction and args.resume_generation_status_correction:
        parser.error('Choose one named correction')
    for name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
        if os.environ.get(name) != '1':
            parser.error(name+' must be 1')
    if not args.worker:
        # The parent also bounds all certificate/reconstruction/JSON work, not
        # only the native child calls. The shared receipt blocks resets.
        common = Path(subprocess.check_output(['git', 'rev-parse', '--git-common-dir'], text=True).strip()).resolve()
        path = common/'model-pannusch2024-prefix-conditioned-006-budget.json'
        used = json.loads(path.read_text())['wall_s'] if path.exists() else 0.
        if used >= 1800:
            raise RuntimeError('AGGREGATE_WALL_LIMIT')
        subprocess.run([sys.executable, '-m', 'tools.pannusch_prefix_conditioned_verification',
                        *sys.argv[1:], '--worker'], check=True, timeout=1800-used)
        return
    budget = Budget(args.evidence_dir)
    if args.resume_joint_repair_correction:
        resume_repair_correction(budget)
    else:
        execute(budget, resume_generation_status_correction=args.resume_generation_status_correction)


if __name__ == '__main__':
    main()
