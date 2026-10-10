"""Small controls for the bounded native attempt; no scientific executions."""
import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from tools import capture_grudeva2026_native_010 as native
from tools import grudeva2026_remaining_010 as adapter


def put(path, value):
    path.write_text(json.dumps(value))
    return {'path':str(path), 'sha256':adapter.digest(path)}


@pytest.fixture
def attempt(tmp_path, monkeypatch):
    root = tmp_path/'repo'; (root/adapter.DOC).mkdir(parents=True)
    parent = {'new_row_order':['repeat','axial_coarse'],
              'recovered_anchor':{'records':{'admission':{'sha256':'original'}}},
              'implementation':{'tools/run_grudeva2026_full_reference_010.py':'old-runner',
                                'science.py':'unchanged'},
              'adapter_files':{'tools/grudeva2026_remaining_010.py':'old-adapter'},
              'environment':{'unchanged':True}, 'evidence_directory_identity':'old'}
    record = put(root/adapter.DOC/'REMAINING.json',parent)
    monkeypatch.setattr(adapter,'PARENT_BINDING_SHA256',record['sha256'])
    debugger = tmp_path/'gdb'; debugger.write_bytes(b'fixture-debugger')
    monkeypatch.setattr(native,'DEBUGGER',str(debugger))
    supervisor = tmp_path/'supervisor.py'; supervisor.write_bytes(b'fixture-supervisor')
    spec = {'parent_binding_sha256':record['sha256'], 'authorization':adapter.NATIVE_AUTHORIZATION,
            'starting_reviewed_head':adapter.NATIVE_HEAD, 'new_row_order':parent['new_row_order'][:],
            'changed_sources':{'tools/run_grudeva2026_full_reference_010.py':'new-runner',
                               'tools/grudeva2026_remaining_010.py':'new-adapter'},
            'added_sources':{'tools/capture_grudeva2026_native_010.py':'capture',
                             'tests/test_grudeva2026_native_010.py':'tests'},
            'parent_anchor_admission':put(tmp_path/'admission.json',{
                'status':'PASS','binding_sha256':record['sha256'],
                'actual_admission_records':{'admission':'original'}}),
            'parent_review':put(tmp_path/'review.json',{'candidate_commit':adapter.NATIVE_HEAD,
                'disposition':'PASS_FOR_BOUNDED_CRASH_STOP_CLOSEOUT_ONLY'}),
            'capability':put(tmp_path/'capability.json',{'status':'PASS_NATIVE_CAPTURE_CAPABILITY',
                                                     'source_sha256':'capture'}),
            'debugger':{'path':str(debugger),'sha256':adapter.digest(debugger),'settings':native.SETTINGS},
            'preserved_records':{'interrupted':put(tmp_path/'interrupted.json',{'exit':-11})},
            'supervisor':{'path':str(supervisor),'sha256':adapter.digest(supervisor)},
            'evidence_directory_identity':'exclusive-new'}
    return root,parent,spec


def test_native_transition_retains_science_and_parent(attempt):
    root,parent,spec = attempt
    before = copy.deepcopy(parent)
    result = adapter.native_binding(root,parent,spec)
    assert parent == before
    assert result['environment'] == parent['environment']
    assert result['implementation']['science.py']=='unchanged'
    assert result['recovered_anchor']==parent['recovered_anchor']
    assert result['implementation']['tools/run_grudeva2026_full_reference_010.py']=='new-runner'
    assert result['evidence_directory_identity']=='exclusive-new'


@pytest.mark.parametrize('fault',['parent','order','anchor','source','capability','debugger','supervisor','receipt'])
def test_native_transition_rejects_stale_or_widened_binding(attempt,fault):
    root,parent,spec = attempt
    if fault=='parent': spec['parent_binding_sha256']='stale'
    elif fault=='order': spec['new_row_order'].reverse()
    elif fault=='anchor': spec['new_row_order'].insert(0,'anchor')
    elif fault=='source': spec['changed_sources']['science.py']='changed'
    elif fault=='capability': spec['added_sources']['tools/capture_grudeva2026_native_010.py']='stale'
    elif fault=='debugger': Path(spec['debugger']['path']).write_bytes(b'changed')
    elif fault=='supervisor': Path(spec['supervisor']['path']).write_bytes(b'changed')
    else: Path(spec['parent_anchor_admission']['path']).write_text('{}')
    with pytest.raises(ValueError): adapter.native_binding(root,parent,spec)


def test_native_command_retains_aslr_and_intercepts_fatal_signals(tmp_path):
    command = native.command(tmp_path/'private',['/usr/bin/python3.12','-I','-S','-X','faulthandler','fixture.py'])
    assert 'set disable-randomization off' in command
    assert 'set startup-with-shell off' in command
    assert 'set auto-load off' in command
    assert 'set debuginfod enabled off' in command
    assert 'handle SIGSEGV stop print nopass' in command
    assert command[command.index('--args')+1:] == ['/usr/bin/python3.12','-I','-S','-X','faulthandler','fixture.py']
    with pytest.raises(ValueError): native.command(tmp_path,['python','-c','import ctypes'])


@pytest.mark.parametrize('outcome',[{'kind':'exited','child_exit_code':7},
    {'kind':'native_signal_stop','child_exit_code':None}, {'kind':'debugger_error','child_exit_code':0}])
def test_debugger_success_cannot_substitute_for_child_success(tmp_path,outcome):
    put(tmp_path/'OUTCOME.json',outcome)
    with pytest.raises(RuntimeError): native.require_child_success(tmp_path)
    put(tmp_path/'OUTCOME.json',{'kind':'exited','child_exit_code':0})
    assert native.require_child_success(tmp_path)['child_exit_code']==0


def test_numerical_reader_remains_supervised_and_checks_actual_child(tmp_path,monkeypatch):
    from tools import run_grudeva2026_full_reference_010 as runner
    monkeypatch.setattr(sys,'argv',['runner','--native'])
    monkeypatch.setattr(runner,'REMAINING_RUNTIME',{})
    seen=[]
    def run(command,**kwargs):
        seen.append(command)
        output=tmp_path/'bundles-native-reader';output.mkdir()
        put(output/'OUTCOME.json',{'kind':'native_signal_stop','child_exit_code':None})
        return subprocess.CompletedProcess(command,0)
    monkeypatch.setattr(subprocess,'run',run)
    with pytest.raises(RuntimeError): runner.fresh_read(tmp_path,'bundles')
    assert seen[0][0]==native.DEBUGGER and '--native' in seen[0]
    assert adapter.read(tmp_path/'bundles-reader-exit.json')['exit_code']==0


def test_native_path_refuses_uninstrumented_process(monkeypatch):
    original = Path.read_text
    monkeypatch.setattr(Path,'read_text',lambda p,*a,**k: 'TracerPid:\t0\n'
                       if str(p)=='/proc/self/status' else original(p,*a,**k))
    with pytest.raises(ValueError,match='live GDB tracer'):
        adapter.require_native_tracer({'native_attempt':{'debugger':{'path':native.DEBUGGER,'sha256':'unused'}}})
