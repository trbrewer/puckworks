"""Locked, monitored offline 007 reassessment. No production entry point."""
from __future__ import annotations

import argparse
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from puckworks.analysis import grudeva2026_replay_reassessment_007 as study
from puckworks.analysis import grudeva2026_baseline_observation_005 as obs
from puckworks.analysis import grudeva2026_fine_baseline_qualification_007 as task
from tools import grudeva2026_fine_baseline_qualification_007_invoke as practical

STAGES={'diagnose':study.diagnose,'analyze':study.analyze}


def ledger(folder, plan_path=study.PLAN, stages=STAGES):
    path=folder/'ledger.jsonl'
    rows=[json.loads(s) for s in path.read_text().splitlines()] if path.exists() else []
    starts={};ends={};active=None
    for r in rows:
        if r['event']=='start':
            task.require(active is None and r['identity'] not in starts,'concurrent/duplicate reassessment')
            task.require(r['stage'] in stages and r['plan_sha256']==obs.sha(plan_path),'stage/plan mismatch')
            starts[r['identity']]=r;active=r['identity']
        elif r['event']=='spawn':
            task.require(r['identity']==active,'orphan spawn')
        elif r['event']=='end':
            task.require(r['identity']==active and r['seconds']>=0,'unmatched end')
            ends[active]=r;active=None
        else: raise ValueError('unknown reassessment event')
    return dict(starts=starts,ends=ends,unresolved=active,
        seconds=sum(r['seconds'] for r in ends.values()),offline_invocations=len(starts),production_invocations=0)


def worker(args,folder,plan,stages=STAGES,plan_path=study.PLAN):
    fd=int(os.environ['GRUDEVA007_REASSESS_LOCK'])
    a=os.fstat(fd);b=(args.evidence/'controller.lock').stat()
    task.require((a.st_dev,a.st_ino)==(b.st_dev,b.st_ino),'wrong inherited lock')
    audit=ledger(folder,plan_path,stages);start=audit['starts'][args.identity]
    task.require(audit['unresolved']==args.identity,'unmatched worker start')
    validate_worker_stage(start,args.stage,args.identity,audit)
    parent=practical.process(os.getppid())
    task.require(parent and all(parent[k]==start['controller'][k] for k in ('pid','boot_id','start_ticks')),'orphan worker')
    for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
        task.require(os.environ.get(name)=='1','uncontrolled threads')
    practical.child_safeguards(os.getppid())
    study.verify(args.evidence,plan)
    work=folder/args.identity
    task.write_new(work/'runtime.json',dict(environment=obs.environment(),actual_limits=practical.capacity(folder),
        production_invocations=0,application_limits=practical.UNLIMITED))
    result=stages[args.stage](args.evidence,work,plan)
    task.write_new(work/'completion.json',dict(stage=args.stage,identity=args.identity,
        result_disposition=result['disposition'],production_invocations=0,plan_sha256=obs.sha(plan_path)))
    return 0


def validate_worker_stage(start,stage,identity,audit):
    task.require(start['stage']==stage,'worker/start stage mismatch')
    ordinal=sum(r['stage']==stage for r in audit['starts'].values())
    task.require(identity==f'{stage}-{ordinal:04d}','worker identity/ordinal mismatch')


def main(stages=STAGES,plan_path=study.PLAN,folder_name='replay_reassessment'):

    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=('run','worker','status'))
    p.add_argument('--stage',choices=tuple(stages))
    p.add_argument('--evidence',type=Path,required=True)
    p.add_argument('--identity');p.add_argument('--reason')
    args=p.parse_args();folder=args.evidence/folder_name
    plan=obs.read_json(plan_path)
    task.require(obs.digest(str(args.evidence.resolve()))==plan['evidence_root_sha256'],'wrong root')
    if args.action=='status':
        print(obs.canonical(ledger(folder,plan_path,stages)));return 0
    if args.action=='worker':return worker(args,folder,plan,stages,plan_path)
    task.require(args.stage in stages,'offline stage required')
    folder.mkdir(exist_ok=True)
    with (args.evidence/'controller.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        audit=ledger(folder,plan_path,stages)
        task.require(audit['unresolved'] is None,'unresolved prior start; no new work')
        earlier=[s for s in audit['starts'].values() if s['stage']==args.stage]
        task.require(not earlier or args.reason,'repeat offline work requires an explicit recorded reason')
        study.verify(args.evidence,plan)
        live=practical.capacity(folder);task.require(not practical.safety_reasons(live),'unsafe current machine headroom')
        task.require(live['disk_free_bytes']>=live['disk_operating_margin_bytes']+plan['additional_storage_reserve_bytes'],
                     'insufficient remaining output storage')
        key=f"{args.stage}-{len(earlier)+1:04d}";work=folder/key;work.mkdir()
        parent=practical.process(os.getpid());started=time.perf_counter()
        practical.append(folder/'ledger.jsonl',dict(event='start',identity=key,stage=args.stage,
            utc=practical.utc(),plan_sha256=obs.sha(plan_path),controller={k:parent[k] for k in ('pid','boot_id','start_ticks')},
            reason=args.reason,production_invocations=0))
        env=dict(os.environ,GRUDEVA007_REASSESS_LOCK=str(lock.fileno()))
        command=[sys.executable,str(Path(sys.argv[0]).resolve()),'worker','--stage',args.stage,
                 '--evidence',str(args.evidence),'--identity',key]
        process=None;termination=None;previous=None;peak={}
        try:
            with (work/'worker.log').open('x') as log:
                process=subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT,
                    pass_fds=(lock.fileno(),),start_new_session=True)
                practical.append(folder/'ledger.jsonl',dict(event='spawn',identity=key,utc=practical.utc(),
                    process=practical.process(process.pid)))
                while process.poll() is None:
                    snap=practical.capacity(folder,process.pid)
                    snap.update(elapsed_seconds=time.perf_counter()-started,warnings=practical.safety_reasons(snap))
                    practical.append(work/'progress.jsonl',snap)
                    for k,v in (snap.get('process') or {}).items():
                        if k.startswith('Vm'):peak[k]=max(peak.get(k,0),v)
                    if previous is not None and practical.safety_reasons(snap,previous):
                        termination='evidenced_machine_safety';os.killpg(process.pid,signal.SIGTERM)
                    previous=snap
                    time.sleep(15)
                code=process.returncode
        except BaseException:
            if process is not None and process.poll() is None:
                os.killpg(process.pid,signal.SIGTERM)
                process.wait()  # no arbitrary deadline
            raise  # preserve unresolved start on controller failure/cancellation
        result={p.name:obs.sha(p) for p in work.iterdir() if p.is_file() and p.name!='progress.jsonl'}
        practical.append(folder/'ledger.jsonl',dict(event='end',identity=key,utc=practical.utc(),
            seconds=time.perf_counter()-started,exit_code=code,termination=termination,peak_memory_bytes=peak,
            outputs=result,production_invocations=0))
        print(obs.canonical(ledger(folder,plan_path,stages)))
        return code


if __name__=='__main__':raise SystemExit(main())
