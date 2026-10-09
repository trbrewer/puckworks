"""007-only certificate for rounded BDF time coordinates, never a new observer."""
from __future__ import annotations

import copy
import ctypes
from fractions import Fraction as F
from pathlib import Path

import numpy as np

from . import grudeva2026_replay_reassessment_007 as reassess
from . import grudeva2026_baseline_observation_005 as obs
from . import grudeva2026_fine_baseline_qualification_007 as task

PLAN = task.DOCS/'REPLAY_ADMISSION_CORRECTION.json'


def rational(value):
    return F.from_float(float(value))


def basis(t, shifts, denominators):
    product=F(1);result=[]
    for s,h in zip(shifts,denominators):
        product *= (t-s)/h
        result.append(product)
    return result


def exact_record(x):
    # Exact fractions control decisions; decimal approximations are report-only.
    return dict(numerator=str(x.numerator),denominator=str(x.denominator),approximate=float(x))


def floating_model():
    task.require(ctypes.CDLL(None).fegetround()==0, 'round-to-nearest floating mode required')
    # Construct operands by bits, then use runtime ufuncs: no constant folding.
    normal=np.array([0x0010000000000000],dtype=np.uint64).view(np.float64)
    tiny=np.array([1],dtype=np.uint64).view(np.float64)
    half=np.multiply(normal,np.array([.5])).view(np.uint64)[0]
    twice=np.multiply(tiny,np.array([2.])).view(np.uint64)[0]
    task.require(half==0x0008000000000000 and twice==2, 'gradual underflow / denormal input mode required')


def certify_point(point):
    """Original coefficient residual plus exact coordinate/evaluation bounds.

All decisions use exact rational arithmetic on the recorded binary64 values.
No allowance is inferred from a measured accepted-state maximum.
"""
    floating_model()
    k=point['order'];t=point['t'];end=point['interval'][1];h=point['dense_h']
    d=np.asarray(point['differences'],float);s=np.asarray(point['shifts'],float)
    den=np.asarray(point['denominators'],float)
    task.require(1<=k<=5 and d.shape==(k+1,) and s.shape==den.shape==(k,), 'invalid certificate shape/order')
    task.require(np.all(np.isfinite(np.r_[d,s,den,t,end,h,point['accepted_value'],point['reconstructed_value']])) and
        h>0 and point['interval'][0]<=t<=end, 'nonfinite or unsupported certificate')
    task.require(np.array_equal(s.view(np.uint64),(end-h*np.arange(k)).view(np.uint64)) and
        np.array_equal(den.view(np.uint64),(h*(1+np.arange(k))).view(np.uint64)),
        'coordinates differ from pinned BDF construction')
    tf,ef,hf=map(rational,(t,end,h));df=list(map(rational,d))
    stored=basis(tf,list(map(rational,s)),list(map(rational,den)))
    ideal=basis(tf,[ef-j*hf for j in range(k)],[(j+1)*hf for j in range(k)])
    floating=np.cumprod((t-s)/den)
    task.require(np.all(np.isfinite(floating)), 'nonfinite evaluation factors')
    pf=list(map(rational,floating))
    ps=df[0]+sum((v*p for v,p in zip(df[1:],stored)),F(0))
    pi=df[0]+sum((v*p for v,p in zip(df[1:],ideal)),F(0))
    saved=rational(point['accepted_value']);actual=rational(point['reconstructed_value'])
    coordinate=sum((abs(v)*abs(p-q) for v,p,q in zip(df[1:],stored,ideal)),F(0))
    # Factor rounding is measured exactly against independent rational factors;
    # the remaining length-k dot and addition have <= 2*k+2 rounded operations.
    u=F(1,2**53);n=2*k+2;gamma=n*u/(1-n*u)
    magnitude=abs(df[0])+sum((abs(v*p) for v,p in zip(df[1:],pf)),F(0))
    # Gradual underflow: each operation's absolute rounding term <= min subnormal.
    # The 1/(1-n*u) factor also bounds its amplification in this sum/dot.
    underflow=F(n,2**1074)/(1-n*u)
    evaluation=sum((abs(v)*abs(p-q) for v,p,q in zip(df[1:],pf,stored)),F(0))+gamma*magnitude+underflow
    threshold=rational(reassess.THRESHOLD)
    # Guard the finite, round-to-nearest model for intermediate dot magnitudes.
    task.require(magnitude < rational(np.finfo(float).max)/(1+gamma), 'potential dot overflow')
    gates=dict(coefficient_consistency=abs(pi-saved)<=threshold,
               evaluation_roundoff=abs(actual-ps)<=evaluation,
               coordinate_bound=abs(ps-pi)<=coordinate,
               accepted_state_bound=abs(actual-saved)<=threshold+coordinate+evaluation)
    return dict(passed=all(gates.values()),gates=gates,
        location={key:point[key] for key in ('t','accepted_index','state_index','component','cell','mode')},
        original_threshold=exact_record(threshold),coefficient_residual=exact_record(pi-saved),
        stored_polynomial_residual=exact_record(ps-saved),evaluation_residual=exact_record(actual-ps),
        coordinate_rounding=[dict(index=j,shift_error=exact_record(rational(s[j])-(ef-j*hf)),
            denominator_error=exact_record(rational(den[j])-(j+1)*hf),
            signed_polynomial_contribution=exact_record(df[j+1]*(stored[j]-ideal[j]))) for j in range(k)],
        coordinate_bound=exact_record(coordinate),evaluation_bound=exact_record(evaluation),
        accepted_state_allowance=exact_record(threshold+coordinate+evaluation),
        original_signed_difference=point['signed_difference'],
        rule='original gate OR independently certified rounded-coordinate branch; events unchanged')


def validate_offenders(diagnosis):
    points=diagnosis['findings']
    identities={(p['accepted_index'],p['state_index']) for p in points}
    task.require(points and len(identities)==len(points)==diagnosis['exceeding_locations'], 'offender coverage mismatch')
    task.require(all(abs(p['signed_difference'])>reassess.THRESHOLD and p['threshold']==reassess.THRESHOLD for p in points),
                 'nonexceptional or differently assessed offender')
    task.require(max(abs(p['signed_difference']) for p in points)==diagnosis['maximum'], 'offender maximum mismatch')


def replay_admission(live, certified=False):
    return bool(live['allowance_fraction']<=1 and live['event_state_error']<=reassess.THRESHOLD and
                (live['accepted_state_error']<=reassess.THRESHOLD or certified))


def bound_relative(root, binding):
    relative=Path(binding['file'])
    task.require(not relative.is_absolute() and '..' not in relative.parts, 'unsafe evidence-relative path')
    path=(root/relative).resolve()
    task.require(path.is_relative_to(root.resolve()), 'evidence path escapes root')
    return task.bound_json(path.parent,dict(file=path.name,sha256=binding['sha256']))


def certify(root, work, plan):
    review=obs.read_json(root/plan['preexecution_review_file'])
    task.require(review['passed'] and review['contract_sha256']==obs.sha(PLAN), 'independent correction review missing/mismatched')
    original,args=reassess.verify(root,plan)
    task.require(set(plan['captures'])=={'baseline_512','pilot','repeat_512','modes_fine','time_fine','bed_fine','combined'},
                 'retained capture coverage differs')
    diagnosis=bound_relative(root,plan['diagnosis'])
    analysis=bound_relative(root,plan['analysis'])
    validate_offenders(diagnosis)
    task.require(diagnosis['exceeding_locations']==len(diagnosis['findings']) and
        diagnosis['metadata_sha256']==analysis['metadata_sha256'],'diagnostic identity/coverage mismatch')
    # Cross-check every recorded offender against the independently validated
    # original archive. Completeness is inherited from the frozen exhaustive scan.
    path,meta=reassess.combined_input(root,original)
    segment=reassess.validated_segment(path.parent,meta['segments'][2],meta['state_layout']['size'])
    try:
        for p in diagnosis['findings']+diagnosis['controls']:
            i,j=p['accepted_index'],p['state_index'];t=segment.t[i];k=reassess.selected(segment,t)
            task.require(t==p['t'] and p['selection_side']==segment.meta['dense_side'] and segment.y[j,i]==p['accepted_value'] and
                segment.evaluate(t)[j]==p['reconstructed_value'] and k==p['interval_index'], 'point identity mismatch')
            task.require(int(segment.orders[k])==p['order'] and
                segment.data[f'D_{k}'][:,j].tolist()==p['differences'] and
                segment.shifts[k,:p['order']].tolist()==p['shifts'] and
                segment.denominators[k,:p['order']].tolist()==p['denominators'] and
                segment.step_bounds[k].tolist()==p['interval'], 'point polynomial mismatch')
    finally: segment.close()
    certificates=[certify_point(p) for p in diagnosis['findings']]
    controls=[certify_point(p) for p in diagnosis['controls']]
    # Apply one disjunction to every relevant retained capture. Original passing
    # receipts are reused, including their event tests and live/offline fidelity.
    captures={};exceeding_segments=[]
    for identity,binding in plan['captures'].items():
        base=args.prior if binding['root']=='006' else root
        path=base/binding['file'];m=bound_relative(base,binding)
        rows=[]
        for i,s in enumerate(m['segments']):
            for key,hkey in (('file','sha256'),('receipt_file','receipt_sha256')):
                task.require(Path(s[key]).name==s[key] and obs.sha(path.parent/s[key])==s[hkey], 'capture artifact changed')
            task.require(s['artifact_integrity']==s['array_fidelity']=='PASS', 'file/array fidelity failure')
            live=s['live_replay']
            fidelity=live['allowance_fraction']<=1
            events=live['event_state_error']<=reassess.THRESHOLD
            accepted=live['accepted_state_error']<=reassess.THRESHOLD
            corrected=False
            if not accepted:
                exceeding_segments.append((identity,i))
                task.require(identity=='combined' and i==2 and obs.sha(path)==diagnosis['metadata_sha256'] and
                    live==diagnosis['original_receipt'] and live['accepted_state_error']==diagnosis['maximum'],
                    'unassessed accepted-state discrepancy')
                task.require(certificates and len({(p['accepted_index'],p['state_index']) for p in diagnosis['findings']})==len(certificates),
                    'missing or duplicate certified offender')
                corrected=all(c['passed'] for c in certificates)
            else:
                task.require(s['capture_outcome']==s['numerical_replay']=='PASS' and 'unavailable_reason' not in s,
                    'unrelated historical admission failure')
            rows.append(dict(segment=i,original_accepted_error=live['accepted_state_error'],
                original_accepted_gate=accepted,event_gate=events,live_offline_fidelity=fidelity,
                coordinate_certificate=corrected if not accepted else 'NOT_NEEDED_ORIGINAL_GATE_PASSED',
                passed=replay_admission(live,corrected)))
        captures[identity]=dict(metadata_sha256=obs.sha(path),segments=rows,passed=all(v['passed'] for v in rows))
    task.require(exceeding_segments==[('combined',2)], 'unexpected certificate coverage')
    # A new certificate supplements rather than rewrites FAILED metadata. Results
    # computed with unchanged observer code remain labelled diagnostic at origin.
    passed=all(v['passed'] for v in captures.values()) and all(c['passed'] for c in certificates+controls)
    result=dict(task=task.TASK,passed=passed,disposition=task.INCOMPLETE,
        meaning='Replay admission only; final qualification additionally requires every original scientific gate.',
        certificates=certificates,controls=controls,captures=captures,diagnosis_sha256=plan['diagnosis']['sha256'],
        analysis_sha256=plan['analysis']['sha256'],physical_validation='NOT_ESTABLISHED')
    task.write_new(work/'certificate.json',result)
    prior=obs.read_json(task.DOCS/'CONTINUATION_RESULTS.json')
    bindings=dict(plan_sha256=obs.sha(PLAN),certificate_sha256=obs.sha(work/'certificate.json'),
        diagnosis_sha256=plan['diagnosis']['sha256'],analysis_sha256=plan['analysis']['sha256'],
        original_failed_metadata_preserved=True,scientific_sources_unchanged=True,production_invocations=0)
    scope=dict(baseline=task.ROWS['baseline_512'],parameters=original['parameters'],horizon=8.,
        environment=original['environment'],scientific_sources=original['scientific_sources'],
        requests=original['requests'],masks='unchanged pair-specific inherited masks',
        refinements=['modes_fine','time_fine','bed_fine','combined'],
        physical_validation='NOT_ESTABLISHED',continuum_accuracy='NOT_ESTABLISHED',adoption='NOT_AUTHORIZED')
    final=assemble_qualification(prior,analysis,passed,scope,bindings)
    task.write_new(work/'qualification.json',final)
    return final


def assemble_qualification(prior,analysis,passed,scope,bindings):
    """Pure report assembly; certificate success cannot replace scientific gates."""
    final=copy.deepcopy(prior)
    final['historical_disposition']=prior['disposition']
    final['historical_reasons']=prior['reasons']
    final['reassessment']=bindings
    combined=dict(prior['rows']['007-combined'])
    combined.update(historical_execution=prior['rows']['007-combined'],
        status='SAVED_RESULT_REASSESSED',gates=analysis['gates'],individual_details=analysis['individual_details'],
        audits=analysis['audits'],replay_admission=passed,
        passed=passed and all(analysis['gates'].values()),
        observation_origin='DIAGNOSTIC_ONLY artifact, admitted separately by reviewed replay certificate')
    final['rows']['007-combined']=combined
    final['comparisons']['combined']=analysis['refinement']
    gates=dict(replay=passed,baseline=prior['baseline_reuse_validated'] and
        set(prior['baseline_gates'])==task.GATES and all(prior['baseline_gates'].values()),
        prerequisites=all(v['passed'] for v in prior['prerequisites'].values()),
        rows=all(v['passed'] for v in final['rows'].values()),
        combined_audit_coverage=set(analysis['gates'])==set(analysis['individual_details'])==task.GATES,
        refinement_coverage=set(final['comparisons'])=={'modes_fine','time_fine','bed_fine','combined'})
    gates['refinements']=all(set(rows)==set(reassess.report.BUDGETS) and
        all(r['passed'] and r['included']>0 and r['unavailable']==0 for r in rows.values())
        for rows in final['comparisons'].values())
    gates['independent_audits']=all(set(row['gates'])==task.GATES and all(row['gates'].values())
        for name,row in final['rows'].items() if name in
        {'007-repeat_512','007-modes_fine','007-time_fine','007-bed_fine','007-combined'})
    gates['neutrality']=final['rows']['007-control_512']['neutrality']['passed']
    gates['repeatability']=final['rows']['007-repeat_512']['repeatability']['passed']
    final['qualification_gates']=gates
    final['disposition']=task.QUALIFIED if all(gates.values()) else task.INCOMPLETE
    reasons={k:[] for k in prior['reasons']}
    for key in ('integration_software','source_environment_rights'):
        reasons[key]=copy.deepcopy(prior['reasons'][key])
    if not passed:reasons['persistence_replay_observation'].append('saved combined replay admission remains failed')
    if not gates['baseline']:reasons['source_environment_rights'].append('baseline reuse/audit binding failed')
    if not gates['prerequisites']:reasons['persistence_replay_observation'].append('readout/pilot prerequisite failed or unavailable')
    for key in ('neutrality','repeatability'):
        if not gates[key]:reasons['neutrality_repeatability'].append(key+' failed')
    reasons['individual_audits']={name:[key for key,value in row.get('gates',{}).items() if not value]
        for name,row in final['rows'].items() if 'gates' in row and not all(row['gates'].values())}
    if not gates['combined_audit_coverage'] or not gates['independent_audits']:
        reasons['individual_audits'].setdefault('coverage',[]).append('required individual audit coverage or gate failed')
    reasons['refinements']={name:[key for key,r in rows.items() if not
        (r['passed'] and r['included']>0 and r['unavailable']==0)]
        for name,rows in final['comparisons'].items() if set(rows)!=set(reassess.report.BUDGETS) or
        not all(r['passed'] and r['included']>0 and r['unavailable']==0 for r in rows.values())}
    if not gates['refinement_coverage']:reasons['refinements']['coverage']=['mandatory pair missing']
    for name,row in final['rows'].items():
        if name!='007-combined' and not row['passed']:
            reasons['resources_execution'].append(name+': retained row failed or unavailable')
    final['reasons']=reasons
    gates['other_blockers']=not any(reasons[k] for k in ('integration_software','source_environment_rights','resources_execution'))
    final['disposition']=task.QUALIFIED if all(gates.values()) else task.INCOMPLETE
    final['reassessment_failures']=[k for k,v in gates.items() if not v]
    final['scope']=scope
    return final
