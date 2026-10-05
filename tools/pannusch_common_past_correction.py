"""007 correction evidence loaders and diagnostics; no new scientific query."""
from __future__ import annotations

from dataclasses import fields
import hashlib
import json
from pathlib import Path

import numpy as np

from puckworks.models.pannusch2024 import common_past_contrast as cc, prefix_conditioned as pc, state_envelope as se, stateful_fv as sf

DOCS = Path('docs/analysis/model_pannusch2024_common_past_contrast_007')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verified_inputs(evidence):
    index = json.loads((DOCS/'EXTERNAL_EVIDENCE_INDEX.json').read_text())
    result = {}
    for name, expected in index['artifacts'].items():
        path = Path(evidence)/name
        if path.stat().st_size != expected['bytes'] or sha(path) != expected['sha256']:
            raise ValueError('HISTORICAL_EVIDENCE_HASH_MISMATCH:'+name)
        result[name] = json.loads(path.read_text())
    return result


def _tuple(value):
    return tuple(_tuple(v) for v in value) if isinstance(value, list) else value


def construct(cls, data, **overrides):
    """Deserialize only explicitly selected dataclasses, checking derived identities.

    Native plans are reconstructed from their COMPLETE archived histories; every
    compiled array and derived field must reproduce the archive exactly.
    """
    args = {}
    for f in fields(cls):
        if f.init and f.name in data:
            v = data[f.name]
            args[f.name] = np.array(v) if v is not None and 'np.ndarray' in str(f.type) else _tuple(v)
    args.update(overrides)
    obj = cls(**args)
    actual = pc._json_value(obj, True, True)
    for f in fields(cls):
        if not f.init and f.name in data and actual[f.name] != data[f.name]:
            raise ValueError('DERIVED_EVIDENCE_MISMATCH:'+cls.__name__+':'+f.name)
    return obj


def state(d):
    s = construct(sf.FVChemicalState, d)
    s.validate()
    return s


def plan(d):
    return construct(sf.FVPlan, d,
        temperature_history=construct(sf.TemperatureHistory, d['temperature_history']),
        flow_history=construct(sf.FlowHistory, d['flow_history']), settings=construct(sf.FVSettings, d['settings']))


def state_set(d):
    return construct(se.FVChemicalStateSet, d, lower=state(d['lower']), upper=state(d['upper']))


def response(d):
    return construct(se.FVDeliveryResponse, d, plan=plan(d['plan']), model=state(d['model']),
                     settings=construct(se.FVEnvelopeSettings, d['settings']))


def poly(d):
    return construct(pc._Polytope, d)


def lp(d):
    return construct(pc._LPEvidence, d, problem=poly(d['problem']),
        raw_residuals=None if d['raw_residuals'] is None else construct(pc._Residuals, d['raw_residuals']))


def core(d):
    return construct(pc._CoreResult, d, outer=poly(d['outer']), inner=poly(d['inner']), search=poly(d['search']),
        feasibility=lp(d['feasibility']), outer_optimizations=tuple(lp(e) for e in d['outer_optimizations']),
        inner_optimizations=tuple(lp(e) for e in d['inner_optimizations']))


def stage(u, inner, search, mass, raw, objective):
    residual = pc._residuals(inner, mass)
    sr = pc._residuals(search, mass)
    return dict(masses_kg=mass, residuals=residual, original_residuals=se._residuals(u, mass),
        search_residuals=sr, exact_active_rows=tuple(label for label, a, b in zip(inner.row_labels, inner.A, inner.b)
            if pc._dotq(a, mass) == pc._q(b)),
        row_slacks_kg=tuple(pc._rounded(pc._q(b)-pc._dotq(a, mass)) for a, b in zip(inner.A, inner.b)),
        mass_movement_kg=pc._rounded(sum(abs(pc._q(x)-pc._q(y)) for x, y in zip(mass, raw)), 1),
        signed_interval_kg=pc._prediction(objective, mass))


def diagnose_maxima(saved):
    from types import SimpleNamespace
    rows = []
    for name, d in saved.items():
        if not name.endswith('-full.json') or 'maximum' not in d:
            continue
        u = state_set(d['conditioned_set']['original'])
        c = core(d['core']) if d['core'] else None
        inner = c.inner if c else pc._base_polytope(u)
        search = c.search if c else inner
        w = d['maximum']['witness']
        raw = np.array(w['raw_optimizer_masses_kg'])
        obj = SimpleNamespace(weights=np.array(d['objective']['weights']),
                              coefficient_allowances=np.array(d['objective']['coefficient_allowances']))
        converted = (raw/u.capacities_m3)*u.capacities_m3
        projected_c = np.clip(raw/u.capacities_m3, se._concentrations(u.lower), se._concentrations(u.upper))
        projected = projected_c*u.capacities_m3
        old = w['repair_optimization']
        problem = poly(old['problem'])
        # Identify inconsistent individual row/box combinations exactly. This is
        # diagnostic evidence about SEARCH, never an original-set contradiction.
        impossible = []
        for label, a, b in zip(problem.row_labels, problem.A, problem.b):
            floor = sum(min(pc._q(x)*pc._q(l), pc._q(x)*pc._q(h)) for x, l, h in zip(a, problem.lower, problem.upper))
            if floor > pc._q(b):
                impossible.append(dict(row=label, lower_excess_kg=pc._rounded(floor-pc._q(b), 1)))
        rows.append(dict(query=name, row_labels=inner.row_labels, search_row_labels=search.row_labels,
            stages={key: stage(u, inner, search, m, raw, obj) for key, m in
                    (('raw', raw), ('round_trip', converted), ('box_projection', projected),
                     ('retained_state', se._concentrations(state(w['state']))*u.capacities_m3))},
            historical_repair_solver_status=old['solver_status'], historical_repair_iterations=old['iterations'],
            historical_repair_termination=old['termination'], impossible_search_rows=impossible,
            minimum_search_box_width_kg=float(np.min(problem.upper-problem.lower)),
            inward_margin_kg=1024*se.EPS*u.inventory_scale_kg))
    return rows


def legacy_witness(d):
    return construct(se.FVWitness, d, state=None if d['state'] is None else state(d['state']),
        original_residuals=construct(se.FVConstraintResiduals, d['original_residuals']),
        residuals=construct(se.FVConstraintResiduals, d['residuals']),
        replays=tuple(construct(se.FVReplay, r) for r in d['replays']))


def legacy_extremum(d):
    return construct(se.FVExtremum, d, witness=legacy_witness(d['witness']),
        optimization=construct(se.FVOptimizationEvidence, d['optimization'],
            settings=construct(se.FVEnvelopeSettings, d['optimization']['settings'])))


def legacy_result(d, u, a, b):
    return construct(se.FVEnvelopeResult, d, state_set=u, responses=(b, a),
        minimum=legacy_extremum(d['minimum']), maximum=legacy_extremum(d['maximum']))


def fresh_query(saved, name):
    """New validation/objective, hash-verified unchanged native numerical evidence."""
    from dataclasses import replace
    d = saved[name]
    level = name.split('-conditioned')[0].split('-unconditioned')[0]
    u = state_set(d['conditioned_set']['original'])
    responses = tuple(response(saved[f'{level}-response-{i}.json']) for i in range(4))
    for r in responses:
        r.validate()  # Native source/model/content checks before any reuse.
    if len(responses[0].model.edges_m) != len(u.lower.edges_m):
        responses = tuple(pc.pull_back_equal_children(r, u) for r in responses)
    a, b = responses[-2:]
    for r, key in ((a, 'response_a'), (b, 'response_b')):
        if pc._json_value(r, True, True) != d['objective'][key]:
            raise ValueError('TARGET_RESPONSE_REUSE_MISMATCH')
    observations = tuple(pc.FVFractionObservation(o['label'], responses[i], o['mass_interval_kg'], o['provenance'])
                         for i, o in enumerate(d['conditioned_set']['observations']))
    conditioned = (cc._MappedEmptySet(u, a.plan) if not observations and isinstance(a, pc.FVEqualChildPullback)
                   else pc.condition_on_fractions(u, a.plan, observations))
    if pc._json_value(conditioned, True, True) != d['conditioned_set']:
        raise ValueError('ORIGINAL_SET_OR_OBSERVATION_REUSE_MISMATCH')
    old = d['objective']['receipt']
    receipt, eps, delta = cc._validate(conditioned, a, b, old['branch_time_s'], d['epsilon_kg'], d['delta_kg'], old['comparison_basis'])
    objective = cc.FVSignedContrast(a, b, receipt)
    for key in ('weights', 'coefficient_allowances', 'subtraction_allowances'):
        if not np.array_equal(getattr(objective, key), d['objective'][key]):
            raise ValueError('SIGNED_OBJECTIVE_CHANGED')
    for f in fields(receipt):
        if f.name not in ('identity_sha256', 'algorithm_source_sha256'):
            if pc._json_value(getattr(receipt, f.name), True, True) != old[f.name]:
                raise ValueError('COMMON_PAST_DEPENDENCY_CHANGED:'+f.name)
    c = core(d['core']) if d['core'] else None
    legacy = legacy_result(d['legacy_b_a'], u, a, b) if d['legacy_b_a'] else None
    if c:
        bands, search = cc._bands(conditioned)
        for key, expected in (('outer', pc._intersect(pc._base_polytope(u), bands, inner=False)),
                              ('inner', pc._intersect(pc._base_polytope(u), bands, inner=True)),
                              ('search', pc._intersect(pc._base_polytope(u), search, inner=True))):
            if pc._json_value(getattr(c, key), True, True) != pc._json_value(expected, True, True):
                raise ValueError('JOINT_POLYTOPE_CHANGED')
        for e in c.outer_optimizations:
            checked = pc._weak_dual(e.problem, e.objective, e.projected_duals)[0]
            if checked != e.checked_dual_lower_kg or e.status != 'CHECKED':
                raise ValueError('REUSED_OUTER_CERTIFICATE_FAILED')
    result = cc.FVCommonPastBounds(conditioned, objective, eps, delta, core=c, legacy_b_a=legacy,
                                  outer_interval_kg=tuple(d['outer_interval_kg']))
    extrema = []
    inner = c.inner if c else pc._base_polytope(u)
    for i, sense in enumerate(('minimum', 'maximum')):
        old_w = d[sense]['witness']
        w = cc._existing_state(u, inner, state(old_w['state']), np.array(old_w['raw_optimizer_masses_kg']), objective)
        eout = c.outer_optimizations[i] if c else getattr(legacy, sense).optimization
        ein = c.inner_optimizations[i] if c else eout
        extrema.append(pc.FVConditionalExtremum(sense, None, None, eout, ein, w))
    return replace(result, minimum=extrema[0], maximum=extrema[1])


def prefix_differences(a, b, branch):
    k = int(np.flatnonzero(a.primary.times_s == branch)[0])
    x, y = a.raw_primary_masses_kg[:k+1, :-1], b.raw_primary_masses_kg[:k+1, :-1]
    idx = np.argwhere(x != y)
    first = None
    if len(idx):
        i, j = map(int, idx[0]); n = len(a.root_state.edges_m)-1
        xx, yy = float(x[i, j]), float(y[i, j])
        phase, cell = divmod(j, n)
        values = [float(getattr(f.primary, se.PHASES[phase]+'_cell_average_kg_m3')[i, cell]) for f in (a, b)]
        first = dict(primary_index=i, absolute_time_s=float(a.primary.times_s[i]), phase=se.PHASES[phase], cell=cell,
            values_kg=(xx, yy), difference_kg=xx-yy, local_scale_kg=max(abs(xx), abs(yy)),
            ulp_difference=abs(int(np.float64(xx).view(np.int64))-int(np.float64(yy).view(np.int64))),
            concentration_values_kg_m3=values, concentration_difference_kg_m3=values[0]-values[1],
            preceding_original_primary_steps=[f.plan.primary_steps[max(0, i-1)].tolist() for f in (a, b)])
    return dict(first_difference=first, differing_entries=len(idx), maximum_difference_kg=float(np.max(np.abs(x-y))),
        raw_trace_bitwise_equal=bool(np.array_equal(x, y)),
        branch_state_bitwise_equal=bool(np.array_equal(x[-1], y[-1])),
        concentration_view_bitwise_equal=all(np.array_equal(getattr(a.primary, p+'_cell_average_kg_m3')[:k+1],
            getattr(b.primary, p+'_cell_average_kg_m3')[:k+1]) for p in se.PHASES),
        outlet_increments_bitwise_equal=bool(np.array_equal(a.step_outlet_solute_kg[:k], b.step_outlet_solute_kg[:k])),
        volume_increments_bitwise_equal=bool(np.array_equal(a.step_volume_m3[:k], b.step_volume_m3[:k])),
        prefix_deliveries_kg=[float(f.primary.segment_outlet_solute_kg[k]) for f in (a, b)],
        prefix_volumes_m3=[float(f.primary.segment_volume_m3[k]) for f in (a, b)])


def prefix_diagnostic(saved, budget):
    from dataclasses import replace
    import pickle
    name = 'N400-h0.01-unconditioned-full.json'
    result = fresh_query(saved, name)
    original = sf.simulate_stateful_fv
    returned = []
    def forward(**kwargs):
        value = budget.run('failed-minimum-'+('A' if not returned else 'B'), 'forward', 1,
                           lambda: original(**kwargs), forward_inputs=kwargs)
        returned.append(value)
        return value
    sf.simulate_stateful_fv = forward
    try:
        replay = cc._paired_replay(result, result.minimum.witness)
    finally:
        sf.simulate_stateful_fv = original
    outputs = dict(query=name, historical_state_identity=saved[name]['minimum']['witness']['state']['identity_sha256'],
        new_receipt=result.receipt, replay=replay, historical_complete_trajectories='NOT_ARCHIVED_NOT_RECOVERABLE_FROM_HASHES')
    if len(returned) == 2:
        outputs['after_freeze'] = prefix_differences(*returned, result.receipt.branch_time_s)
        rows = budget.data['executions'][-2:]
        for label in ('before-transport', 'after-transport'):
            values = []
            for row in rows:
                path = budget.evidence/row['archive']/(label+'.pickle')
                if sha(path) != row['archive_index'][path.name]['sha256']:
                    raise ValueError('FRESH_ARCHIVE_HASH_MISMATCH')
                values.append(pickle.loads(path.read_bytes()))
            outputs[label] = prefix_differences(*values, result.receipt.branch_time_s)
        outputs['transport_raw_arrays_unchanged'] = all(np.array_equal(a.raw_primary_masses_kg, b.raw_primary_masses_kg)
            for a, b in zip(values, returned))
    from tools.pannusch_prefix_conditioned_verification import _write
    _write(budget.output/'diagnostic.json', pc._json_value(outputs, True, True))
    # Separate complete new result from original. No historical receipt is restamped.
    maximum = replace(result.maximum, witness=None)
    qualified = cc._finish_replays(result, (cc._qualify_extremum(result, result.minimum, replay), maximum))
    (budget.output/'minimum-result.json').write_text(qualified.to_json(include_arrays=True, include_timing=True)+'\n')
    return dict(disposition='IMPLEMENTED_QUALIFICATION_INCOMPLETE', diagnostic=outputs['after_freeze'])


def replay_receipt(d):
    def branch(row):
        return None if row is None else construct(pc.FVConditionedReplay, row,
            windows=tuple(construct(pc.FVWindowReplay, w) for w in row['windows']))
    return construct(cc.FVPairedReplay, d, branch_a=branch(d['branch_a']), branch_b=branch(d['branch_b']),
        legacy_receipts_b_a=tuple(construct(se.FVReplay, r) for r in d['legacy_receipts_b_a']))


def checked_replay_delta():
    """Exact function-text delta, in addition to preserved dependency source hashes."""
    import ast
    import subprocess
    old = subprocess.check_output(['git', 'show', '28fe6c36873fa52965b9413dd3ab7d2b6316a773:puckworks/models/pannusch2024/common_past_contrast.py'], text=True)
    new = Path(cc.__file__).read_text()
    def bodies(s):
        lines = s.splitlines(keepends=True)
        return {n.name: ''.join(lines[n.lineno-1:n.end_lineno]) for n in ast.parse(s).body if isinstance(n, ast.FunctionDef)}
    x, y = bodies(old), bodies(new)
    names = ('_paired_replay', '_window_replay', '_legacy_receipt', '_signed_coefficients', '_decision')
    if any(x[k] != y[k] for k in names):
        raise ValueError('REUSED_REPLAY_COMPUTATION_CHANGED')
    protected = json.loads((DOCS/'PRESERVATION.json').read_text())['protected_sha256']
    if any(sha(p) != h for p, h in protected.items()):
        raise ValueError('PRESERVED_SOURCE_OR_HISTORICAL_EVIDENCE_CHANGED')
    return tuple((k, hashlib.sha256(y[k].encode()).hexdigest()) for k in names)


def reuse_minimum(result, historical, evidence_hash, delta):
    """Retain the OLD replay receipt, with a separate explicit old/new binding.

    Missing historical trajectory arrays remain a limitation. This reuse depends
    on the unchanged executed check code and retained checked result, not on new
    tests. Every retained state, response, row, window and prediction is rechecked.
    """
    from dataclasses import replace
    e = result.minimum
    old = historical['minimum']
    replay = replay_receipt(old['witness']['replay'])
    if (e.witness.status != 'CHECKED_REPLAY_REQUIRED' or old['status'] != 'QUALIFIED'
            or replay.status != 'CHECKED' or not replay.prefix_bitwise_equal
            or replay.maximum_prefix_mass_discrepancy_kg != 0.
            or e.witness.state.identity_sha256 != replay.state_identity
            or not np.array_equal(e.witness.masses_kg, old['witness']['masses_kg'])
            or e.witness.prediction_interval_kg != replay.signed_prediction_interval_kg
            or replay.receipt_identity != historical['objective']['receipt']['identity_sha256']):
        raise ValueError('HISTORICAL_REPLAY_DEPENDENCY_FAILED')
    qualified = cc._qualify_extremum(result, e, replay)
    if qualified.interval_kg != tuple(old['interval_kg']) or qualified.gap_kg != old['gap_kg']:
        raise ValueError('HISTORICAL_COMPLETE_GAP_CHANGED')
    binding = dict(kind='UNCHANGED_EXECUTED_CHECKS_AND_EXACT_INPUT_DEPENDENCIES', evidence_sha256=evidence_hash,
        old_receipt_identity=replay.receipt_identity, new_receipt_identity=result.receipt.identity_sha256,
        state_identity=replay.state_identity, original_set_identity=result.conditioned_set.original.identity_sha256,
        observation_identities=result.receipt.observation_identities, response_identities=(
            result.receipt.response_a_identity, result.receipt.response_b_identity), unchanged_functions=delta,
        original_coordinate_rows_sha256=sf._hash(result.core.inner if result.core else pc._base_polytope(result.conditioned_set.original)),
        reused_forward_calls=2, limitation='HISTORICAL_COMPLETE_TRAJECTORIES_NOT_ARCHIVED; OLD_RECEIPT_RETAINED_UNALTERED')
    return replace(result, minimum=qualified), binding


def correct_witnesses(saved, budget):
    from dataclasses import replace
    from tools.pannusch_prefix_conditioned_verification import _write
    from tools.pannusch_common_past_contrast_verification import LEVELS, sensitivity
    delta = checked_replay_delta()
    # Diagnostic arrays and elapsed analysis are appended; original result bundles
    # and the original resources.json remain immutable.
    start = __import__('time').monotonic()
    diagnoses = diagnose_maxima(saved)
    _write(budget.output/'maximum-diagnoses.json', pc._json_value(diagnoses, True, True))
    diagnosis_wall = __import__('time').monotonic()-start
    records = dict(disposition='IMPLEMENTED_QUALIFICATION_INCOMPLETE', PHYSICAL_VALIDATION='NOT_ESTABLISHED',
        levels=[], bindings=[], unchanged_functions=delta, diagnostic_wall_s=diagnosis_wall,
        response_reuse=16, backward_passes_reused=32, fresh_backward_passes=0,
        original_campaign='PRESERVED_UNCHANGED', unresolved_prefix='HISTORICAL_B_TRACE_UNAVAILABLE_CAUSE_NOT_ESTABLISHED')
    original_lp, original_forward = pc.linprog, sf.simulate_stateful_fv
    lp_count = forward_count = 0
    current = 'initial'
    def bounded_lp(*args, **kwargs):
        nonlocal lp_count
        lp_count += 1
        return budget.run(f'{current}-LP-{lp_count}', 'lp', 0, lambda: original_lp(*args, **kwargs))
    def bounded_forward(**kwargs):
        nonlocal forward_count
        forward_count += 1
        return budget.run(f'{current}-forward-{forward_count}', 'forward', 1,
                          lambda: original_forward(**kwargs), forward_inputs=kwargs)
    pc.linprog, sf.simulate_stateful_fv = bounded_lp, bounded_forward
    try:
        diagnostic_query = fresh_query(saved, 'N400-h0.02-conditioned-full.json')
        failure = saved['N400-h0.02-conditioned-full.json']['maximum']['witness']['repair_optimization']
        old_problem = poly(failure['problem'])
        current = 'original-inward-problem-diagnostic'
        proposal = cc._joint_proposal(diagnostic_query.conditioned_set.original, old_problem,
            diagnostic_query.core.inner_optimizations[1], diagnostic_query.objective, previous=None)
        records['original_inward_problem_diagnostic'] = pc._json_value(proposal, False, False)
        _write(budget.output/'original-inward-problem-diagnostic-full.json', pc._json_value(proposal, True, True))
        for n, h in LEVELS:
            label = f'N{n}-h{h:g}'
            row = dict(label=label, cells=n, h_s=h)
            for query in ('unconditioned', 'conditioned'):
                current = f'{label}-{query}'
                name = current+'-full.json'
                result = fresh_query(saved, name)
                u, obj = result.conditioned_set.original, result.objective
                if result.legacy_b_a:
                    inner = pc._base_polytope(u)
                    legacy = result.legacy_b_a
                    low, high = pc._coefficient_bounds(obj.weights, obj.coefficient_allowances)
                    for i, sense in enumerate(('minimum', 'maximum')):
                        opt = getattr(legacy, sense).optimization
                        y = opt.inequality_duals*opt.objective_scale
                        lower = pc._weak_dual(inner, (low, -high)[i], y)[0]
                        stored = (result.outer_interval_kg[0], -result.outer_interval_kg[1])[i]
                        if lower < stored:
                            raise ValueError('LEGACY_OUTER_ORIGINAL_KG_CERTIFICATE_FAILED')
                    lw = legacy.maximum.witness
                    proposal = pc._LPEvidence(inner, -obj.weights, raw_masses_kg=lw.optimizer_masses_kg)
                    w = cc._candidate(u, inner, proposal, obj, legacy=lw)
                else:
                    inner = result.core.inner
                    proposal = result.core.inner_optimizations[1]
                    old_failure = saved[name]['maximum']['witness']
                    previous = construct(pc.FVConditionedWitness, old_failure,
                        state=state(old_failure['state']), raw_residuals=construct(pc._Residuals, old_failure['raw_residuals']),
                        final_residuals=construct(pc._Residuals, old_failure['final_residuals']),
                        original_set_residuals=construct(se.FVConstraintResiduals, old_failure['original_set_residuals']),
                        repair_optimization=lp(old_failure['repair_optimization']))
                    w = cc._joint_proposal(u, inner, proposal, obj, previous=previous, search=result.core.search)
                result = replace(result, maximum=replace(result.maximum, witness=w))
                if current == 'N400-h0.01-unconditioned':
                    old_replay = replay_receipt(saved[name]['minimum']['witness']['replay'])
                    result = replace(result, minimum=replace(result.minimum,
                        witness=replace(result.minimum.witness, status='UNRESOLVED', replay=old_replay,
                            termination='HISTORICAL_PREFIX_DISCREPANCY_CAUSE_UNRESOLVED')))
                else:
                    result, binding = reuse_minimum(result, saved[name], sha(budget.evidence/name), delta)
                    records['bindings'].append(dict(query=current, **binding))
                result = cc.replay_common_past_extrema(result)
                (budget.output/(current+'-full.json')).write_text(result.to_json(include_arrays=True, include_timing=True)+'\n')
                row[query] = json.loads(result.to_json())
                row[query+'_before'] = {sense: dict(status=saved[name][sense]['status'], gap_kg=saved[name][sense]['gap_kg'])
                                       for sense in ('minimum', 'maximum')}
                # Supporting marginals are unchanged checked outer-only evidence.
                original_row = next(r for r in saved['results.json']['levels'] if r['label'] == label)
                row[query+'_supporting_marginals'] = original_row[query+'_supporting_marginals']
            records['levels'].append(row)
            _write(budget.output/'results.json', records)
        records['sensitivity'] = sensitivity(records['levels'])
        if all(r[q]['bounds'] == 'QUALIFIED' for r in records['levels'] for q in ('unconditioned', 'conditioned')):
            records['disposition'] = 'REPRESENTATIVE_FIXED_OPERATOR_QUERIES_QUALIFIED'
    finally:
        pc.linprog, sf.simulate_stateful_fv = original_lp, original_forward
        records.update(fresh_forward_calls=forward_count, fresh_lp_calls=lp_count)
        _write(budget.output/'results.json', records)
        budget.save()
    return records


def validate_archived_transport(saved, budget):
    """Recheck two affected paired receipts from COMPLETE pre-transport outputs.

    No propagation/optimizer is launched. The original native executions remain
    charged. All four complete input identities must match the replay requests.
    """
    from dataclasses import replace
    import pickle
    from tools.pannusch_common_past_contrast_verification import sensitivity
    from tools.pannusch_prefix_conditioned_verification import _freeze_received, _write
    index = json.loads((DOCS/'CORRECTION_EXTERNAL_EVIDENCE_INDEX.json').read_text())['artifacts']
    def archived(relative, *, as_json=False):
        path = budget.evidence/relative
        expected = index[relative]
        data = path.read_bytes()
        if len(data) != expected['bytes'] or hashlib.sha256(data).hexdigest() != expected['sha256']:
            raise ValueError('ARCHIVE_DEPENDENCY_HASH_MISMATCH:'+relative)
        return json.loads(data) if as_json else pickle.loads(data)
    previous = 'corrections/007-joint-witness-v1/'
    record = archived(previous+'results.json', as_json=True)
    record['archive_transport_revalidation'] = []
    delta = checked_replay_delta()
    original_forward = sf.simulate_stateful_fv
    for query, directories in (
        ('unconditioned', ('118-N400-h0.005-unconditioned-forward-9', '119-N400-h0.005-unconditioned-forward-10')),
        ('conditioned', ('121-N400-h0.005-conditioned-forward-11', '122-N400-h0.005-conditioned-forward-12'))):
        name = 'N400-h0.005-'+query+'-full.json'
        retained = archived(previous+name, as_json=True)
        result = fresh_query(saved, name)
        u = result.conditioned_set.original
        inner = result.core.inner if result.core else pc._base_polytope(u)
        old = retained['maximum']['witness']
        witness = cc._existing_state(u, inner, state(old['state']), np.array(old['raw_optimizer_masses_kg']), result.objective)
        if (witness.status != 'CHECKED_REPLAY_REQUIRED' or not np.array_equal(witness.masses_kg, old['masses_kg'])
                or witness.prediction_interval_kg != tuple(old['prediction_interval_kg'])):
            raise ValueError('ARCHIVED_MAXIMUM_STATE_DEPENDENCY_CHANGED')
        result = replace(result, maximum=replace(result.maximum, witness=witness))
        result, minimum_binding = reuse_minimum(result, saved[name], sha(budget.evidence/name), delta)
        used = []
        def cached_forward(**kwargs):
            if len(used) >= 2:
                raise ValueError('ARCHIVED_PAIRED_REPLAY_COUNT')
            directory = previous+directories[len(used)]+'/'
            inputs = archived(directory+'inputs.pickle')
            if sf._hash(inputs) != sf._hash(kwargs):
                raise ValueError('COMPLETE_ARCHIVED_FORWARD_INPUT_MISMATCH')
            forward = archived(directory+'before-transport.pickle')
            before = sf._hash(forward)
            _freeze_received(forward)
            if sf._hash(forward) != before:
                raise ValueError('ARCHIVED_CONTENT_CHANGED_WHEN_FROZEN')
            used.append(dict(directory=directory, input_identity=sf._hash(inputs), content_identity=before,
                input_sha256=index[directory+'inputs.pickle']['sha256'],
                output_sha256=index[directory+'before-transport.pickle']['sha256']))
            return forward
        sf.simulate_stateful_fv = cached_forward
        try:
            revised = cc.replay_common_past_extrema(result)
        finally:
            sf.simulate_stateful_fv = original_forward
        if len(used) != 2:
            raise ValueError('ARCHIVED_PAIRED_REPLAY_INCOMPLETE')
        binding = dict(query=query, native_executions=used, fresh_propagations=0, fresh_lp_calls=0,
            reused_forward_executions=2, original_paired_receipt=retained['maximum']['witness']['replay'],
            prior_result_sha256=index[previous+name]['sha256'], new_receipt_identity=revised.receipt.identity_sha256,
            repair_provenance='UNCHANGED_STATE_AND_RAW_VECTOR; COMPLETE_PRIOR_REPAIR_RECEIPT_RETAINED_BY_PRIOR_RESULT_HASH',
            minimum_reuse_binding=minimum_binding, check='ALL_PAIRED_REPLAY_CHECKS_REEXECUTED_ON_VERIFIED_PRETRANSPORT_OUTPUTS')
        record['archive_transport_revalidation'].append(binding)
        row = next(x for x in record['levels'] if x['label'] == 'N400-h0.005')
        row[query] = json.loads(revised.to_json())
        (budget.output/name).write_text(revised.to_json(include_arrays=True, include_timing=True)+'\n')
    record['sensitivity'] = sensitivity(record['levels'])
    record['disposition'] = 'IMPLEMENTED_QUALIFICATION_INCOMPLETE'
    _write(budget.output/'results.json', record)
    _write(budget.output/'revalidation-bindings.json', record['archive_transport_revalidation'])
    budget.save()
    return record
