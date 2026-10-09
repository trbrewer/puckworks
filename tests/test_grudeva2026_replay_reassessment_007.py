"""Manufactured offline-reader/control tests; no canonical numerical work."""
from copy import deepcopy
from decimal import Decimal
from types import SimpleNamespace

import numpy as np
import pytest

from puckworks.analysis import grudeva2026_replay_reassessment_007 as r
from tools import grudeva2026_replay_reassessment_007_invoke as ctl


def fixture(path):
    size=8
    arrays=dict(accepted_t=np.array([0.,1.]),accepted_y=np.ones((size,2)),breaks=np.array([0.,1.]),
        orders=np.array([1]),shifts=np.array([[1.,0.,0.,0.,0.]]),
        denominators=np.ones((1,5)),step_bounds=np.array([[0.,1.]]),D_0=np.array([np.ones(size),np.zeros(size)]))
    archive=path/'manufactured.npz';np.savez(archive,**arrays)
    geometry=dict(w=[.6,.4],rates=[1.,2.],face=[0.,.75,1.])
    segment=dict(file=archive.name,sha256=r.obs.sha(archive),array_manifest={k:r.obs._array_identity(v) for k,v in arrays.items()},
        persistence_schema='005.segment-persistence.v2',artifact_integrity='PASS',array_fidelity='PASS',
        capture_outcome='FAILED',numerical_replay='FAILED',unavailable_reason='ValueError: live dense replay failed',
        failure=dict(stage='numerical_replay',exception_type='ValueError',exception_message='live dense replay failed'),
        geometry=geometry,event_channels=0,dense_side='right',valid_interval=[0.,1.],requested_interval=[0.,1.],fixed=True)
    meta=dict(schema=r.obs.SCHEMA,controls=dict(cells=2,modes=1,front_mesh_power=2.),geometry=geometry,
        state_layout=dict(size=size,modal_shape=[2,2],modal_axis=0,order='s,liquid,mode-major,cup'),segments=[segment])
    file=path/'manufactured.json';file.write_text(r.obs.canonical(meta));return file,meta


def test_failed_reader_preserves_original_metadata_and_normal_refusal(tmp_path):
    path,meta=fixture(tmp_path);before=path.read_bytes()
    with pytest.raises(ValueError,match='live dense'):r.obs.Trajectory(path)
    tr=r.DiagnosticTrajectory(path)
    try:
        assert tr.meta==meta and tr.segments[0].meta['capture_outcome']=='FAILED'
        np.testing.assert_array_equal(tr.evaluate(.5)[0],np.ones(8))
        assert tr.evaluate.__func__ is r.obs.Trajectory.evaluate
        assert tr.activation.__func__ is r.obs.Trajectory.activation
    finally:tr.close()
    assert path.read_bytes()==before


@pytest.mark.parametrize('fault',['hash','manifest','geometry','interval','order','fidelity','other_failure'])
def test_diagnostic_reader_rejects_real_corruption(tmp_path,fault):
    path,meta=fixture(tmp_path);s=meta['segments'][0]
    if fault=='hash':s['sha256']='0'*64
    if fault=='manifest':s['array_manifest']['D_0']['sha256']='0'*64
    if fault=='geometry':meta['geometry']['face'][1]=.5
    if fault=='interval':s['valid_interval']=[0.,2.]
    if fault=='order':
        s['array_manifest']['orders']['shape']=[2]
    if fault=='fidelity':s['array_fidelity']='FAILED'
    if fault=='other_failure':s['failure']['exception_message']='bad array'
    path.write_text(r.obs.canonical(meta))
    with pytest.raises(ValueError):r.DiagnosticTrajectory(path)


def test_partial_segment_failure_closes_decoded_archive(tmp_path,monkeypatch):
    path,meta=fixture(tmp_path);s=meta['segments'][0];s['array_manifest']['D_0']['sha256']='bad'
    closed=[];real=r.obs.Segment.close
    def close(self):closed.append(True);real(self)
    monkeypatch.setattr(r.obs.Segment,'close',close)
    with pytest.raises(ValueError):r.validated_segment(tmp_path,s,8)
    assert closed==[True]


def test_isolated_observer_factory_preserves_original_namespace(monkeypatch):
    ns={'Trajectory':lambda path:('original',path),'__builtins__':__builtins__}
    exec('def observe(path, value=7):\n    return Trajectory(path), value\n',ns)
    original=ns['observe'];before=dict(ns)
    monkeypatch.setattr(r.obs,'observe_saved',original)
    monkeypatch.setattr(r,'DiagnosticTrajectory',lambda path:('diagnostic',path))
    assert r.observe_diagnostic('x')==(('diagnostic','x'),7)
    assert all(ns[k] is v for k,v in before.items())
    assert original('x')==(('original','x'),7)


def test_independent_decimal_polynomial_and_zero_factors():
    assert r.decimal_polynomial(1.,[2.,3.,4.],[1.,0.],[1.,2.])==Decimal(2)
    # Exact arithmetic: 2 + 3*(-1/2) + 4*(-1/2)*(1/4) = 0.
    assert r.decimal_polynomial(.5,[2.,3.,4.],[1.,0.],[1.,2.])==Decimal(0)


def test_selection_is_preserved_and_never_snaps():
    s=SimpleNamespace(breaks=np.array([0.,1.,2.]),orders=np.array([1,1]),meta={'dense_side':'right'})
    assert r.selected(s,1.)==1
    s.meta['dense_side']='left';assert r.selected(s,1.)==0


@pytest.mark.parametrize('index,want',[(0,('front',None,None)),(1,('liquid',0,None)),(2,('liquid',1,None)),
    (3,('grain_mode',0,0)),(6,('grain_mode',1,1)),(7,('cup',None,None))])
def test_state_index_mapping(index,want):
    item=r.component(index,2,2)
    assert (item['component'],item['cell'],item['mode'])==want


def test_ledger_rejects_duplicate_and_unresolved_starts(tmp_path,monkeypatch):
    monkeypatch.setattr(ctl.obs,'sha',lambda p:'frozen')
    start=dict(event='start',identity='diagnose-0001',stage='diagnose',plan_sha256='frozen')
    path=tmp_path/'ledger.jsonl';path.write_text(r.obs.canonical(start)+'\n')
    assert ctl.ledger(tmp_path)['unresolved']=='diagnose-0001'
    with path.open('a') as f:f.write(r.obs.canonical(deepcopy(start))+'\n')
    with pytest.raises(ValueError,match='concurrent/duplicate'):ctl.ledger(tmp_path)


def test_offline_entry_points_have_no_solver_or_resource_quotas():
    import inspect
    source=inspect.getsource(ctl)
    for forbidden in ('setrlimit(', 'alarm(', 'setitimer(', 'timeout=', 'solve_ivp(', '.simulate('):
        assert forbidden not in source
    assert set(ctl.STAGES)=={'diagnose','analyze'}
    assert all(v is None for v in ctl.practical.UNLIMITED.values())
