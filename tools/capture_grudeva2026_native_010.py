"""Bounded GDB capture for the explicitly authorized 010 repeat/refinements.

No scientific imports. GDB executes capture() in its embedded Python; the
numerical inferior retains its separately verified interpreter and arguments.
"""
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import time

DEBUGGER = '/usr/bin/gdb'
SETTINGS = ['set auto-load off', 'set debuginfod enabled off',
            'set disable-randomization off', 'set startup-with-shell off',
            'set pagination off', 'set confirm off', 'set print elements 24',
            'set print repeats 4', 'set print max-depth 3',
            'set max-value-size 65536', 'set use-coredump-filter on',
            'set dump-excluded-mappings off', 'set follow-fork-mode parent',
            'set detach-on-fork on',
            *[f'handle {s} stop print nopass' for s in
              ('SIGSEGV', 'SIGBUS', 'SIGILL', 'SIGFPE', 'SIGABRT')]]


def command(output, inferior):
    # GDB --args shell-escapes words even with startup-with-shell off. The
    # declared 010 file/flag arguments need no such encoding; reject others.
    if any(shlex.quote(str(arg)) != str(arg) for arg in inferior):
        raise ValueError('Native010 requires the declared whitespace-free argument tokens')
    code = f"import runpy; runpy.run_path({str(Path(__file__).resolve())!r})['capture']({str(output)!r})"
    return [DEBUGGER, '-nx', '-nh', '--batch',
            *[part for setting in SETTINGS for part in ('-iex', setting)],
            '-ex', 'python '+code, '--args', *map(str, inferior)]


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        while block := stream.read(4*1024**2):
            h.update(block)
    return h.hexdigest()


def require_child_success(output):
    record = json.loads((Path(output)/'OUTCOME.json').read_text())
    if record['kind'] != 'exited' or record['child_exit_code'] != 0:
        raise RuntimeError('Native child did not succeed: '+str(output))
    return record


def capture(output):
    import gdb
    os.umask(0o077)
    output = Path(output)
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    state = {'signal':None, 'exit':None, 'pid':None}
    loaded = set()

    def save(name, value):
        with (output/name).open('x') as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write('\n'); stream.flush(); os.fsync(stream.fileno())

    def text_record(name, value):
        with (output/name).open('x') as stream:
            stream.write(value); stream.flush(); os.fsync(stream.fileno())

    def continued(event):
        if state['pid'] is None:
            state['pid'] = gdb.selected_inferior().pid
            save('INFERIOR.json', {'pid':state['pid'], 'debugger_pid':os.getpid(),
                 'personality':Path(f"/proc/{state['pid']}/personality").read_text().strip(),
                 'core_filter':Path(f"/proc/{state['pid']}/coredump_filter").read_text().strip(),
                 'recorded_unix':time.time()})

    def library(event):
        path = Path(getattr(event, 'new_objfile', event).filename)
        if str(path) in loaded:
            return
        loaded.add(str(path))
        record = {'path':str(path), 'recorded_unix':time.time()}
        try:
            info = path.stat()
            record.update(sha256=digest(path), bytes=info.st_size,
                          device=info.st_dev, inode=info.st_ino)
        except Exception as exc:
            record['unavailable'] = repr(exc)
        with (output/'loaded-files.jsonl').open('a') as stream:
            stream.write(json.dumps(record, sort_keys=True)+'\n')
            stream.flush(); os.fsync(stream.fileno())

    def stopped(event):
        if isinstance(event, gdb.SignalEvent):
            state['signal'] = event.stop_signal
            # Primary signal is durable before every fallible enrichment.
            save('PRIMARY_SIGNAL.json', {'kind':'native_signal_stop',
                 'signal':event.stop_signal, 'pid':gdb.selected_inferior().pid,
                 'recorded_unix':time.time(), 'continued_after_signal':False})

    def exited(event):
        state['exit'] = getattr(event, 'exit_code', None)
        save('EXIT_EVENT.json', {'child_exit_code':state['exit'],
             'after_intercepted_signal':state['signal'] is not None})

    gdb.events.cont.connect(continued)
    gdb.events.new_objfile.connect(library)
    gdb.events.stop.connect(stopped)
    gdb.events.exited.connect(exited)
    for obj in gdb.objfiles():
        library(obj)
    save('CONFIGURATION.json', {'gdb_version':gdb.VERSION, 'settings':SETTINGS,
         'source_sha256':digest(__file__), 'debugger_sha256':digest(DEBUGGER),
         'inferior_arguments':gdb.execute('show args', to_string=True),
         'disable_randomization':gdb.execute('show disable-randomization', to_string=True),
         'observation_effects':'ptrace and library-load identity recording change timing; no claim of original schedule recreation',
         'forks':'Readers have their own native launcher; unrelated subprocesses follow original parent/detach semantics'})
    errors = []
    try:
        gdb.execute('run')
        if state['signal'] is not None:
            for name, query in [('signal','p $_siginfo'), ('registers','info registers'),
                                ('instruction','x/12i $pc-16'), ('threads','info threads'),
                                ('native-stack','thread apply all bt 32'),
                                ('fault-frame','info args\ninfo locals'),
                                ('libraries','info sharedlibrary'), ('mappings','info proc mappings')]:
                try:
                    value = '\n'.join(gdb.execute(q, to_string=True) for q in query.splitlines())
                    text_record(name+'.txt', value[:262144])
                    if len(value)>262144:
                        errors.append(name+': textual output truncated at262144 characters')
                except Exception as exc:
                    errors.append(name+': '+repr(exc))
            try:
                maps = Path(f"/proc/{state['pid']}/maps").read_text()
                text_record('proc-maps.txt', maps)
                # Conservative readable-mapping size; never increase a limit.
                estimate = sum(int(line.split()[0].split('-')[1],16)-int(line.split()[0].split('-')[0],16)
                               for line in maps.splitlines() if line.split()[1].startswith('r'))
                free = shutil.disk_usage(output).free
                if free < estimate + 64*1024**3:
                    save('CORE.json', {'status':'SKIPPED_UNSAFE_HEADROOM',
                         'estimated_readable_bytes':estimate, 'free_bytes':free})
                else:
                    core = output/'inferior.core'
                    note = gdb.execute('generate-core-file '+str(core), to_string=True)
                    save('CORE.json', {'status':'WRITTEN', 'path':str(core),
                         'bytes':core.stat().st_size, 'sha256':digest(core),
                         'gdb_message':note[:8192], 'estimated_readable_bytes':estimate,
                         'free_bytes_before':free, 'mode':oct(core.stat().st_mode & 0o777)})
            except Exception as exc:
                errors.append('core: '+repr(exc))
            save('ENRICHMENT.json', {'errors':errors,
                 'unavailable_state':'Optimized-out arguments/locals are unavailable; no matrix or operand reconstruction',
                 'continued_after_signal':False})
            # A stopped fatal signal is never delivered and then resumed.
            gdb.execute('kill')
            outcome = {'kind':'native_signal_stop', 'signal':state['signal'],
                       'child_exit_code':state['exit'], 'cleanup':'killed_without_resuming'}
        else:
            outcome = {'kind':'exited', 'child_exit_code':state['exit']}
    except Exception as exc:
        save('DEBUGGER_ERROR.json', {'error':repr(exc), 'primary_signal':state['signal']})
        outcome = {'kind':'debugger_error', 'child_exit_code':state['exit'], 'signal':state['signal']}
        if gdb.selected_inferior().pid:
            gdb.execute('kill')
    save('OUTCOME.json', outcome)
    success = outcome['kind']=='exited' and outcome['child_exit_code']==0
    gdb.execute('quit '+('0' if success else '1'))
