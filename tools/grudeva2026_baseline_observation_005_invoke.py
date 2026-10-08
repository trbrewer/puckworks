"""005 owner-amended external controller; original append-only ledger and lock."""
from __future__ import annotations

import datetime
import fcntl
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import sys
import time

MEMORY = 8*1024**3
POLICY = '005-owner-8gib-20261008'


def headroom(folder):
    mem = {k: int(v.split()[0])*1024 for k, v in
           (s.split(':', 1) for s in Path('/proc/meminfo').read_text().splitlines())}
    relative = Path('/proc/self/cgroup').read_text().strip().split('::', 1)[1]
    group = Path('/sys/fs/cgroup')/relative.lstrip('/')
    groups = []
    for path in [group, *group.parents]:
        if not str(path).startswith('/sys/fs/cgroup'):
            continue
        values = {n: (path/n).read_text().strip() for n in
                  ('memory.max', 'memory.high', 'memory.current') if (path/n).exists()}
        groups.append(dict(path=str(path), values=values))
        for key in ('memory.max', 'memory.high'):
            if values.get(key, 'max') != 'max':
                assert int(values[key])-int(values['memory.current']) >= MEMORY+2*1024**3, 'cgroup headroom blocked'
    limits = list(resource.getrlimit(resource.RLIMIT_AS))
    assert all(x == resource.RLIM_INFINITY or x >= MEMORY for x in limits), 'inherited address space blocked'
    assert mem['MemAvailable'] >= MEMORY+2*1024**3, 'host headroom blocked'
    free = shutil.disk_usage(folder).free
    assert free >= 32*1024**3, 'evidence storage headroom blocked'
    return dict(host_available_bytes=mem['MemAvailable'], cgroups=groups,
                inherited_rlimit_as=limits, storage_free_bytes=free,
                operating_margin_bytes=2*1024**3)


def main(argv=None):
    from puckworks.analysis import grudeva2026_baseline_observation_005 as obs
    from puckworks.analysis.grudeva2026_baseline_observation_005_report import (
        resource_audit, ATTRIBUTION_POLICY, ATTRIBUTION_ATTEMPTS)
    folder = Path(__file__).resolve().parent
    name, kind, phase, *command = sys.argv[1:] if argv is None else argv
    assert kind in ('short', 'full') and phase in ('development', 'final', 'correction')
    with (folder/'controller.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        accounting = resource_audit(folder)
        assert accounting['passed'], accounting['reasons']
        assert name not in accounting['starts'], 'attempt names cannot be reused'
        attribution = obs.read_json(folder/'attribution-amendment.json') if (folder/'attribution-amendment.json').exists() else None
        short_limit = 21 if attribution else 20
        assert accounting[kind] < {'short': short_limit, 'full': 10}[kind]
        used = accounting['seconds']
        primary = [n for n, s in accounting['starts'].items() if s['phase'] != 'correction']
        primary_seconds = sum(accounting['ends'][n]['seconds'] for n in primary)
        primary_full = sum(accounting['starts'][n]['kind'] == 'full' for n in primary)
        assert used < 1200
        ceiling = min(300., 1200.-used)
        if phase != 'correction':
            assert primary_seconds < 900 and (kind != 'full' or primary_full < 7)
            ceiling = min(ceiling, 900.-primary_seconds)
        amendment = obs.read_json(folder/'resource-amendment.json')
        assert amendment['policy'] == POLICY and amendment['memory_bytes'] == MEMORY
        persistence = obs.read_json(folder/'persistence-amendment.json') if (folder/'persistence-amendment.json').exists() else None
        assert obs.sha(__file__) == (attribution or persistence or amendment)['controller_sha256']
        assert '--allocation' in command, 'explicit bound allocation required'
        allocation = Path(command[command.index('--allocation')+1]).resolve()
        assert allocation.parent == folder, 'allocation must be retained beside original ledger'
        spec = obs.read_json(allocation)
        assert spec['attempt'] == name and spec['kind'] == kind
        assert spec['resource_amendment_sha256'] == obs.sha(folder/'resource-amendment.json')
        assert spec['controller_sha256'] == obs.sha(__file__)
        policy = POLICY
        if attribution:
            assert attribution['policy'] == ATTRIBUTION_POLICY and attribution['short_limit'] == 21
            assert name in ATTRIBUTION_ATTEMPTS and phase == 'final'
            index = ATTRIBUTION_ATTEMPTS.index(name)
            prior = {r['name'] for r in map(json.loads, (folder/'invocations-before-attribution.jsonl').read_text().splitlines())
                     if r['event'] == 'start'}
            added = [n for n in accounting['starts'] if n not in prior]
            assert added == list(ATTRIBUTION_ATTEMPTS[:index]), 'exact diagnostic execution order required'
            assert kind == ('short' if index == 4 else 'full')
            assert spec['role'] == ('single_axis_reduction' if index == 4 else 'single_axis_diagnostic')
            assert spec['attribution_amendment_sha256'] == obs.sha(folder/'attribution-amendment.json')
            assert spec['output'] == name+'.json'
            if index:
                previous = ATTRIBUTION_ATTEMPTS[index-1]
                end = accounting['ends'][previous]
                check_path = folder/(previous+'-attribution-check.json')
                assert end['exit_code'] in (0, 2) and end.get('diagnostic_check_sha256') == obs.sha(check_path)
                check = obs.read_json(check_path)
                assert check['safe_to_continue'], check.get('reasons')
                assert check['artifact_sha256'] == end['artifact_sha256']
            future = sum(attribution['estimated_seconds'][n] for n in ATTRIBUTION_ATTEMPTS[index+1:])
            ceiling = min(ceiling, 900.-primary_seconds-future, 1200.-used-future)
            assert ceiling > 0, 'remaining allocation and final reduction reserve do not fit'
            policy = ATTRIBUTION_POLICY
        if phase == 'correction':
            assert persistence and name == 'combined-persistence-recapture' and kind == 'full'
            assert spec['role'] == 'combined_persistence_recapture'
            assert spec['persistence_amendment_sha256'] == obs.sha(folder/'persistence-amendment.json')
        capacity = headroom(folder)
        root = Path.cwd()
        source = {str(p.relative_to(root)): obs.sha(p) for p in sorted((root/'puckworks/analysis').glob('grudeva2026_*.py'))}
        ledger = folder/'invocations.jsonl'
        def append(value):
            with ledger.open('a') as f:
                f.write(json.dumps(value, sort_keys=True)+'\n'); f.flush(); os.fsync(f.fileno())
        append(dict(name=name, kind=kind, phase=phase, event='start',
                    utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), command=command,
                    source_hashes=source, time_ceiling=ceiling, memory_bytes=MEMORY,
                    resource_policy=policy, controller_sha256=obs.sha(__file__),
                    resource_amendment_sha256=obs.sha(folder/'resource-amendment.json'),
                    allocation_file=allocation.name, allocation_sha256=obs.sha(allocation), headroom=capacity,
                    **(dict(short_limit=21, attribution_amendment_sha256=obs.sha(folder/'attribution-amendment.json'))
                       if attribution else {})))
        start = time.perf_counter()
        def limits():
            resource.setrlimit(resource.RLIMIT_AS, (MEMORY, MEMORY))
        env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                   NUMEXPR_NUM_THREADS='1', PYTHONPATH=str(root), PYTHONHASHSEED='0',
                   GRUDEVA005_ATTEMPT=name, GRUDEVA005_RESOURCE_POLICY=policy)
        telemetry, enforced, code = {}, None, 125
        with (folder/(name+'.log')).open('w') as log:
            try:
                p = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT,
                                     preexec_fn=limits, start_new_session=True)
                while p.poll() is None:
                    try:
                        status = Path(f'/proc/{p.pid}/status').read_text()
                        for line in status.splitlines():
                            key, _, value = line.partition(':')
                            if key in ('VmPeak', 'VmHWM', 'VmSize', 'VmRSS'):
                                telemetry[key+'_bytes'] = max(telemetry.get(key+'_bytes', 0), int(value.split()[0])*1024)
                        limits_line = next(v for v in Path(f'/proc/{p.pid}/limits').read_text().splitlines()
                                           if v.startswith('Max address space'))
                        enforced = [int(v) for v in limits_line.split()[3:5]]
                    except (FileNotFoundError, ProcessLookupError):
                        pass
                    if time.perf_counter()-start >= ceiling:
                        os.killpg(p.pid, signal.SIGKILL); p.wait(); code = 124; break
                    time.sleep(.05)
                else:
                    code = p.returncode
            except Exception as exc:
                log.write(repr(exc)); code = 125
            if 'p' in locals() and p.poll() is None:
                os.killpg(p.pid, signal.SIGKILL); p.wait()
        finish = dict(event='end', name=name, utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      seconds=time.perf_counter()-start, exit_code=code,
                      log_sha256=obs.sha(folder/(name+'.log')),
                      peak_rss_bytes=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024,
                      enforced_rlimit_as=enforced, telemetry=telemetry)
        artifact = Path(command[command.index('--output')+1])
        finish['artifact_sha256'] = obs.sha(artifact) if artifact.exists() else None
        finish['evidence_bytes'] = {f.name: f.stat().st_size for f in artifact.parent.glob(artifact.stem+'*') if f.is_file()}
        if attribution and kind == 'full':
            check = artifact.with_name(artifact.stem+'-attribution-check.json')
            finish['diagnostic_check_sha256'] = obs.sha(check) if check.is_file() else None
        append(finish)
        print(json.dumps(finish)); print((folder/(name+'.log')).read_text()[-2500:])
        return 0 if code in (0, 2) else code


if __name__ == '__main__':
    raise SystemExit(main())
