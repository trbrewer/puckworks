"""Fixed 006 serial controller; no arbitrary command, reset, retry, or 005 authority."""
from __future__ import annotations

import argparse
import ctypes
import datetime
import fcntl
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from puckworks.analysis import grudeva2026_spatial_resolution_006 as task
from puckworks.analysis import grudeva2026_baseline_observation_005 as obs

MEMORY = 8589934592
LIMITS = dict(full=1, short=2, aggregate_seconds=600., per_invocation_seconds=300., memory_bytes=MEMORY)
KINDS = ('short', 'full', 'short')
ALLOCATIONS = (90., 290., 180.)


def append(ledger, value):
    with ledger.open('a') as stream:
        stream.write(obs.canonical(value)+'\n'); stream.flush(); os.fsync(stream.fileno())


def accounting(folder, plan_hash):
    rows = [json.loads(line) for line in (Path(folder)/'invocations.jsonl').read_text().splitlines()]
    task.require(rows and rows[0] == dict(event='freeze', task=task.TASK, plan_sha256=plan_hash, limits=LIMITS),
                 'ledger freeze identity mismatch')
    starts, ends = {}, {}
    active = None
    for row in rows[1:]:
        name = row['name']
        task.require(name in task.ATTEMPTS, 'unauthorized ledger attempt')
        if row['event'] == 'start':
            task.require(active is None and name not in starts, 'concurrent/duplicate ledger start')
            i = task.ATTEMPTS.index(name)
            task.require(row['kind'] == KINDS[i] and row['ceiling'] <= ALLOCATIONS[i], 'invalid allocation')
            task.require(row['memory_bytes'] == MEMORY and row['plan_sha256'] == plan_hash,
                         'ledger policy/source mismatch')
            starts[name], active = row, name
        elif row['event'] == 'end':
            task.require(active == name and name not in ends, 'unmatched/duplicate completion')
            task.require(row['seconds'] >= 0, 'negative consumption')
            ends[name], active = row, None
        else:
            raise ValueError('unknown ledger event')
    seconds = sum(r['seconds'] for r in ends.values())
    unresolved = [n for n in starts if n not in ends]
    reserved = seconds+sum(starts[n]['ceiling'] for n in unresolved)
    full = sum(r['kind'] == 'full' for r in starts.values())
    short = len(starts)-full
    reasons = []
    if unresolved:
        reasons.append('unresolved start; ceiling reserved; no further execution')
    if full > 1 or short > 2 or reserved > 600 or any(r['seconds'] > 300 for r in ends.values()):
        reasons.append('resource ceiling exceeded')
    return dict(full=full, short=short, seconds=seconds, charged_or_reserved_seconds=reserved,
                unresolved_starts=unresolved, starts=starts, ends=ends, reasons=reasons, passed=not reasons)


def capacity(folder):
    # Same existing 005 headroom policy; no host/cgroup/inherited limit is raised.
    from tools.grudeva2026_baseline_observation_005_invoke import headroom
    try:
        return headroom(Path(folder))
    except AssertionError as exc:
        raise ValueError(str(exc)) from exc


def allocation(index, audit):
    task.require(audit['passed'], '; '.join(audit['reasons']))
    name = task.ATTEMPTS[index]
    task.require(name not in audit['starts'], 'duplicate attempt forbidden')
    task.require(list(audit['starts']) == list(task.ATTEMPTS[:index]), 'exact execution order required')
    task.require(audit[KINDS[index]] < LIMITS[KINDS[index]], 'attempt ceiling reached')
    future = sum(ALLOCATIONS[index+1:])
    ceiling = min(ALLOCATIONS[index], 600.-audit['seconds']-future)
    task.require(ceiling > 0, 'aggregate ceiling cannot reserve mandatory downstream work')
    return ceiling


def child_limits(parent):
    # Linux parent-death signal plus independent deadline prevents an orphan run.
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(1, signal.SIGKILL, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), 'PR_SET_PDEATHSIG failed')
    if os.getppid() != parent:
        os.kill(os.getpid(), signal.SIGKILL)
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY, MEMORY))


def worker(args, plan):
    index = task.ATTEMPTS.index(args.action)
    fd = int(os.environ.get('GRUDEVA006_LOCK_FD', '-1'))
    task.require(fd >= 0 and os.environ.get('GRUDEVA006_ATTEMPT') == args.action,
                 'scientific work requires the 006 controller')
    lock = args.evidence/'controller.lock'
    task.require(os.fstat(fd).st_ino == lock.stat().st_ino and os.fstat(fd).st_dev == lock.stat().st_dev,
                 'wrong controller lock')
    audit = accounting(args.evidence, obs.sha(task.DOCS/'PLAN.json'))
    start = audit['starts'].get(args.action, {})
    task.require(audit['unresolved_starts'] == [args.action] and start.get('controller_pid') == os.getppid(),
                 'no matching live controller start')
    task.require(resource.getrlimit(resource.RLIMIT_AS) == (MEMORY, MEMORY), 'wrong address-space limits')
    for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        task.require(os.environ.get(key) == '1', 'numerical threading not controlled')
    # Supervisor remains primary watchdog; the worker independently terminates on deadline.
    remaining = float(os.environ['GRUDEVA006_DEADLINE'])-time.monotonic()
    task.require(remaining > 0, 'allocation expired before worker entry')
    signal.setitimer(signal.ITIMER_REAL, remaining)
    task.write_new(args.evidence/(args.action+'-runtime.json'),
        dict(task=task.TASK, attempt=args.action, enforced_rlimit_as=list(resource.getrlimit(resource.RLIMIT_AS)),
             environment=obs.environment()))
    task.verify_sources(plan)
    task.require(obs.environment() == plan['environment'], 'execution environment changed')
    output = args.evidence/(args.action+'.json')
    if index == 0:
        result = task.screen(args.evidence, args.historical, plan)
        return 0 if result['passed'] else 2
    if index == 1:
        task.require_screen(args.evidence, plan, audit)
        task.historical_inputs(args.historical, plan)
        task.capture(output, plan)
        return 0
    from puckworks.analysis.grudeva2026_spatial_resolution_006_report import reduce
    result = reduce(args.evidence, args.historical, plan, audit)
    return 0 if result['conclusion'] == 'A' else 2


def finalize(folder, plan_hash):
    """Accounting-only completion; retains preliminary report and performs no numerics."""
    audit = accounting(folder, plan_hash)
    last = next((n for n in reversed(task.ATTEMPTS) if n in audit['ends']), None)
    task.require(last is not None, 'no completed invocation')
    path = Path(folder)/(last+'.json')
    summary = dict(task=task.TASK, physical_validation='NOT_ESTABLISHED', resources=audit,
                   plan_sha256=plan_hash, preliminary_file=path.name,
                   preliminary_sha256=obs.sha(path) if path.exists() else None)
    if last == task.ATTEMPTS[0]:
        raw = obs.read_json(path) if path.exists() else {}
        summary.update(conclusion='B' if raw.get('disposition') == 'FIXED_READOUT_PREREQUISITE_FAILS' else None,
                       disposition=raw.get('disposition', 'EXECUTION_INCOMPLETE'), production_attempted=False)
    elif last == task.ATTEMPTS[2] and path.exists():
        raw = obs.read_json(path)
        summary.update(conclusion=raw.get('conclusion'), disposition=raw.get('disposition'), production_attempted=True)
    else:
        summary.update(conclusion=None, disposition='EXECUTED_UNQUALIFIED', production_attempted=True)
    resource_failure = Path(folder)/(last+'-resource-failure.json')
    if resource_failure.exists() or (path.exists() and obs.read_json(path).get('conclusion') == 'D'):
        summary.update(conclusion='D', disposition='FIXED_RESOURCE_MEMORY_EXHAUSTED')
    if audit['ends'][last].get('exit_code') in (124, -signal.SIGALRM):
        summary.update(conclusion='D', disposition='FIXED_RESOURCE_EXECUTION_TIMEOUT')
    if not audit['passed']:
        summary.update(conclusion='D', disposition='RESOURCE_ACCOUNTING_INCOMPLETE')
    target = Path(folder)/(last+'-accounting-closure.json')
    task.write_new(target, summary)
    return summary


def verify_roots(evidence, historical, plan):
    task.require(obs.digest(str(Path(evidence).resolve())) == plan['evidence_root_sha256'],
                 '006 evidence root differs; consumption cannot move to a new ledger')
    task.require(obs.digest(str(Path(historical).resolve())) == plan['historical_root_sha256'],
                 'historical evidence root differs')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['initialize', *task.ATTEMPTS])
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--historical', type=Path, required=True)
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    args.evidence, args.historical = args.evidence.resolve(), args.historical.resolve()
    task.require(args.evidence != args.historical, '006 and 005 evidence roots must be distinct')
    plan_path = task.DOCS/'PLAN.json'
    task.require(sys.flags.optimize == 0, 'optimized Python is not the frozen controller environment')
    plan = obs.read_json(plan_path)
    plan_hash = obs.sha(plan_path)
    verify_roots(args.evidence, args.historical, plan)
    if args.worker:
        try:
            return worker(args, plan)
        except MemoryError:
            task.write_new(args.evidence/(args.action+'-resource-failure.json'),
                           dict(task=task.TASK, attempt=args.action, failure='MemoryError',
                                conclusion='D', disposition='FIXED_RESOURCE_MEMORY_EXHAUSTED'))
            raise
    task.verify_sources(plan)
    args.evidence.mkdir(parents=True, exist_ok=True)
    with (args.evidence/'controller.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        ledger = args.evidence/'invocations.jsonl'
        if args.action == 'initialize':
            task.require(not ledger.exists() and not list(args.evidence.glob('006-*.json')),
                         'existing ledger/evidence cannot be reset')
            task.write_new(ledger, dict(event='freeze', task=task.TASK, plan_sha256=plan_hash, limits=LIMITS))
            return 0
        audit = accounting(args.evidence, plan_hash)
        index = task.ATTEMPTS.index(args.action)
        ceiling = allocation(index, audit)
        if index:
            task.require_screen(args.evidence, plan, audit)
        if index == 2:
            previous = audit['ends'][task.ATTEMPTS[1]]
            candidate = args.evidence/(task.ATTEMPTS[1]+'.json')
            task.require(candidate.is_file() and previous.get('artifact_sha256') == obs.sha(candidate),
                         'no trustworthy candidate partial evidence for reduction')
        headroom = capacity(args.evidence)
        output = args.evidence/(args.action+'.json')
        task.require(not output.exists(), 'existing output cannot be overwritten')
        command = [sys.executable, str(Path(__file__).resolve()), args.action, '--evidence', str(args.evidence),
                   '--historical', str(args.historical), '--worker']
        start = time.monotonic()
        # Leave one second for termination/accounting within the allocated wall time.
        deadline = start+ceiling-1.
        append(ledger, dict(event='start', name=args.action, kind=KINDS[index], task=task.TASK,
            controller_pid=os.getpid(), utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            plan_sha256=plan_hash, ceiling=ceiling, memory_bytes=MEMORY, headroom=headroom,
            controller_sha256=obs.sha(__file__), command=command))
        env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
            NUMEXPR_NUM_THREADS='1', PYTHONHASHSEED='0', PYTHONPATH=str(ROOT),
            GRUDEVA006_LOCK_FD=str(lock.fileno()), GRUDEVA006_ATTEMPT=args.action,
            GRUDEVA006_DEADLINE=str(deadline))
        telemetry, code, termination = {}, 125, None
        child = None
        log_path = args.evidence/(args.action+'.log')
        def terminated(signum, frame):
            raise InterruptedError('controller signal '+str(signum))
        handlers = {s:signal.signal(s, terminated) for s in (signal.SIGTERM, signal.SIGINT)}
        with log_path.open('x') as log:
            try:
                parent = os.getpid()
                child = subprocess.Popen(command, env=env, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                    pass_fds=(lock.fileno(),), preexec_fn=lambda:child_limits(parent), start_new_session=True)
                while child.poll() is None:
                    try:
                        for line in Path(f'/proc/{child.pid}/status').read_text().splitlines():
                            key, _, value = line.partition(':')
                            if key in ('VmPeak','VmHWM','VmSize','VmRSS'):
                                telemetry[key+'_bytes'] = max(telemetry.get(key+'_bytes',0),int(value.split()[0])*1024)
                    except (FileNotFoundError, ProcessLookupError):
                        pass
                    if time.monotonic() >= deadline:
                        termination = 'TIMEOUT'; os.killpg(child.pid, signal.SIGKILL); child.wait(); code=124; break
                    time.sleep(.02)
                else:
                    code = child.returncode
            except BaseException as exc:
                termination = type(exc).__name__+': '+str(exc)
                log.write(termination+'\n')
            finally:
                if child is not None and child.poll() is None:
                    os.killpg(child.pid, signal.SIGKILL); child.wait()
                for s, handler in handlers.items():
                    signal.signal(s, handler)
        if code == -signal.SIGALRM:
            termination = 'WORKER_DEADLINE_TIMEOUT'
        finish = dict(event='end', name=args.action, seconds=time.monotonic()-start, exit_code=code,
            termination=termination, utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            telemetry=telemetry, peak_rss_bytes=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024,
            log_sha256=obs.sha(log_path), artifact_sha256=obs.sha(output) if output.exists() else None,
            evidence_bytes={p.name:p.stat().st_size for p in args.evidence.glob('006-*') if p.is_file()})
        observations = output.with_name(output.stem+'-observations.json')
        finish['observations_sha256'] = obs.sha(observations) if observations.exists() else None
        runtime = args.evidence/(args.action+'-runtime.json')
        finish['runtime_sha256'] = obs.sha(runtime) if runtime.exists() else None
        finish['enforced_rlimit_as'] = obs.read_json(runtime)['enforced_rlimit_as'] if runtime.exists() else None
        append(ledger, finish)
        finalize(args.evidence, plan_hash)
        print(obs.canonical(finish))
        return 0 if code in (0,2) else 1


if __name__ == '__main__':
    raise SystemExit(main())
