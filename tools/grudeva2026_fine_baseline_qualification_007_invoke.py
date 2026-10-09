"""Serial 007 controller with fixed identities, separate admission and crash accounting."""
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
MEMORY=34359738368
MARGIN=4*GIB
LIMITS=dict(full=6,short=3,aggregate_seconds=4800.,per_invocation_seconds=1200.,memory_bytes=MEMORY)
SHORT={'007-readout':120.,'007-pilot':300.,'007-reduction':240.}
FULL_ALLOCATIONS=dict(zip(('007-'+n for n in task.FULL),(300.,420.,600.,480.,1000.,1200.)))
ALLOCATIONS={**SHORT,**FULL_ALLOCATIONS}
ARCHIVES={n:(32*GIB if n.endswith('combined') else 20*GIB if n.endswith('bed_fine') else 12*GIB)
          for n in FULL_ALLOCATIONS}
ARCHIVES.update({'007-readout':GIB,'007-pilot':16*GIB,'007-control_512':GIB,'007-reduction':GIB})


def append(path,value):
    with path.open('a') as stream:
        stream.write(obs.canonical(value)+'\n');stream.flush();os.fsync(stream.fileno())


def accounting(folder,plan_hash):
    rows=[json.loads(s) for s in (Path(folder)/'invocations.jsonl').read_text().splitlines()]
    task.require(rows and rows[0]==dict(event='freeze',task=task.TASK,plan_sha256=plan_hash,limits=LIMITS), 'ledger freeze differs')
    starts,ends={},{}
    active=None
    for r in rows[1:]:
        n=r['name'];task.require(n in task.ATTEMPTS, 'unauthorized ledger name')
        if r['event']=='start':
            task.require(active is None and n not in starts, 'concurrent/duplicate start')
            task.require('007-reduction' not in starts, 'campaign already reduced')
            if n!='007-reduction':
                task.require(list(starts)==list(task.ATTEMPTS[:task.ATTEMPTS.index(n)]), 'ledger sequence differs')
            task.require(r['kind']==('full' if n in FULL_ALLOCATIONS else 'short') and r['ceiling']==ALLOCATIONS[n], 'allocation differs')
            task.require(r['memory_bytes']==MEMORY and r['plan_sha256']==plan_hash and r['task']==task.TASK, 'ledger policy differs')
            starts[n]=r;active=n
        elif r['event']=='end':
            task.require(active==n and n not in ends, 'unmatched/duplicate end')
            task.require(math.isfinite(r['seconds']) and r['seconds']>=0, 'invalid consumption')
            ends[n]=r;active=None
        else:
            raise ValueError('invalid ledger event')
    unresolved=[n for n in starts if n not in ends]
    seconds=sum(r['seconds'] for r in ends.values())
    reserved=seconds+sum(starts[n]['ceiling'] for n in unresolved)
    full=sum(r['kind']=='full' for r in starts.values());short=len(starts)-full
    reasons=[]
    if unresolved: reasons.append('unresolved start; full allocation reserved; numerical work blocked')
    if full>6 or short>3 or reserved>4800: reasons.append('aggregate attempt/time ceiling exceeded')
    for n,r in ends.items():
        if r['seconds']>min(starts[n]['ceiling'],1200): reasons.append(n+': invocation allocation exceeded')
        if r.get('enforced_rlimit_as') not in (None,[MEMORY,MEMORY]): reasons.append(n+': wrong address-space policy')
        if r.get('exit_code')==0 and r.get('enforced_rlimit_as')!=[MEMORY,MEMORY]: reasons.append(n+': successful worker lacks enforced limit receipt')
    return dict(starts=starts,ends=ends,full=full,short=short,seconds=seconds,charged_or_reserved_seconds=reserved,
        unresolved_starts=unresolved,reasons=reasons,passed=not reasons)


def capacity(folder,remaining_storage,*,worker=False):
    """007's actual 32 GiB policy, not the inherited 8 GiB capacity check."""
    mem={k:int(v.split()[0])*1024 for k,v in (s.split(':',1) for s in Path('/proc/meminfo').read_text().splitlines())}
    own={k:int(v.split()[0])*1024 for k,v in (s.split(':',1) for s in Path('/proc/self/status').read_text().splitlines())
         if k in ('VmSize','VmPeak','VmRSS','VmHWM')}
    membership=[s.split(':',2)[2] for s in Path('/proc/self/cgroup').read_text().splitlines() if s.startswith('0::')]
    task.require(len(membership)==1, 'unresolved cgroup v2 membership')
    group=(Path('/sys/fs/cgroup')/membership[0].lstrip('/')).resolve()
    root=Path('/sys/fs/cgroup')
    task.require(group==root or root in group.parents, 'cgroup escaped mount')
    groups=[]
    for p in (group,*group.parents):
        if p!=root and root not in p.parents: continue
        task.require(p.is_dir(), 'cgroup ancestor unavailable')
        values={n:(p/n).read_text().strip() for n in ('memory.max','memory.high','memory.current') if (p/n).exists()}
        groups.append(dict(path=str(p),values=values))
        for key in ('memory.max','memory.high'):
            if values.get(key,'max')!='max':
                task.require('memory.current' in values, 'cgroup current usage unavailable')
                task.require(int(values[key])-int(values['memory.current'])>=MEMORY+MARGIN, '32 GiB cgroup operating margin blocked')
    inherited=list(resource.getrlimit(resource.RLIMIT_AS))
    task.require(all(x==resource.RLIM_INFINITY or x>=MEMORY for x in inherited), 'inherited virtual ceiling below 32 GiB')
    if worker: task.require(inherited==[MEMORY,MEMORY], 'worker address-space limit differs')
    task.require(own['VmSize']<MEMORY-MARGIN, 'current virtual use leaves insufficient working margin')
    task.require(mem['MemAvailable']>=MEMORY+MARGIN, '32 GiB host resident margin blocked')
    storage=shutil.disk_usage(folder).free
    task.require(storage>=remaining_storage+8*GIB, 'remaining archives plus 8 GiB storage margin unavailable')
    return dict(host_available_bytes=mem['MemAvailable'],process_memory_bytes=own,cgroups=groups,
        inherited_rlimit_as=inherited,operating_margin_bytes=MARGIN,requested_address_space_bytes=MEMORY,
        remaining_archive_bytes=remaining_storage,storage_margin_bytes=8*GIB,storage_free_bytes=storage)


def artifact(folder,name,audit,*,must_pass=True):
    end=audit['ends'].get(name,{})
    path=Path(folder)/(name+'.json')
    task.require(path.is_file() and end.get('artifact_sha256')==obs.sha(path), 'unbound output: '+name)
    r=obs.read_json(path)
    task.require(r['task']==task.TASK and r.get('plan_sha256',r.get('matrix_sha256'))==obs.sha(task.DOCS/'PLAN.json'), 'output task/plan differs')
    if must_pass: task.require(end.get('exit_code')==0 and r.get('passed') is True, 'required predecessor did not pass: '+name)
    return r


def allocations(name,audit):
    task.require(audit['passed'], '; '.join(audit['reasons']))
    task.require(name not in audit['starts'], 'duplicate attempt forbidden')
    task.require(audit['short' if name in SHORT else 'full']<LIMITS['short' if name in SHORT else 'full'], 'attempt limit reached')
    if name=='007-reduction':
        task.require(bool(audit['ends']), 'nothing to reduce')
        future=[]
    else:
        i=task.ATTEMPTS.index(name)
        task.require(set(audit['starts'])==set(task.ATTEMPTS[:i]), 'fixed serial execution order required')
        future=list(task.ATTEMPTS[i+1:])
    task.require(audit['seconds']+ALLOCATIONS[name]+sum(ALLOCATIONS[n] for n in future)<=4800., 'future reservations exceed aggregate')
    return ALLOCATIONS[name],sum(ARCHIVES[n] for n in [name,*future])


def admission(folder,plan,audit):
    """Metadata-only post-pilot receipt. PLAN never receives measured feasibility."""
    task.require(audit['passed'] and set(audit['ends'])==set(task.ATTEMPTS[:2]), 'admission requires closed A/B only')
    a=artifact(folder,'007-readout',audit);b=artifact(folder,'007-pilot',audit)
    consumed=audit['seconds']
    remaining=sum(FULL_ALLOCATIONS.values())+SHORT['007-reduction']
    pilot_end=audit['ends']['007-pilot']
    # A short pilot cannot establish horizon-8 retained output or runtime. These are
    # conservative bounded engineering allocations, including explicit stop risk.
    peak=pilot_end['telemetry'].get('VmPeak_bytes')
    task.require(peak is not None and peak<MEMORY-MARGIN, 'pilot virtual margin is not established')
    headroom=capacity(folder,sum(ARCHIVES[n] for n in (*FULL_ALLOCATIONS,'007-reduction')))
    estimates=plan['full_panel_estimates']
    passed=(consumed+remaining<=4800 and all(v<=1200 for v in FULL_ALLOCATIONS.values()) and
            estimates['peak_virtual_envelope_bytes']<=MEMORY-MARGIN)
    receipt=dict(task=task.TASK,plan_sha256=obs.sha(task.DOCS/'PLAN.json'),passed=passed,
        prerequisites={n:audit['ends'][n]['artifact_sha256'] for n in task.ATTEMPTS[:2]},
        ledger_prefix_sha256=obs.sha(Path(folder)/'invocations.jsonl'),consumed_seconds=consumed,
        full_allocations=FULL_ALLOCATIONS,final_reduction_reserve=SHORT['007-reduction'],
        reserved_total_seconds=remaining,aggregate_with_reservations=consumed+remaining,
        pilot_resources=pilot_end,pilot_phase_seconds=b['phase_seconds'],headroom=headroom,estimates=estimates,
        remaining_archive_bytes=sum(ARCHIVES[n] for n in (*FULL_ALLOCATIONS,'007-reduction')),
        conclusion='BOUNDED_FULL_PANEL_ADMITTED' if passed else 'RESOURCE_ALLOCATION_BLOCKED',
        limitation='Pilot establishes only its horizon-.4 capture; full-horizon runtime and retained memory are unproven. No scaling law or retry authority.',
        failure_closeout='Single reduction allowed after any closed failed start; missing rows remain NOT_RUN; unresolved starts block.')
    task.write_new(Path(folder)/'ADMISSION.json',receipt)
    return receipt


def prerequisites(folder,name,plan,audit):
    if name=='007-reduction':
        # Deliberately allow closed failures and absent partial outputs. Hash all
        # surviving outputs against end receipts before numerical reduction.
        for n,e in audit['ends'].items():
            p=Path(folder)/(n+'.json')
            task.require(not p.exists() or obs.sha(p)==e['artifact_sha256'], 'unsafe closeout input')
        return
    for n in task.ATTEMPTS[:task.ATTEMPTS.index(name)]: artifact(folder,n,audit)
    if name in FULL_ALLOCATIONS:
        receipt=obs.read_json(Path(folder)/'ADMISSION.json')
        task.require(receipt['task']==task.TASK and receipt['plan_sha256']==obs.sha(task.DOCS/'PLAN.json') and
            receipt['passed'] and receipt['full_allocations']==FULL_ALLOCATIONS and
            receipt['final_reduction_reserve']==SHORT['007-reduction'], 'full-panel admission differs')
        task.require(receipt['prerequisites']=={n:audit['ends'][n]['artifact_sha256'] for n in task.ATTEMPTS[:2]}, 'admission A/B differs')
        task.require(receipt['estimates']==plan['full_panel_estimates'] and
            receipt['consumed_seconds']==sum(audit['ends'][n]['seconds'] for n in task.ATTEMPTS[:2]) and
            receipt['reserved_total_seconds']==sum(FULL_ALLOCATIONS.values())+SHORT['007-reduction'] and
            receipt['aggregate_with_reservations']==receipt['consumed_seconds']+receipt['reserved_total_seconds']<=4800,
            'admission resource basis differs')
        prior_admission={r['admission_sha256'] for n,r in audit['starts'].items() if n in FULL_ALLOCATIONS}
        task.require(not prior_admission or prior_admission=={obs.sha(Path(folder)/'ADMISSION.json')}, 'admission changed after first full start')
        if not prior_admission:
            # The controller reads the complete A/B prefix. In the worker the
            # current start is already appended; hash exactly the preceding bytes.
            lines=(Path(folder)/'invocations.jsonl').read_bytes().splitlines(keepends=True)
            if json.loads(lines[-1]).get('event')=='start': lines=lines[:-1]
            import hashlib
            task.require(hashlib.sha256(b''.join(lines)).hexdigest()==receipt['ledger_prefix_sha256'], 'admission ledger prefix differs')


def roots(args,plan):
    for attr in ('evidence','prior','historical'):
        task.require(obs.digest(str(getattr(args,attr).resolve()))==plan[attr+'_root_sha256'], 'evidence root changed: '+attr)
    task.require(len({args.evidence,args.prior,args.historical})==3, 'task ledgers must remain separate')


def child_limits(parent):
    libc=ctypes.CDLL(None,use_errno=True)
    if libc.prctl(1,signal.SIGKILL,0,0,0)!=0: raise OSError(ctypes.get_errno(),'PR_SET_PDEATHSIG failed')
    if os.getppid()!=parent: os.kill(os.getpid(),signal.SIGKILL)
    resource.setrlimit(resource.RLIMIT_AS,(MEMORY,MEMORY))


def closed_prefix(audit,name):
    task.require(audit['unresolved_starts']==[name], 'unexpected unresolved start')
    reasons=[r for r in audit['reasons'] if r!='unresolved start; full allocation reserved; numerical work blocked']
    prior=dict(audit,starts={n:r for n,r in audit['starts'].items() if n!=name},
        unresolved_starts=[],reasons=reasons,passed=not reasons)
    kind=audit['starts'][name]['kind']
    prior[kind]-=1
    return prior


def retain_failure(folder,name,plan_hash,exc):
    path=folder/(name+'.json')
    r=obs.read_json(path) if path.exists() else dict(task=task.TASK,attempt=name,
        plan_sha256=plan_hash,physical_validation='NOT_ESTABLISHED')
    category=('resources_execution' if isinstance(exc,MemoryError) else
        'source_environment_rights' if any(s in str(exc).lower() for s in ('source','environment','binding','identity','rights','plan','request'))
        else 'persistence_replay_observation')
    r.update(passed=False,status='EXECUTION_INCOMPLETE',failure=dict(type=type(exc).__name__,reason=str(exc),category=category))
    if path.exists(): task.checkpoint(path,r)
    else: task.write_new(path,r)


def worker(args,plan):
    fd=int(os.environ.get('GRUDEVA007_LOCK_FD','-1'))
    task.require(fd>=0 and os.environ.get('GRUDEVA007_ATTEMPT')==args.action, '007 controller required')
    stat=os.fstat(fd);lock=(args.evidence/'controller.lock').stat()
    task.require((stat.st_ino,stat.st_dev)==(lock.st_ino,lock.st_dev), 'wrong inherited lock')
    audit=accounting(args.evidence,obs.sha(task.DOCS/'PLAN.json'))
    start=audit['starts'].get(args.action,{})
    task.require(audit['unresolved_starts']==[args.action] and start.get('controller_pid')==os.getppid(), 'orphan/unmatched start')
    task.require(start['controller_sha256']==obs.sha(__file__), 'controller source differs')
    for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
        task.require(os.environ.get(k)=='1', 'uncontrolled numerical threading')
    remaining=start['deadline_monotonic']-time.monotonic()
    task.require(remaining>0, 'deadline elapsed')
    signal.setitimer(signal.ITIMER_REAL,remaining)
    # Worker independently rechecks all closed-prefix admission and live capacity.
    prior=closed_prefix(audit,args.action)
    ceiling,storage=allocations(args.action,prior)
    task.require(ceiling==start['ceiling'], 'worker allocation differs')
    prerequisites(args.evidence,args.action,plan,prior)
    live=capacity(args.evidence,storage,worker=True)
    task.verify_plan(plan)
    task.require(obs.environment()==plan['environment'], 'execution environment differs')
    task.write_new(args.evidence/(args.action+'-runtime.json'),dict(task=task.TASK,attempt=args.action,
        enforced_rlimit_as=list(resource.getrlimit(resource.RLIMIT_AS)),environment=obs.environment(),headroom=live))
    if args.action=='007-readout': result=task.readout(args.evidence,args.prior,args.historical,plan)
    elif args.action=='007-reduction':
        result=task.reduction(args.evidence,args.prior,plan,audit)
        return 0 if result['disposition']==task.QUALIFIED else 2
    else:
        result=task.simulate_row(args.evidence,args.prior,plan,'combined' if args.action=='007-pilot' else args.action[4:],pilot=args.action=='007-pilot')
    return 0 if result['passed'] else 2


def finalize(folder,plan_hash,name):
    audit=accounting(folder,plan_hash)
    p=folder/(name+'.json')
    result=dict(task=task.TASK,plan_sha256=plan_hash,resources=audit,
        preliminary_file=p.name,preliminary_sha256=obs.sha(p) if p.exists() else None,
        disposition=task.INCOMPLETE,physical_validation='NOT_ESTABLISHED')
    if name=='007-reduction' and p.exists() and audit['passed'] and audit['ends'][name]['exit_code']==0:
        result['disposition']=obs.read_json(p)['disposition']
    task.write_new(folder/(name+'-accounting-closure.json'),result)
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['initialize','admit',*task.ATTEMPTS])
    for name in ('evidence','prior','historical'): parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--worker',action='store_true',help=argparse.SUPPRESS)
    args=parser.parse_args(argv)
    for name in ('evidence','prior','historical'): setattr(args,name,getattr(args,name).resolve())
    plan=obs.read_json(task.DOCS/'PLAN.json');plan_hash=obs.sha(task.DOCS/'PLAN.json')
    task.require(sys.flags.optimize==0,'optimized Python forbidden')
    roots(args,plan)
    if args.worker:
        try:
            return worker(args,plan)
        except Exception as exc:
            retain_failure(args.evidence,args.action,plan_hash,exc)
            raise
    task.verify_plan(plan)
    task.require(plan['resource_limits']==LIMITS and plan['allocations']==ALLOCATIONS and plan['archive_reservations']==ARCHIVES, 'resource freeze differs')
    args.evidence.mkdir(parents=True,exist_ok=True)
    with (args.evidence/'controller.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        ledger=args.evidence/'invocations.jsonl'
        if args.action=='initialize':
            task.require(not ledger.exists() and not list(args.evidence.glob('007-*')), 'ledger/evidence cannot be reset')
            task.write_new(ledger,dict(event='freeze',task=task.TASK,plan_sha256=plan_hash,limits=LIMITS));return 0
        audit=accounting(args.evidence,plan_hash)
        if args.action=='admit':
            try:
                receipt=admission(args.evidence,plan,audit)
            except ValueError as exc:
                receipt=dict(task=task.TASK,plan_sha256=plan_hash,passed=False,
                    conclusion='RESOURCE_OR_PREREQUISITE_ADMISSION_BLOCKED',reason=str(exc))
                task.write_new(args.evidence/'ADMISSION.json',receipt)
            print(obs.canonical(dict(passed=receipt['passed'])));return 0 if receipt['passed'] else 2
        review=obs.read_json(task.DOCS/'PREEXECUTION_REVIEW.json')
        task.require(review['passed'] and review['plan_sha256']==plan_hash and review['adapter_sources']==plan['adapter_sources'], 'independent frozen review missing/different')
        ceiling,storage=allocations(args.action,audit)
        prerequisites(args.evidence,args.action,plan,audit)
        live=capacity(args.evidence,storage)
        output=args.evidence/(args.action+'.json')
        task.require(not output.exists(), 'output name already exists')
        command=[sys.executable,str(Path(__file__).resolve()),args.action,'--evidence',str(args.evidence),
                 '--prior',str(args.prior),'--historical',str(args.historical),'--worker']
        started=time.monotonic();deadline=started+ceiling-2.
        append(ledger,dict(event='start',task=task.TASK,name=args.action,kind='full' if args.action in FULL_ALLOCATIONS else 'short',
            controller_pid=os.getpid(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),plan_sha256=plan_hash,
            ceiling=ceiling,memory_bytes=MEMORY,headroom=live,deadline_monotonic=deadline,controller_sha256=obs.sha(__file__),
            admission_sha256=obs.sha(args.evidence/'ADMISSION.json') if (args.evidence/'ADMISSION.json').exists() else None,command=command))
        env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',
            PYTHONHASHSEED='0',PYTHONPATH=str(ROOT),GRUDEVA007_LOCK_FD=str(lock.fileno()),GRUDEVA007_ATTEMPT=args.action)
        child=None;telemetry={};code=125;termination=None
        def terminated(signum,frame): raise InterruptedError('controller signal '+str(signum))
        handlers={s:signal.signal(s,terminated) for s in (signal.SIGTERM,signal.SIGINT)}
        log_path=args.evidence/(args.action+'.log')
        with log_path.open('x') as log:
            try:
                parent=os.getpid()
                child=subprocess.Popen(command,env=env,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,
                    pass_fds=(lock.fileno(),),preexec_fn=lambda:child_limits(parent),start_new_session=True)
                while child.poll() is None:
                    try:
                        for line in Path(f'/proc/{child.pid}/status').read_text().splitlines():
                            key,_,value=line.partition(':')
                            if key in ('VmPeak','VmHWM','VmSize','VmRSS'):
                                telemetry[key+'_bytes']=max(telemetry.get(key+'_bytes',0),int(value.split()[0])*1024)
                    except (FileNotFoundError,ProcessLookupError): pass
                    if time.monotonic()>=deadline:
                        termination='TIMEOUT';os.killpg(child.pid,signal.SIGKILL);child.wait();code=124;break
                    time.sleep(.02)
                else: code=child.returncode
            except BaseException as exc:
                termination=type(exc).__name__+': '+str(exc);log.write(termination+'\n')
            finally:
                if child is not None and child.poll() is None: os.killpg(child.pid,signal.SIGKILL);child.wait()
                for s,h in handlers.items(): signal.signal(s,h)
        if code==-signal.SIGALRM: termination='WORKER_DEADLINE_TIMEOUT'
        runtime=args.evidence/(args.action+'-runtime.json')
        observations=args.evidence/(args.action+'-observations.json')
        end=dict(event='end',name=args.action,seconds=time.monotonic()-started,exit_code=code,termination=termination,
            utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),telemetry=telemetry,
            peak_rss_bytes=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024,log_sha256=obs.sha(log_path),
            artifact_sha256=obs.sha(output) if output.exists() else None,
            observations_sha256=obs.sha(observations) if observations.exists() else None,
            runtime_sha256=obs.sha(runtime) if runtime.exists() else None,
            enforced_rlimit_as=obs.read_json(runtime)['enforced_rlimit_as'] if runtime.exists() else None,
            evidence_bytes={p.name:p.stat().st_size for p in args.evidence.glob('007-*') if p.is_file()})
        # Include all post-worker evidence hashing in charged wall time.
        end['seconds']=time.monotonic()-started
        append(ledger,end);finalize(args.evidence,plan_hash,args.action)
        print(obs.canonical({k:end[k] for k in ('name','seconds','exit_code','termination','telemetry')}))
        return 0 if code in (0,2) else 1


if __name__=='__main__': raise SystemExit(main())
