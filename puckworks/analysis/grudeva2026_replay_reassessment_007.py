"""Owner-authorized offline diagnosis of preserved 007 captures; never a solver.

The normal qualified reader and every historical scientific function stay intact.
Diagnostic results are explicitly unqualified while replay admission is unresolved.
"""
from __future__ import annotations

import copy
from decimal import Decimal, localcontext
from pathlib import Path
from types import FunctionType, SimpleNamespace

import numpy as np

from . import grudeva2026_baseline_observation_005 as obs
from . import grudeva2026_baseline_observation_005_report as report
from . import grudeva2026_fine_baseline_qualification_007 as task
from .grudeva2026_spatial_resolution_006_report import individual_details

DOCS = task.DOCS
PLAN = DOCS/'REPLAY_REASSESSMENT_PLAN.json'
THRESHOLD = float(obs.ALGEBRA*8)


def verify(root, plan):
    """Bind immutable history and exact environment before any array decoding."""
    from tools import grudeva2026_fine_baseline_qualification_007_invoke as ctl
    original = obs.read_json(DOCS/'PLAN.json')
    policy = obs.read_json(ctl.POLICY)
    task.require(obs.digest(str(root.resolve())) == plan['evidence_root_sha256'], 'wrong evidence root')
    args = SimpleNamespace(evidence=root, prior=root.parent/'grudeva2026-spatial-resolution-006',
                           historical=root.parent/'grudeva2026-baseline-observation-005')
    ctl.verify(original, policy, args)
    for group in ('sources', 'historical_repository'):
        for name, digest in plan[group].items():
            task.require(obs.sha(task.ROOT/name) == digest, 'reassessment source/history changed: '+name)
    for name, digest in plan['historical_external'].items():
        task.require(obs.sha(root/name) == digest, 'reassessment external history changed: '+name)
    task.require(obs.environment() == original['environment'], 'numerical environment changed')
    for name, digest in plan['scipy_sources'].items():
        import scipy.integrate._ivp as ivp
        task.require(obs.sha(Path(ivp.__file__).parent/name) == digest, 'pinned SciPy changed: '+name)
    audit = ctl.accounting(root/'continuation', obs.sha(ctl.POLICY))
    task.require(audit['passed'], 'earlier continuation start unresolved')
    return original, args


def combined_input(root, original):
    """Genuine 007 binding checks, without treating a replay failure as success."""
    path = root/'continuation/attempts/007-combined-0001/007-combined.json'
    bindings = obs.read_json(DOCS/'CONTINUATION_EVIDENCE_BINDINGS.json')
    relative = str(path.relative_to(root))
    task.require(obs.sha(path) == bindings['external_artifacts'][relative]['sha256'], 'combined metadata changed')
    m = obs.read_json(path)
    task.require(m['task'] == task.TASK and m['row'] == 'combined' and m['attempt'] == '007-combined', 'wrong task/row')
    task.require(m['controls'] == task.ROWS['combined'] and m['horizon'] == 8., 'wrong combined controls')
    task.require(m['parameters'] == original['parameters'] and m['environment'] == original['environment'], 'binding mismatch')
    task.require(m['sources'] == obs.sources() and m['matrix_sha256'] == obs.sha(DOCS/'PLAN.json'), 'scientific source mismatch')
    task.require(m['requests'] == original['requests'] and m['request_hashes'] == {
        k:obs.digest(v) for k,v in original['requests'].items()}, 'request changed')
    policy = obs.read_json(DOCS/'EXECUTION_POLICY_OVERRIDE.json')
    task.require(m['adapter_sources'] == policy['adapter_sources'] and m['execution'] == dict(
        adapter_sources=policy['adapter_sources'],execution_id='007-combined-0001',
        policy_sha256=obs.sha(DOCS/'EXECUTION_POLICY_OVERRIDE.json')), 'execution binding mismatch')
    public = task.bound_json(path.parent, m['public_checkpoint'])
    task.require(public == m['public_result'] and obs.digest(public) == m['public_result_sha256'], 'public Result changed')
    task.require(public['controls'] == m['controls'] and public['parameters'] == m['parameters'] and
                 public['time'] == m['requests']['public_times'] and public['profile_z'] == m['requests']['public_z'], 'public binding mismatch')
    task.require(len(m['segments']) == m['returned'] == m['solve_invocations'] == 3 and m['restored'] and
                 m['public_result_unchanged_after_capture'], 'capture coverage or seam mismatch')
    for i,s in enumerate(m['segments']):
        task.require(s['segment_index'] == i and s['attempt'] == m['attempt'], 'segment identity mismatch')
        for key, hashkey in (('file','sha256'), ('receipt_file','receipt_sha256')):
            task.require(Path(s[key]).name == s[key] and obs.sha(path.parent/s[key]) == s[hashkey], 'segment/receipt hash mismatch')
        import json
        receipts = [json.loads(line) for line in (path.parent/s['receipt_file']).read_text().splitlines()]
        binding = [v for v in receipts if v['stage'] == 'array_binding']
        task.require(len(binding) == 1 and binding[0]['array_manifest'] == s['array_manifest'], 'receipt manifest mismatch')
        task.require(s['artifact_integrity'] == s['array_fidelity'] == 'PASS', 'original array/file fidelity failed')
    return path, m


def validated_segment(folder, meta, size):
    segment = obs.Segment.__new__(obs.Segment)
    try:
        obs.Segment.__init__(segment, folder, copy.deepcopy(meta), size, validate=True)
        return segment
    except BaseException:
        if hasattr(segment, 'data'): segment.close()
        raise


class DiagnosticTrajectory(obs.Trajectory):
    """Separate diagnostic admission; original FAILED metadata is never removed.

Mathematical evaluate/activation/close methods are inherited unchanged. Only the
constructor differs because qualified Trajectory intentionally rejects this row.
"""
    def __init__(self, path):
        self.path = Path(path)
        self.meta = obs.read_json(path)
        c, g = self.meta['controls'], self.meta['geometry']
        self.n, self.m = c['cells'], c['modes']+1
        self.size = 2+self.n*(self.m+1)
        task.require(self.meta['schema'] == obs.SCHEMA and self.meta['state_layout'] == dict(
            size=self.size,modal_shape=[self.m,self.n],modal_axis=0,order='s,liquid,mode-major,cup'), 'diagnostic layout mismatch')
        self.weights, self.rates, self.faces = (np.asarray(g[k]) for k in ('w','rates','face'))
        task.require(self.weights.shape == self.rates.shape == (self.m,) and self.faces.shape == (self.n+1,) and
            np.all(np.isfinite(np.r_[self.weights,self.rates,self.faces])) and
            np.all(self.weights>0) and np.all(self.rates>0), 'invalid spectrum/geometry')
        task.require(np.array_equal(self.faces, 1-(1-np.arange(self.n+1)/self.n)**c['front_mesh_power']), 'mesh mismatch')
        self.segments = []
        try:
            for s in self.meta['segments']:
                task.require(s['geometry'] == g and s['persistence_schema'] == '005.segment-persistence.v2' and
                    s['artifact_integrity'] == s['array_fidelity'] == 'PASS', 'unsafe diagnostic segment')
                if 'unavailable_reason' in s:
                    task.require(s.get('failure') == dict(stage='numerical_replay',exception_type='ValueError',
                        exception_message='live dense replay failed') and s['numerical_replay'] == 'FAILED' and
                        s['capture_outcome'] == 'FAILED', 'diagnostic admission cannot bypass unrelated failures')
                else:
                    task.require(s['capture_outcome'] == s['numerical_replay'] == 'PASS', 'incomplete original receipt')
                # Independent current file hash, full safe array manifests and all
                # support/order/event checks in the unchanged lower-level reader.
                self.segments.append(validated_segment(self.path.parent, s, self.size))
            task.require(self.segments and self.segments[0].t[0] == 0., 'missing initial support')
            for a,b in zip(self.segments,self.segments[1:]):
                task.require(a.t[-1] == b.t[0] and np.array_equal(a.y[:,-1],b.y[:,0]), 'segment discontinuity')
            self.arrival = None
            for s in self.segments:
                if not s.meta['fixed'] and s.events and len(s.events[0][0]):
                    task.require(self.arrival is None, 'duplicate exit')
                    self.arrival = float(s.events[0][0][0])
            self.horizon = float(self.segments[-1].t[-1])
        except BaseException:
            self.close()
            raise


def observe_diagnostic(path):
    """Reuse the exact observation code object with one explicit reader binding.

No original globals, source, metadata, reconstruction, side or support is changed.
This callable is diagnostic only and cannot promote qualification.
"""
    namespace = dict(obs.observe_saved.__globals__, Trajectory=DiagnosticTrajectory)
    original = obs.observe_saved
    task.require(set(namespace) == set(original.__globals__) and all(
        namespace[k] is v for k,v in original.__globals__.items() if k != 'Trajectory'), 'observer namespace changed')
    method = FunctionType(original.__code__, namespace, 'diagnostic_observation', original.__defaults__, original.__closure__)
    method.__kwdefaults__ = original.__kwdefaults__
    return method(path)


def selected(segment, t):
    return min(max(int(np.searchsorted(segment.breaks,t,side=segment.meta['dense_side']))-1,0),len(segment.orders)-1)


def component(index, n, m):
    if index == 0: return dict(component='front',cell=None,mode=None)
    if index == 1+n*(m+1): return dict(component='cup',cell=None,mode=None)
    if index <= n: return dict(component='liquid',cell=index-1,mode=None)
    q=index-1-n
    return dict(component='grain_mode',cell=q%n,mode=q//n,tail=q//n == m-1)


def decimal_polynomial(t, differences, shifts, denominators, *, precision=100):
    """Independent scalar Decimal evaluation of the exact stored binary64 values."""
    with localcontext() as ctx:
        ctx.prec = precision
        dec = lambda x: Decimal.from_float(float(x))
        product, total = Decimal(1), dec(differences[0])
        for d,s,h in zip(differences[1:],shifts,denominators):
            product *= (dec(t)-dec(s))/dec(h)
            total += dec(d)*product
        return +total


def point_detail(segment, t, state, accepted, accepted_index, n, m):
    k=selected(segment,t);order=int(segment.orders[k]);d=segment.data[f'D_{k}'][:,state]
    shifts=segment.shifts[k,:order];den=segment.denominators[k,:order]
    reconstructed=float(segment.evaluate(t)[state])
    high=decimal_polynomial(t,d,shifts,den)
    higher=decimal_polynomial(t,d,shifts,den,precision=160)
    with localcontext() as ctx:
        ctx.prec=100
        exact_saved=Decimal.from_float(float(accepted))
        hi_error=high-exact_saved
        evaluation=Decimal.from_float(reconstructed)-high
        # Diagnostic counterfactual only: reconstruct unrounded time coordinates
        # from the recorded BDF endpoint and h; never use for scientific output.
        end=Decimal.from_float(float(segment.step_bounds[k,1]));h=Decimal.from_float(float(den[0]))
        product=Decimal(1);ideal=Decimal.from_float(float(d[0]));td=Decimal.from_float(float(t))
        for j in range(order):
            product *= (td-(end-j*h))/((j+1)*h)
            ideal += Decimal.from_float(float(d[j+1]))*product
        neighbors=[]
        for neighbor in sorted(set([max(k-1,0),k,min(k+1,len(segment.orders)-1)])):
            q=int(segment.orders[neighbor]);v=segment.data[f'D_{neighbor}'][:,state]
            hp=decimal_polynomial(t,v,segment.shifts[neighbor,:q],segment.denominators[neighbor,:q])
            neighbors.append(dict(interval_index=neighbor,interval=segment.step_bounds[neighbor].tolist(),order=q,
                h=float(segment.denominators[neighbor,0]),stored_polynomial=str(hp),difference=str(hp-exact_saved),
                inside_interval=bool(segment.step_bounds[neighbor,0]<=t<=segment.step_bounds[neighbor,1])))
        return dict(t=float(t),t_hex=float(t).hex(),accepted_index=accepted_index,state_index=int(state),
            **component(state,n,m),accepted_value=float(accepted),reconstructed_value=reconstructed,
            signed_difference=reconstructed-float(accepted),threshold=THRESHOLD,selection_side=segment.meta['dense_side'],
            interval_index=k,interval=segment.step_bounds[k].tolist(),order=order,
            step_size=float(segment.step_bounds[k,1]-segment.step_bounds[k,0]),dense_h=float(den[0]),
            differences=d.tolist(),shifts=shifts.tolist(),denominators=den.tolist(),
            high_precision_stored=str(high),high_precision_stored_error=str(hi_error),
            floating_evaluation_error=str(evaluation),precision_100_vs_160=str(high-higher),
            unrounded_time_coordinates_value=str(ideal),unrounded_time_coordinates_error=str(ideal-exact_saved),
            neighboring_polynomials=neighbors)


def diagnose(root, work, plan):
    original,args=verify(root,plan);path,meta=combined_input(root,original)
    # Segment alone permits diagnostic decoding without using the qualified
    # Trajectory constructor or modifying the failed metadata.
    s=validated_segment(path.parent,meta['segments'][2],meta['state_layout']['size'])
    result=dict(task=task.TASK,assessment='DIAGNOSTIC_ONLY',disposition=task.INCOMPLETE,
        metadata_sha256=obs.sha(path),original_threshold=THRESHOLD,original_receipt=meta['segments'][2]['live_replay'],
        findings=[],controls=[],physical_validation='NOT_ESTABLISHED')
    maximum=0.;at=None
    try:
        for i,(t,y) in enumerate(zip(s.t,s.y.T)):
            actual=s.evaluate(t);delta=actual-y;j=int(np.argmax(abs(delta)));error=float(abs(delta[j]))
            if error>maximum: maximum=error;at=(i,j)
            for j in np.flatnonzero(abs(delta)>THRESHOLD):
                result['findings'].append(point_detail(s,t,int(j),y[j],i,meta['controls']['cells'],meta['controls']['modes']+1))
        task.require(maximum==meta['segments'][2]['live_replay']['accepted_state_error'], 'original discrepancy not reproduced exactly')
        points={(i,j) for i,j in [at]}
        points.update((max(0,min(len(s.t)-1,i+di)),j) for i,j in [(v['accepted_index'],v['state_index']) for v in result['findings']] for di in (-1,1))
        points.update((i,j) for i in (0,len(s.t)-1) for j in (0,s.y.shape[0]-1))
        for i,j in sorted(points):
            result['controls'].append(point_detail(s,s.t[i],j,s.y[j,i],i,meta['controls']['cells'],meta['controls']['modes']+1))
        result.update(maximum=maximum,accepted_states=len(s.t),state_size=s.y.shape[0],
            exceeding_locations=len(result['findings']),maximum_location=dict(accepted_index=at[0],state_index=at[1]),
            questions=dict(A='Original direct returned-array fidelity PASS; segment-2 arrays and structure independently revalidated.',
                B='Original live/offline replay comparison retained: exact match. This offline diagnosis is not a new live-run comparison.',
                C='Original accepted-state discrepancy reproduced with unchanged evaluation and selection.'))
    finally: s.close()
    task.write_new(work/'diagnosis.json',result)
    return result


def analyze(root, work, plan):
    original,args=verify(root,plan);path,meta=combined_input(root,original)
    observed=observe_diagnostic(path)
    task.write_new(work/'observations.json',observed)
    gates=report.numeric_gates(observed,meta)
    tr=DiagnosticTrajectory(path)
    try: details=individual_details(tr,observed)
    finally: tr.close()
    task.require(set(gates)==set(details)==task.GATES,'audit coverage differs')
    baseline=task.bound_json(args.prior,original['reuse']['observations'])
    metrics=report.refinement(baseline,observed)
    task.require(set(metrics)==set(report.BUDGETS),'comparison coverage differs')
    result=dict(task=task.TASK,assessment='DIAGNOSTIC_ONLY',disposition=task.INCOMPLETE,
        replay_admission='UNRESOLVED_ORIGINAL_FAILURE_PRESERVED',gates=gates,individual_details=details,
        audits=observed['audits'],refinement=metrics,observations_sha256=obs.sha(work/'observations.json'),
        metadata_sha256=obs.sha(path),physical_validation='NOT_ESTABLISHED')
    task.write_new(work/'analysis.json',result)
    return result
