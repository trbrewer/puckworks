"""Owner-authorized 007 continuation; no task time, attempt or memory ceilings.

Run under a persistent user service. Read-only status never starts work. Original
PLAN, closed ledger and evidence stay immutable; every continuation attempt gets
its own directory and append-only identity. Scientific failures stop the panel.
"""
from __future__ import annotations

import argparse
import ctypes
import datetime
import fcntl
import json
import math
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from puckworks.analysis import grudeva2026_fine_baseline_qualification_007 as task
from puckworks.analysis import grudeva2026_baseline_observation_005 as obs

GIB=1024**3
STAGES=('007-pilot',*('007-'+n for n in task.FULL))
POLICY=task.DOCS/'EXECUTION_POLICY_OVERRIDE.json'
UNLIMITED=dict(per_invocation_seconds=None,aggregate_seconds=None,full_attempts=None,
    short_attempts=None,application_rlimit_as=None)


def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()


def append(path,value):
    with path.open('a') as stream:
        stream.write(obs.canonical(value)+'\n');stream.flush();os.fsync(stream.fileno())


def process(pid):
    """PID reuse safe process identity, CPU progress and resident/virtual telemetry."""
    try:
        stat=Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()
        values={k:int(v.split()[0])*1024 for k,v in (s.split(':',1) for s in
            Path(f'/proc/{pid}/status').read_text().splitlines()) if k in ('VmRSS','VmHWM','VmSize','VmPeak')}
        return dict(pid=pid,boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
            start_ticks=int(stat[19]),state=stat[0],cpu_ticks=int(stat[11])+int(stat[12]),**values)
    except (FileNotFoundError,ProcessLookupError): return None


def alive(identity):
    now=process(identity['pid']) if identity else None
    return now is not None and now['state']!='Z' and all(now[k]==identity[k] for k in ('boot_id','start_ticks'))


def capacity(folder,pid=None):
    """Actual limits and use; margins protect the machine, never cap this worker."""
    mem={k:int(v.split()[0])*1024 for k,v in (s.split(':',1) for s in Path('/proc/meminfo').read_text().splitlines())}
    membership=[s.split(':',2)[2] for s in Path('/proc/self/cgroup').read_text().splitlines() if s.startswith('0::')]
    task.require(len(membership)==1,'unresolved cgroup v2 membership')
    root=Path('/sys/fs/cgroup');group=(root/membership[0].lstrip('/')).resolve()
    task.require(group==root or root in group.parents,'cgroup escaped mount')
    groups=[]
    for p in (group,*group.parents):
        if p!=root and root not in p.parents: continue
        values={n:(p/n).read_text().strip() for n in ('memory.max','memory.high','memory.current','memory.events','memory.pressure') if (p/n).exists()}
        task.require(p.is_dir(),'cgroup ancestor unavailable')
        groups.append(dict(path=str(p),values=values))
    disk=shutil.disk_usage(folder)
    return dict(utc=utc(),host_total_bytes=mem['MemTotal'],host_available_bytes=mem['MemAvailable'],
        process=process(pid or os.getpid()),cgroups=groups,inherited_rlimit_as=list(resource.getrlimit(resource.RLIMIT_AS)),
        inherited_rlimit_cpu=list(resource.getrlimit(resource.RLIMIT_CPU)),disk_free_bytes=disk.free,disk_total_bytes=disk.total,
        host_operating_margin_bytes=max(256*1024**2,mem['MemTotal']//100),disk_operating_margin_bytes=GIB,
        pressure=Path('/proc/pressure/memory').read_text())


def safety_reasons(snapshot,previous=None):
    reasons=[]
    if snapshot['disk_free_bytes']<snapshot['disk_operating_margin_bytes']:
        reasons.append('evidence filesystem has less than 1 GiB free; cannot safely persist output')
    if snapshot['host_available_bytes']<snapshot['host_operating_margin_bytes']:
        reasons.append('host available memory below 1% operating margin')
    for group in snapshot['cgroups']:
        v=group['values'];limit=v.get('memory.max','max')
        if limit!='max' and int(limit)-int(v['memory.current'])<max(64*1024**2,int(limit)//100):
            reasons.append('ancestor cgroup near its actual hard memory limit')
    # A low-margin sample is a warning while running. Stop only after another
    # sample confirms the pressure persists and the process is consuming memory
    # or storage. Quiet output / elapsed time are never stop conditions.
    if previous is not None:
        prior=safety_reasons(previous)
        growing=((snapshot.get('process') or {}).get('VmRSS',0)>(previous.get('process') or {}).get('VmRSS',0)
            or snapshot['disk_free_bytes']<previous['disk_free_bytes'])
        return [r for r in reasons if r in prior] if growing else []
    return reasons


def verify(plan,policy,args):
    task.verify_plan(plan,policy)
    task.require(policy['limits']==UNLIMITED,'owner override policy differs')
    task.require(obs.sha(task.DOCS/'OWNER_OVERRIDE.md')==policy['authorization_sha256'],'owner authorization record changed')
    task.require(obs.environment()==plan['environment'],'matched numerical environment differs')
    for attr in ('evidence','prior','historical'):
        task.require(obs.digest(str(getattr(args,attr).resolve()))==plan[attr+'_root_sha256'],'evidence root differs: '+attr)
    for name,h in policy['historical_documents'].items():
        task.require(obs.sha(ROOT/name)==h,'historical document changed: '+name)
    for name,h in policy['historical_external'].items():
        task.require(Path(name).name==name and obs.sha(args.evidence/name)==h,'original 007 evidence changed: '+name)
    task.require(obs.sha(ROOT/policy['tests']['file'])==policy['tests']['sha256'],'continuation tests changed')
    task.baseline_inputs(args.prior,args.historical,plan,arrays=False)
    readout=obs.read_json(args.evidence/'007-readout.json')
    task.require(readout['passed'] and readout['baseline_reuse'],'reused readout did not pass')


def accounting(folder,policy_hash):
    rows=[json.loads(s) for s in (folder/'invocations.jsonl').read_text().splitlines()]
    task.require(rows and rows[0]['event']=='override' and rows[0]['policy_sha256']==policy_hash and rows[0]['task']==task.TASK,'ledger policy differs')
    starts,ends,spawns={}, {}, {};active=None
    for r in rows[1:]:
        key=r['execution_id']
        if r['event']=='start':
            task.require(active is None and key not in starts,'concurrent/duplicate start')
            task.require(r['stage'] in (*STAGES,'007-reduction') and r['policy_sha256']==policy_hash,'invalid stage/policy')
            task.require(r['kind']==('full' if r['stage'][4:] in task.FULL else 'short'),'incorrect attempt kind')
            task.require(r['directory']==f'attempts/{key}' and Path(key).name==key,'unsafe attempt directory')
            prefix=r['stage']+'-';suffix=key[len(prefix):]
            task.require(key.startswith(prefix) and suffix.isdecimal() and
                int(suffix)==1+sum(s['stage']==r['stage'] for s in starts.values()), 'attempt sequence identity differs')
            starts[key]=r;active=key
        elif r['event']=='spawn':
            task.require(active==key and key not in spawns,'unmatched/duplicate spawn')
            spawns[key]=r
        elif r['event']=='end':
            task.require(active==key and key not in ends,'unmatched/duplicate end')
            task.require(math.isfinite(r['seconds']) and r['seconds']>=0,'invalid elapsed time')
            ends[key]=r;active=None
        else: raise ValueError('unknown ledger event')
    latest={}
    for key,r in starts.items(): latest[r['stage']]=key
    unresolved=[key for key in starts if key not in ends]
    return dict(starts=starts,ends=ends,spawns=spawns,latest=latest,unresolved_starts=unresolved,
        full=sum(r['kind']=='full' for r in starts.values()),short=sum(r['kind']=='short' for r in starts.values()),
        seconds=sum(r['seconds'] for r in ends.values()),passed=not unresolved,
        reasons=['unresolved start'] if unresolved else [])


def artifact(folder,stage,audit,must_pass=True):
    key=audit['latest'][stage];end=audit['ends'][key]
    path=folder/audit['starts'][key]['directory']/(stage+'.json')
    task.require(path.is_file() and obs.sha(path)==end['artifact_sha256'],'unbound output: '+key)
    result=obs.read_json(path)
    task.require(result['task']==task.TASK and result.get('matrix_sha256',result.get('plan_sha256'))==obs.sha(task.DOCS/'PLAN.json'),'artifact plan differs')
    task.require(result['execution']['execution_id']==key and result['execution']['policy_sha256']==audit['starts'][key]['policy_sha256'],'artifact execution differs')
    if must_pass: task.require(end['exit_code']==0 and result.get('passed') is True,'prerequisite did not pass: '+key)
    return path,result


def prerequisites(folder,stage,audit):
    task.require(audit['passed'],'unresolved prior execution')
    if stage=='007-reduction': return
    for earlier in STAGES[:STAGES.index(stage)]: artifact(folder,earlier,audit)
    if stage!='007-pilot':
        admission=obs.read_json(folder/'ADMISSION.json')
        key=audit['latest']['007-pilot']
        task.require(admission['passed'] and admission['policy_sha256']==audit['starts'][key]['policy_sha256'] and
            admission['pilot_execution_id']==key and admission['pilot_sha256']==audit['ends'][key]['artifact_sha256'], 'full admission differs')


def input_signature(audit):
    return {s:dict(execution_id=k,end_sha256=obs.digest(audit['ends'][k]))
        for s,k in audit['latest'].items() if s!='007-reduction'}


def scientific_failure(result):
    """A later crash must never erase a durably recorded scientific stop."""
    if result.get('gates') and not all(result['gates'].values()): return True
    if any(result.get(k,{}).get('passed') is False for k in ('neutrality','repeatability')): return True
    if 'refinement' in result and not task.comparisons_pass(result['refinement']): return True
    if result.get('public_result',{}).get('status','COMPLETED')!='COMPLETED': return True
    return False


def completed_marker(result,stage):
    if stage=='007-reduction':
        return (result.get('disposition') in (task.QUALIFIED,task.INCOMPLETE) and
            set(result.get('rows',{}))==set(task.ATTEMPTS[:-1]) and set(result.get('comparisons',{}))==set(task.REFINEMENTS))
    return result.get('status')=='ROW_PASSED' and result.get('passed') is True


def operational_retry(audit,stage,reason):
    key=audit['latest'].get(stage)
    if key is None: return
    if stage=='007-reduction' and audit['ends'][key]['exit_code'] in (0,2):
        task.require(input_signature(audit)!=audit['starts'][key]['input_signature'], 'completed reduction already covers these inputs')
        return
    task.require(bool(reason),'a recorded operational retry cause is required')
    task.require(audit['ends'][key]['failure_class'] in ('operational','controller_crash'),'scientific/integrity failure cannot be retried')


def execution(policy,key):
    return dict(execution_id=key,policy_sha256=obs.sha(POLICY),adapter_sources=policy['adapter_sources'])


def child_safeguards(parent):
    libc=ctypes.CDLL(None,use_errno=True)
    if libc.prctl(1,signal.SIGKILL,0,0,0)!=0: raise OSError(ctypes.get_errno(),'PR_SET_PDEATHSIG failed')
    if os.getppid()!=parent: os.kill(os.getpid(),signal.SIGKILL)
    # Inherit actual OS limits. No setrlimit, alarm, timer or application deadline.


def projected_inputs(args,folder,audit):
    old=[json.loads(s) for s in (args.evidence/'invocations.jsonl').read_text().splitlines()]
    a=next(r for r in old if r['event']=='end' and r['name']=='007-readout')
    ends={'007-readout':a};inputs={'007-readout':args.evidence/'007-readout.json'}
    for stage in STAGES:
        key=audit['latest'].get(stage)
        if key and key in audit['ends']:
            end=audit['ends'][key];ends[stage]=end
            inputs[stage]=folder/audit['starts'][key]['directory']/(stage+'.json')
            task.require(not inputs[stage].exists() or obs.sha(inputs[stage])==end['artifact_sha256'],'unsafe reduction input')
    return dict(audit,ends=ends,continuation_ends=audit['ends']),inputs


def worker(args,plan,policy):
    fd=int(os.environ.get('GRUDEVA007_LOCK_FD','-1'))
    task.require(fd>=0,'007 controller required')
    stat=os.fstat(fd);lock=(args.evidence/'controller.lock').stat()
    task.require((stat.st_ino,stat.st_dev)==(lock.st_ino,lock.st_dev),'wrong inherited lock')
    folder=args.evidence/'continuation';audit=accounting(folder,obs.sha(POLICY));key=args.execution_id
    task.require(audit['unresolved_starts']==[key],'unmatched worker start')
    start=audit['starts'][key]
    task.require(start['controller']=={k:process(os.getppid())[k] for k in ('pid','boot_id','start_ticks')},'orphan worker')
    task.require(start['controller_sha256']==obs.sha(__file__),'controller changed')
    for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
        task.require(os.environ.get(k)=='1','uncontrolled numerical threading')
    prior=dict(audit,unresolved_starts=[],passed=True,latest={k:v for k,v in audit['latest'].items() if v!=key})
    prerequisites(folder,start['stage'],prior)
    verify(plan,policy,args)
    live=capacity(folder);task.require(not safety_reasons(live),'machine safety admission blocked')
    work=folder/start['directory'];task.write_new(work/'runtime.json',dict(task=task.TASK,execution=execution(policy,key),
        environment=obs.environment(),actual_os_limits=live,limits_changed_by_worker=False))
    stage=start['stage']
    if stage=='007-reduction':
        projected,inputs=projected_inputs(args,folder,audit)
        result=task.reduction(work,args.prior,plan,projected,inputs=inputs,execution=execution(policy,key),admission_path=folder/'ADMISSION.json')
        code=0 if result['disposition']==task.QUALIFIED else 2
    else:
        result=task.simulate_row(work,args.prior,plan,'combined' if stage=='007-pilot' else stage[4:],
            pilot=stage=='007-pilot',execution=execution(policy,key))
        code=0 if result['passed'] else 2
    task.write_new(work/'completion.json',dict(task=task.TASK,execution=execution(policy,key),exit_code=code,
        artifact_sha256=obs.sha(work/(stage+'.json')),utc=utc()))
    return code


def recovered_completion(work,start,plan,policy):
    """Metadata/file-integrity recovery only; never rerun numerical reduction."""
    stage=start['stage'];path=work/(stage+'.json')
    if not path.exists(): return None
    result=obs.read_json(path)
    expected=execution(policy,start['execution_id'])
    task.require(result.get('execution')==expected,'recovery execution identity differs')
    if stage=='007-reduction':
        receipt=obs.read_json(work/'completion.json') if (work/'completion.json').exists() else None
        if receipt is not None:
            task.require(receipt['execution']==expected and receipt['artifact_sha256']==obs.sha(path),'reduction completion differs')
        if not completed_marker(result,stage): return None
        task.require(result['task']==task.TASK and result['plan_sha256']==obs.sha(task.DOCS/'PLAN.json'),'recovered reduction identity differs')
        return 0 if result['disposition']==task.QUALIFIED else 2
    if not completed_marker(result,stage): return None
    task.validate_new(result,'combined' if stage=='007-pilot' else stage[4:],plan,pilot=stage=='007-pilot',execution=expected)
    bindings=[result['public_checkpoint']]
    if result['observed']:
        task.require(set(result['gates'])==task.GATES and all(result['gates'].values()),'recovered gate coverage differs')
        bindings.append(result['observation_binding'])
        for segment in result['segments']:
            bindings.extend([dict(file=segment['file'],sha256=segment['sha256']),
                dict(file=segment['receipt_file'],sha256=segment['receipt_sha256'])])
    for binding in bindings:
        task.require(Path(binding['file']).name==binding['file'] and obs.sha(work/binding['file'])==binding['sha256'],'recovered file identity differs')
    return 0


def reconcile(folder,audit,plan=None,policy=None):
    for key in audit['unresolved_starts']:
        start=audit['starts'][key];spawn=audit['spawns'].get(key,{})
        task.require(not alive(start['controller']) and not alive(spawn.get('worker')),'recorded process still active; reconnect, do not duplicate')
        work=folder/start['directory'];output=work/(start['stage']+'.json')
        result=obs.read_json(output) if output.exists() else {}
        code=125;classification='controller_crash';recovered=False
        if scientific_failure(result): code=2;classification='scientific'
        elif policy is not None:
            completion=recovered_completion(work,start,plan,policy)
            if completion is not None:
                code=completion;classification='none' if code==0 else 'incomplete_reduction';recovered=True
        append(folder/'invocations.jsonl',dict(event='end',execution_id=key,utc=utc(),exit_code=code,
            seconds=max(0.,time.time()-start['wall_start']),failure_class=classification,
            termination=None if recovered else 'verified controller/worker absent; recovered unresolved start',
            recovered_exit_code=code,recovered_completion=recovered,controller_incident='controller/worker absent at reconciliation',
            artifact_sha256=obs.sha(output) if output.exists() else None,elapsed_basis='elapsed through reconciliation; no hidden abandoned interval'))


def invoke(args,plan,policy,stage,lock,retry_reason=None):
    folder=args.evidence/'continuation';ledger=folder/'invocations.jsonl';audit=accounting(folder,obs.sha(POLICY))
    prerequisites(folder,stage,audit);operational_retry(audit,stage,retry_reason)
    live=capacity(folder);task.require(not safety_reasons(live),'machine safety admission blocked: '+str(safety_reasons(live)))
    remaining=STAGES[STAGES.index(stage):] if stage in STAGES else ('007-reduction',)
    estimated=sum(policy['archive_estimates'][n] for n in remaining)
    task.require(live['disk_free_bytes']>=estimated+live['disk_operating_margin_bytes'], 'insufficient disk for conservative remaining archive estimate')
    live['remaining_archive_estimate_bytes']=estimated
    number=1+sum(s['stage']==stage for s in audit['starts'].values());key=f'{stage}-{number:04d}'
    work=folder/'attempts'/key;work.mkdir(parents=True,exist_ok=False)
    started=time.monotonic();identity=process(os.getpid())
    append(ledger,dict(event='start',task=task.TASK,execution_id=key,stage=stage,directory=f'attempts/{key}',
        kind='full' if stage[4:] in task.FULL else 'short',utc=utc(),wall_start=time.time(),
        controller={k:identity[k] for k in ('pid','boot_id','start_ticks')},controller_sha256=obs.sha(__file__),
        policy_sha256=obs.sha(POLICY),plan_sha256=obs.sha(task.DOCS/'PLAN.json'),retry_reason=retry_reason,
        inherited_os_limits=live,input_signature=input_signature(audit) if stage=='007-reduction' else None))
    command=[sys.executable,str(Path(__file__).resolve()),'worker','--execution-id',key]
    for n in ('evidence','prior','historical'): command.extend(['--'+n,str(getattr(args,n))])
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',
        PYTHONHASHSEED='0',PYTHONPATH=str(ROOT),GRUDEVA007_LOCK_FD=str(lock.fileno()))
    child=None;code=125;termination=None;previous=None;peak={};last_sample=-math.inf
    def cancelled(signum,frame): raise InterruptedError('controller signal '+str(signum))
    handlers={s:signal.signal(s,cancelled) for s in (signal.SIGTERM,signal.SIGINT)}
    print(obs.canonical(dict(event='starting',execution_id=key,utc=utc())),flush=True)
    with (work/'worker.log').open('x') as log:
        try:
            parent=os.getpid()
            child=subprocess.Popen(command,env=env,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,
                pass_fds=(lock.fileno(),),preexec_fn=lambda:child_safeguards(parent),start_new_session=True)
            worker_identity=process(child.pid)
            append(ledger,dict(event='spawn',execution_id=key,worker=worker_identity,utc=utc()))
            while child.poll() is None:
                if time.monotonic()-last_sample>=15:
                    snapshot=capacity(folder,child.pid);last_sample=time.monotonic()
                    for k in ('VmRSS','VmHWM','VmSize','VmPeak'):
                        peak[k]=max(peak.get(k,0),(snapshot['process'] or {}).get(k,0))
                    snapshot.update(execution_id=key,elapsed_seconds=time.monotonic()-started,warnings=safety_reasons(snapshot))
                    append(work/'progress.jsonl',snapshot)
                    reasons=safety_reasons(snapshot,previous) if previous else []
                    if reasons:
                        termination='MACHINE_SAFETY: '+str(reasons);os.killpg(child.pid,signal.SIGKILL);child.wait();code=137;break
                    previous=snapshot
                time.sleep(1)
            else: code=child.returncode
        except BaseException as exc:
            termination=type(exc).__name__+': '+str(exc);log.write(termination+'\n')
        finally:
            if child is not None and child.poll() is None: os.killpg(child.pid,signal.SIGKILL);child.wait()
            for s,h in handlers.items(): signal.signal(s,h)
    output=work/(stage+'.json');r=obs.read_json(output) if output.exists() else {}
    original_code=code;recovery_incident=None
    if code not in (0,2) and completed_marker(r,stage) and not scientific_failure(r):
        recovered=recovered_completion(work,accounting(folder,obs.sha(POLICY))['starts'][key],plan,policy)
        if recovered is not None:
            code=recovered;recovery_incident=dict(original_exit_code=original_code,termination=termination,
                reason='durable completed output validated after worker receipt/exit incident')
            termination=None
    failure_class=('scientific' if stage!='007-reduction' and scientific_failure(r) else
        'none' if code==0 else 'incomplete_reduction' if code==2 and stage=='007-reduction' else
        'scientific' if code==2 else r.get('failure',{}).get('classification','operational'))
    end=dict(event='end',execution_id=key,utc=utc(),seconds=time.monotonic()-started,exit_code=code,
        termination=termination,failure_class=failure_class,peak_memory_bytes=peak,
        recovery_incident=recovery_incident,
        artifact_sha256=obs.sha(output) if output.exists() else None,
        files={p.name:dict(bytes=p.stat().st_size,sha256=obs.sha(p)) for p in work.iterdir() if p.is_file()})
    end['seconds']=time.monotonic()-started;append(ledger,end)
    task.write_new(work/'ACCOUNTING.json',accounting(folder,obs.sha(POLICY)))
    print(obs.canonical({k:end[k] for k in ('execution_id','seconds','exit_code','termination','failure_class')}),flush=True)
    return code


def admit(args,policy,audit):
    folder=args.evidence/'continuation';path=folder/'ADMISSION.json';key=audit['latest']['007-pilot']
    _,pilot=artifact(folder,'007-pilot',audit)
    if path.exists():
        receipt=obs.read_json(path)
        task.require(receipt['pilot_execution_id']==key and receipt['policy_sha256']==obs.sha(POLICY),'admission identity changed')
        return
    live=capacity(folder);task.require(not safety_reasons(live),'machine safety admission blocked')
    task.write_new(path,dict(task=task.TASK,plan_sha256=obs.sha(task.DOCS/'PLAN.json'),policy_sha256=obs.sha(POLICY),
        passed=True,pilot_execution_id=key,pilot_sha256=audit['ends'][key]['artifact_sha256'],
        readout_sha256=policy['historical_external']['007-readout.json'],ledger_prefix_sha256=obs.sha(folder/'invocations.jsonl'),
        pilot_resources=audit['ends'][key],pilot_phase_seconds=pilot['phase_seconds'],actual_capacity=live,
        limits=UNLIMITED,full_rows=list(task.FULL),conservative_archive_estimates=policy['archive_estimates'],
        conclusion='FULL_PANEL_ADMITTED_UNDER_OWNER_OVERRIDE',
        limitation='Pilot is not a full-horizon runtime or retained-memory guarantee; estimates are not termination ceilings.'))


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('run','status','worker'))
    for n in ('evidence','prior','historical'): parser.add_argument('--'+n,type=Path,required=True)
    parser.add_argument('--execution-id');parser.add_argument('--retry-reason')
    args=parser.parse_args(argv)
    for n in ('evidence','prior','historical'): setattr(args,n,getattr(args,n).resolve())
    plan=obs.read_json(task.DOCS/'PLAN.json');policy=obs.read_json(POLICY);folder=args.evidence/'continuation'
    task.require(sys.flags.optimize==0,'optimized Python forbidden')
    if args.action=='status':
        a=accounting(folder,obs.sha(POLICY)) if (folder/'invocations.jsonl').exists() else {'status':'NOT_STARTED'}
        print(obs.canonical(a));return 0
    if args.action=='worker':
        try: return worker(args,plan,policy)
        except Exception as exc:
            work=folder/'attempts'/args.execution_id
            audit=accounting(folder,obs.sha(POLICY));stage=audit['starts'][args.execution_id]['stage'];path=work/(stage+'.json')
            r=obs.read_json(path) if path.exists() else dict(task=task.TASK,plan_sha256=obs.sha(task.DOCS/'PLAN.json'),execution=execution(policy,args.execution_id))
            if completed_marker(r,stage):
                task.write_new(work/'worker-incident.json',dict(type=type(exc).__name__,reason=str(exc),
                    phase='after durable completed result',artifact_sha256=obs.sha(path),utc=utc()))
                raise
            r.update(passed=False,status='EXECUTION_INCOMPLETE',failure=dict(type=type(exc).__name__,reason=str(exc),
                classification='operational' if isinstance(exc,(OSError,MemoryError,InterruptedError)) else 'integrity_or_scientific',
                category='resources_execution' if isinstance(exc,(OSError,MemoryError,InterruptedError)) else 'persistence_replay_observation'))
            if path.exists(): task.checkpoint(path,r)
            else: task.write_new(path,r)
            raise
    verify(plan,policy,args)
    review=obs.read_json(task.DOCS/'OVERRIDE_PREEXECUTION_REVIEW.json')
    task.require(review['passed'] and review['policy_sha256']==obs.sha(POLICY) and review['adapter_sources']==policy['adapter_sources'],'override review missing/different')
    with (args.evidence/'controller.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        folder.mkdir(exist_ok=True);ledger=folder/'invocations.jsonl'
        if not ledger.exists():
            task.write_new(ledger,dict(event='override',task=task.TASK,policy_sha256=obs.sha(POLICY),
                original_ledger_sha256=policy['historical_external']['invocations.jsonl'],utc=utc()))
        a=accounting(folder,obs.sha(POLICY));reconcile(folder,a,plan,policy)
        retry=args.retry_reason
        for stage in STAGES:
            a=accounting(folder,obs.sha(POLICY));key=a['latest'].get(stage)
            if key and a['ends'][key]['exit_code']==0:
                artifact(folder,stage,a)
                if stage=='007-pilot': admit(args,policy,a)
                continue
            if key and not retry: break
            code=invoke(args,plan,policy,stage,lock,retry_reason=retry if key else ('owner override restarts original timed-out pilot' if stage=='007-pilot' else None))
            retry=None
            if code!=0: break
            if stage=='007-pilot': admit(args,policy,accounting(folder,obs.sha(POLICY)))
        a=accounting(folder,obs.sha(POLICY));previous=a['latest'].get('007-reduction')
        signature=input_signature(a)
        if previous:
            old=a['starts'][previous].get('input_signature')
            if a['ends'][previous]['exit_code'] in (0,2):
                artifact(folder,'007-reduction',a,must_pass=False)
                if old==signature: return 0
                retry='new completed input set after recorded operational retry'
            else:
                task.require(args.retry_reason,'failed reduction needs a recorded operational retry cause')
                retry=args.retry_reason
        invoke(args,plan,policy,'007-reduction',lock,retry_reason=retry if previous else None)
    return 0


if __name__=='__main__': raise SystemExit(main())
