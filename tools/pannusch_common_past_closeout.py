"""Archive-only 007 consolidation: no propagation, response production or LP.

The owner-created pickle files are loaded only after checking a previously
committed index. Historical executions and their receipts are never rewritten.
"""
from __future__ import annotations

from contextlib import ExitStack
from dataclasses import fields, is_dataclass, replace
import hashlib
import json
import math
from pathlib import Path
import pickle
from unittest.mock import patch

import numpy as np

from tools import pannusch_common_past_correction as co
from puckworks.models.pannusch2024 import common_past_contrast as cc, prefix_conditioned as pc, state_envelope as se, stateful_fv as sf


def forbidden(*args, **kwargs):
    raise RuntimeError('ARCHIVE_ONLY_NO_NUMERICAL_EXECUTION_AUTHORIZED')


class IndexedArchive:
    def __init__(self, root, index):
        self.root, self.index, self.used = Path(root), index, {}

    def load(self, relative, *, as_json=False):
        path = self.root / relative
        if not path.resolve().is_relative_to(self.root.resolve()):
            raise ValueError('ARCHIVE_PATH_OUTSIDE_EVIDENCE')
        expected = self.index[relative]
        data = path.read_bytes()
        if len(data) != expected['bytes'] or hashlib.sha256(data).hexdigest() != expected['sha256']:
            raise ValueError('ARCHIVE_DEPENDENCY_HASH_MISMATCH:' + relative)
        self.used[relative] = expected
        return json.loads(data) if as_json else pickle.loads(data)


def _arrays(value, path=''):
    if isinstance(value, np.ndarray):
        yield path, value
    elif is_dataclass(value):
        for f in fields(value):
            yield from _arrays(getattr(value, f.name), path + '.' + f.name)
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from _arrays(v, path + '.' + k)
    elif isinstance(value, (tuple, list)):
        for i, v in enumerate(value):
            yield from _arrays(v, path + '.' + str(i))


def check_complete_report(forward, request):
    """Reexecute unchanged report arithmetic on archived raw values only.

This seam deliberately supports fresh complete runs with primary-aligned windows.
The reconstructed report is a consistency reference, never a replay substitute.
"""
    if not isinstance(forward, sf.StatefulFVResult):
        raise ValueError('ARCHIVE_FORWARD_TYPE')
    if sf._hash(forward) != forward.identity_sha256:
        raise ValueError('ARCHIVE_ORIGINAL_CONTENT_IDENTITY_MISMATCH')
    root, plan = request['initial_state'], request['plan']
    root.validate(); plan.validate()
    if (sf._hash(root) != sf._hash(forward.root_state) or sf._hash(plan) != sf._hash(forward.plan)
            or forward.mode != 'FRESH_STATE' or forward.parent_identity is not None
            or forward.start_index != 0 or forward.prior_outlet_terms_kg or forward.prior_volume_terms_m3
            or forward.status != 'COMPLETE' or forward.reason is not None
            or not forward.integration_complete or not forward.planned_horizon_complete
            or forward.actual_end_s != plan.t_span_s[1] or forward.requested_stop_s != plan.t_span_s[1]
            or tuple(request['observation_times_s']) != forward.observation_times_s):
        raise ValueError('ARCHIVED_COMPLETE_REQUEST_OR_SUPPORT_MISMATCH')
    for path, array in _arrays(forward):
        # The unchanged FV array freezer stores every numeric array as float64,
        # including the exportability mask. Validate the actual source format.
        expected_dtype = np.dtype('float64')
        if array.dtype != expected_dtype or not np.isfinite(array).all():
            raise ValueError('ARCHIVE_ARRAY_DTYPE_OR_FINITE:' + path)
    times, raw = forward.primary.times_s, forward.raw_primary_masses_kg
    if (not np.array_equal(times, plan.primary_times_s)
            or raw.shape != (len(times), 3 * plan.settings.cells + 1)
            or forward.raw_diagnostic_masses_kg.shape != (len(forward.raw_diagnostic_times_s), raw.shape[1])
            or forward.raw_quadrature.ndim != 2 or forward.raw_quadrature.shape[1] != 13
            or np.any(np.diff(forward.raw_diagnostic_times_s) <= 0)):
        raise ValueError('ARCHIVE_ARRAY_SHAPE_OR_SCHEDULE')
    system = sf.fv._System(root.solute, root.grind, plan.settings.cells)
    initial = np.r_[se._concentrations(root) * system.capacities, 0.]
    if not np.array_equal(raw[0], initial):
        raise ValueError('ARCHIVED_RAW_INITIAL_STATE_CHANGED')
    samples = dict(zip(forward.raw_diagnostic_times_s, forward.raw_diagnostic_masses_kg))
    if any(t not in samples or not np.array_equal(samples[t], y) for t, y in zip(times, raw)):
        raise ValueError('ARCHIVED_PRIMARY_DIAGNOSTIC_INCONSISTENCY')
    windows = tuple(request['fraction_windows_s'])
    parts = []
    for wi, (a, b) in enumerate(windows):
        if a not in times or b not in times or not a < b:
            raise ValueError('ARCHIVE_REVALIDATION_REQUIRES_PRIMARY_ALIGNED_WINDOW')
        ia, ib = int(np.searchsorted(times, a)), int(np.searchsorted(times, b))
        # Each existing raw accumulator is its preceding interval's local mass.
        parts.extend((wi, times[i], times[i+1], i, float(raw[i+1, -1])) for i in range(ia, ib))
    data = dict(times=times, states=raw, actual=forward.actual_end_s, samples=samples,
        quadrature=forward.raw_quadrature, window_parts=parts, reason=None,
        propagations=forward.propagations, exponential_applications=forward.exponential_applications,
        diagnostic_evaluations=forward.diagnostic_evaluations, elapsed_wall_s=forward.elapsed_wall_s)
    c = (initial[:-1] / system.capacities).reshape(3, system.n)
    checked = sf._report(data, root, plan, 0, plan.t_span_s[1], tuple(request['observation_times_s']),
        windows, 'FRESH_STATE', None, (), (), sf._inventory(*c, root.grind), float(np.max(np.abs(c))), system)
    if sf._hash(checked) != sf._hash(forward):
        changed = [f.name for f in fields(forward)
                   if f.name != 'identity_sha256' and sf._hash(getattr(checked, f.name)) != sf._hash(getattr(forward, f.name))]
        raise ValueError('ARCHIVE_FULL_REPORT_INCONSISTENCY:' + ','.join(changed))
    return dict(original_content_identity=forward.identity_sha256, full_report_recomputed=True,
                arrays={p: dict(dtype=a.dtype.str, shape=list(a.shape)) for p, a in _arrays(forward)})


class ArchivePair:
    """Exactly two individually indexed executions, matched to full requests."""
    def __init__(self, archive, directories, expected_sources):
        if len(directories) != 2 or len(set(directories)) != 2:
            raise ValueError('EXACTLY_TWO_DISTINCT_ARCHIVED_EXECUTIONS_REQUIRED')
        self.archive, self.directories, self.sources = archive, tuple(directories), expected_sources
        self.used = []
        self.failure = None

    def __call__(self, **request):
        try:
            return self._consume(request)
        except Exception as exc:
            self.failure = str(exc)
            raise

    def _consume(self, request):
        if len(self.used) == 2:
            raise ValueError('EXTRA_ARCHIVED_EXECUTION_REQUEST')
        directory = self.directories[len(self.used)] + '/'
        inputs = self.archive.load(directory + 'inputs.pickle')
        if set(request) != {'plan', 'initial_state', 'observation_times_s', 'fraction_windows_s'}:
            raise ValueError('UNSUPPORTED_ARCHIVED_REQUEST_FIELDS')
        if sf._hash(inputs) != sf._hash(request):
            raise ValueError('COMPLETE_ARCHIVED_FORWARD_INPUT_MISMATCH')
        outputs = []
        for label in ('inputs', 'before-transport', 'after-transport', 'after-freeze'):
            meta = self.archive.load(directory + label + '.json', as_json=True)
            indexed = self.archive.index[directory + label + '.pickle']
            if ({k: meta[k] for k in ('bytes', 'sha256')} != indexed
                    or meta['format'] != 'PYTHON_PICKLE_5_COMPLETE_OBJECT'
                    or meta['source_sha256'] != self.sources):
                raise ValueError('ARCHIVE_SOURCE_OR_METADATA_MISMATCH')
            if label != 'inputs':
                value = self.archive.load(directory + label + '.pickle')
                if value.identity_sha256 != sf._hash(value):
                    raise ValueError('ARCHIVE_ORIGINAL_CONTENT_IDENTITY_MISMATCH')
                outputs.append(value)
        if len({sf._hash(value) for value in outputs}) != 1:
            raise ValueError('ARCHIVE_TRANSPORT_OR_FREEZING_CHANGED_CONTENT')
        result = outputs[0]
        report = check_complete_report(result, request)
        from tools.pannusch_prefix_conditioned_verification import _freeze_received
        _freeze_received(result)
        if sf._hash(result) != report['original_content_identity']:
            raise ValueError('ARCHIVE_FREEZE_CHANGED_CONTENT')
        self.used.append(dict(directory=directory, input_identity=sf._hash(inputs),
            pre_post_transport_and_freeze_bitwise_content_equal=True, **report))
        return result

    def finish(self):
        if len(self.used) != 2 or self.failure is not None:
            raise ValueError('ARCHIVED_PAIRED_REPLAY_INCOMPLETE:' + str(self.failure))


def recheck_outer(result):
    if result.legacy_b_a is None:
        return tuple(pc._weak_dual(e.problem, e.objective, e.projected_duals)[0]
                     for e in result.core.outer_optimizations)
    inner = pc._base_polytope(result.conditioned_set.original)
    low, high = pc._coefficient_bounds(result.objective.weights, result.objective.coefficient_allowances)
    checked = []
    for i, sense in enumerate(('minimum', 'maximum')):
        opt = getattr(result.legacy_b_a, sense).optimization
        value = pc._weak_dual(inner, (low, -high)[i], opt.inequality_duals * opt.objective_scale)[0]
        stored = (result.outer_interval_kg[0], -result.outer_interval_kg[1])[i]
        if not math.isfinite(value) or value < stored:
            raise ValueError('LEGACY_OUTER_ORIGINAL_KG_CERTIFICATE_FAILED')
        checked.append(value)
    return tuple(checked)


def reuse_maximum(result, retained):
    """Reuse the exact existing paired receipt; recheck state and complete gap."""
    for f in fields(result.receipt):
        if f.name not in ('identity_sha256', 'algorithm_source_sha256'):
            if pc._json_value(getattr(result.receipt, f.name), True, True) != retained['objective']['receipt'][f.name]:
                raise ValueError('RETAINED_MAXIMUM_QUERY_IDENTITY_CHANGED:' + f.name)
    if pc._json_value(result.conditioned_set, True, True) != retained['conditioned_set']:
        raise ValueError('RETAINED_MAXIMUM_ORIGINAL_SET_OR_BANDS_CHANGED')
    for key in ('weights', 'coefficient_allowances', 'subtraction_allowances'):
        if not np.array_equal(getattr(result.objective, key), retained['objective'][key]):
            raise ValueError('RETAINED_MAXIMUM_OBJECTIVE_CHANGED')
    old = retained['maximum']
    u = result.conditioned_set.original
    inner = result.core.inner if result.core else pc._base_polytope(u)
    w = old['witness']
    witness = cc._existing_state(u, inner, co.state(w['state']), np.array(w['raw_optimizer_masses_kg']), result.objective)
    replay = co.replay_receipt(w['replay'])
    if (old['status'] != 'QUALIFIED' or witness.status != 'CHECKED_REPLAY_REQUIRED'
            or replay.status != 'CHECKED' or not replay.prefix_bitwise_equal
            or replay.maximum_prefix_mass_discrepancy_kg != 0.
            or replay.state_identity != witness.state.identity_sha256
            or replay.receipt_identity != retained['objective']['receipt']['identity_sha256']
            or not np.array_equal(witness.masses_kg, w['masses_kg'])
            or witness.prediction_interval_kg != replay.signed_prediction_interval_kg
            or tuple(retained['outer_interval_kg']) != result.outer_interval_kg):
        raise ValueError('RETAINED_MAXIMUM_DEPENDENCY_FAILED')
    for branch, target in ((replay.branch_a, result.objective.response_a), (replay.branch_b, result.objective.response_b)):
        if branch.plan_identity != target.plan.identity_sha256 or branch.windows[0].response_identity != target.identity_sha256:
            raise ValueError('RETAINED_MAXIMUM_PLAN_OR_RESPONSE_CHANGED')
    maximum = cc._qualify_extremum(result, replace(result.maximum, witness=witness), replay)
    if maximum.status != 'QUALIFIED' or maximum.interval_kg != tuple(old['interval_kg']) or maximum.gap_kg != old['gap_kg']:
        raise ValueError('RETAINED_MAXIMUM_COMPLETE_GAP_CHANGED')
    return replace(result, maximum=maximum)


def check_reuse_scope(current, prior, archive, transport_audit):
    """Check retained receipts and distinguish known affected executions.

This is not a retroactive integrity check of unavailable historical arrays.
"""
    reused = [b for b in current['bindings'] if 'minimum_reuse' in b]
    if len(reused) != 7:
        raise ValueError('SEVEN_EXPLICIT_HISTORICAL_MINIMUM_BINDINGS_REQUIRED')
    for row in current['levels']:
        old = next(r for r in prior['levels'] if r['label'] == row['label'])
        for query in ('unconditioned', 'conditioned'):
            for sense in ('minimum', 'maximum'):
                if (row['label'], query, sense) == ('N400-h0.01', 'unconditioned', 'minimum'):
                    continue
                if row[query][sense]['witness']['replay'] != old[query][sense]['witness']['replay']:
                    raise ValueError('RETAINED_REPLAY_RECEIPT_CHANGED')
    checked = []
    for finding in transport_audit['rows']:
        if not finding['differences']:
            continue
        request = archive.load(finding['archive'] + '/inputs.pickle')
        request['initial_state'].validate(); request['plan'].validate()
        affected_state = request['initial_state'].identity_sha256
        if any(b['minimum_reuse']['state_identity'] == affected_state for b in reused):
            raise ValueError('KNOWN_TRANSPORT_FINDING_REQUIRES_REUSE_REASSESSMENT')
        checked.append(dict(archive=finding['archive'], state_identity=affected_state,
            fields=[d['field'] for d in finding['differences']],
            seven_minimum_states_distinct=True))
    return dict(retained_minimum_receipts_unchanged=7, retained_maximum_receipts_unchanged=8,
        known_findings=checked, historical_pre_transport_equality='UNAVAILABLE_NOT_INFERRED',
        limitation='Distinct executions do not prove general reliability of the old transport path.')


def consolidate(evidence):
    """Revalidate the one authorized archived pair and assemble current results."""
    import ast
    index = json.loads((co.DOCS / 'CORRECTION_EXTERNAL_EVIDENCE_INDEX.json').read_text())['artifacts']
    archive = IndexedArchive(evidence, index)
    prefix = 'corrections/007-prefix-diagnostic-v1/'
    # Bind checks to executed source, including the unchanged forward report.
    snapshot = archive.load(prefix + '105-failed-minimum-A/inputs.json', as_json=True)['source_sha256']
    source = (Path(evidence) / prefix / 'source-snapshots/common_past_contrast.py').read_text()
    def functions(text):
        lines = text.splitlines(keepends=True)
        return {n.name: ''.join(lines[n.lineno-1:n.end_lineno]) for n in ast.parse(text).body if isinstance(n, ast.FunctionDef)}
    old, new = functions(source), functions(Path(cc.__file__).read_text())
    checked_functions = ('_paired_replay', '_window_replay', '_legacy_receipt', '_qualify_extremum', '_finish_replays', '_decision')
    if any(old[k] != new[k] for k in checked_functions):
        raise ValueError('ARCHIVED_REPLAY_CHECK_SOURCE_CHANGED')
    for name, expected in snapshot.items():
        path = Path(sf.__file__).parent / name
        if name != 'common_past_contrast.py' and co.sha(path) != expected:
            raise ValueError('ARCHIVED_FORWARD_OR_HELPER_SOURCE_CHANGED')
    # Source snapshots are independently indexed; inspect bytes, never execute them.
    for relative, expected in index.items():
        if relative.startswith(prefix + 'source-snapshots/'):
            path = Path(evidence) / relative
            if path.stat().st_size != expected['bytes'] or co.sha(path) != expected['sha256']:
                raise ValueError('ARCHIVED_SOURCE_SNAPSHOT_CHANGED')
            archive.used[relative] = expected
    saved = co.verified_inputs(evidence)
    prior = archive.load('corrections/007-transport-validation-v1/results.json', as_json=True)
    diagnostic = archive.load(prefix + 'minimum-result.json', as_json=True)
    delta = co.checked_replay_delta()
    rows, bindings = [], []
    with ExitStack() as stack:
        for module, name in ((sf, 'simulate_stateful_fv'), (sf.fv, '_evolve'), (pc, 'linprog'), (se, 'linprog'), (se, 'build_delivery_response')):
            stack.enter_context(patch.object(module, name, forbidden))
        for old_row in prior['levels']:
            row = dict(old_row)
            for query in ('unconditioned', 'conditioned'):
                label = old_row['label'] + '-' + query
                name = label + '-full.json'
                result = co.fresh_query(saved, name)
                outer = recheck_outer(result)
                directory = ('007-transport-validation-v1' if old_row['label'] == 'N400-h0.005' else '007-joint-witness-v1')
                relative = 'corrections/' + directory + '/' + name
                retained = archive.load(relative, as_json=True)
                result = reuse_maximum(result, retained)
                binding = dict(query=label, outer_original_kg_recheck=outer, maximum_result=relative,
                    maximum_replay='RETAINED_UNALTERED_NOT_NEW_FORWARD', new_receipt=result.receipt.identity_sha256)
                if label == 'N400-h0.01-unconditioned':
                    provider = ArchivePair(archive, (prefix + '105-failed-minimum-A', prefix + '106-failed-minimum-B'), snapshot)
                    with patch.object(sf, 'simulate_stateful_fv', provider):
                        result = cc.replay_common_past_extrema(result)
                    provider.finish()
                    if result.minimum.status != 'QUALIFIED':
                        raise ValueError('ARCHIVED_MINIMUM_UNQUALIFIED:' + result.minimum.witness.replay.termination)
                    if result.minimum.interval_kg != tuple(diagnostic['minimum']['interval_kg']) or result.minimum.gap_kg != diagnostic['minimum']['gap_kg']:
                        raise ValueError('ARCHIVED_DIAGNOSTIC_COMPLETE_GAP_DISAGREEMENT')
                    binding.update(archive_checks=provider.used, original_failed_result=name,
                        original_failed_result_sha256=co.sha(Path(evidence) / name),
                        historical_failed_replay=saved[name]['minimum']['witness']['replay'],
                        replacement='DIFFERENT_ARCHIVED_EXECUTION_OF_UNCHANGED_QUERY')
                else:
                    result, reuse = co.reuse_minimum(result, saved[name], co.sha(Path(evidence) / name), delta)
                    result = cc._finish_replays(result, (result.minimum, result.maximum))
                    binding['minimum_reuse'] = reuse
                if result.bounds != 'QUALIFIED':
                    raise ValueError('CURRENT_QUERY_UNQUALIFIED:' + label)
                row[query] = json.loads(result.to_json())
                bindings.append(binding)
            rows.append(row)
    from tools.pannusch_common_past_contrast_verification import sensitivity
    result = dict(disposition='REPRESENTATIVE_FIXED_OPERATOR_QUERIES_QUALIFIED', levels=rows, bindings=bindings,
        HISTORICAL_PREFIX_FAILURE='UNRESOLVED', TRANSPORT_ROOT_CAUSE='UNDETERMINED', PHYSICAL_VALIDATION='NOT_ESTABLISHED',
        fresh_propagations=0, fresh_backward_passes=0, fresh_lp_calls=0, archived_executions_revalidated=2,
        historical_minimum_pairs_reused=7, qualified_maximum_pairs_reused=8, sensitivity=sensitivity(rows),
        checked_function_sha256={k: hashlib.sha256(new[k].encode()).hexdigest() for k in checked_functions},
        archive_dependencies=archive.used,
        integrity_limits=['Seven historical minimum pairs lack full trajectories and pre-transport content receipts; their original executed-check bindings remain explicit.',
            'Known transport changes concern distinct maximum executions and future concentration views; corrected maximum receipts retain their own archive revalidation.',
            'No post-receipt hash proves historical pre-transport equality. No general execution-reliability or root-cause claim.'])
    result['reuse_scope_check'] = check_reuse_scope(result, prior, archive,
        json.loads((co.DOCS / 'CORRECTION_TRANSPORT_AUDIT.json').read_text()))
    return result
