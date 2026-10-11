"""Small solver-free controls for the explicit recovered-anchor adapter."""
import copy
from pathlib import Path
import sys

import numpy as np
import pytest

from tools import grudeva2026_remaining_010 as adapter
from tools import run_grudeva2026_full_reference_010 as runner


@pytest.fixture
def recovered(tmp_path):
    root = tmp_path/'campaign'; root.mkdir()
    saved = tmp_path/'recovered'; saved.mkdir()
    support = {'times':[0.,1.,8.], 'z':[0.,1.], 'r':[0.,1.]}
    wet = np.array([[False,False],[True,True],[True,True]])
    obs = {'times':np.array(support['times']), 'z':np.array(support['z']), 'r':np.array(support['r']),
           'wet':wet, 'liquid':np.where(wet,1.,np.nan), 'outlet':np.array([np.nan,1.,1.]),
           'grain_means':np.ones((3,2,2)), 'grain_radial':np.ones((3,2,2,2)),
           'inventories':np.zeros((3,4)), 'integrals':np.zeros((3,2)), 'boundary_flux':np.zeros((3,4))}
    bundles = {'observations.npz':runner.save_bundle(saved/'observations.npz',obs),
               'diagnostics.npz':runner.save_bundle(saved/'diagnostics.npz',{'native_times':obs['times']})}
    original, members = {}, []
    for group, names in [('geometry',[f'g{k}' for k in range(8)]),
                         *[(f'segment-{j}',['t','y','D','shift','denom','order','concentrations',
                             'boundary_accumulators','physical_z_faces','physical_z_centers']) for j in range(2)]]:
        original[group] = {}
        for key in names:
            data = np.array([1,2],dtype='i1' if key=='order' else '<f8')
            path = saved/(group+'-'+key+'.npy'); np.save(path,data)
            identity = runner.array_identity(data); original[group][key] = identity
            members.append({'group':group,'member':key,'source':str(path),'expected':identity,'file_sha256':runner.sha256(path)})
    records = {}
    def put(name, value):
        path = saved/(name+'.json'); runner.write_json(path,value)
        records[name] = {'path':str(path),'sha256':runner.sha256(path)}
    matrix = {'case':{'fixture':'solver-free'},'rows':{'anchor':{'fixture':True}},'support':support}
    put('original_source',original)
    put('checkpoint',{'case':matrix['case'],'settings':matrix['rows']['anchor'],
         'segments':[{'arrays':{k:{'array':original[f'segment-{j}'][k]} for k in ('t','y')}} for j in range(2)]})
    put('solver_end',{'row':'anchor','status':'COMPLETE'})
    put('fidelity',{'status':'PASS_EQUIVALENT_COMMITTED_COEFFICIENT_EVALUATION','required_support_times':3})
    put('admission',{'status':'ADMITTED_FOR_ORIGINAL_OBSERVATIONS_AND_AUDITS_BY_REVIEWED_EQUIVALENT_CHECK',
                    'original_write_succeeded':False,
                    'original_source_commitment_sha256':records['original_source']['sha256'],
                    'fidelity_sha256':records['fidelity']['sha256']})
    put('results',{'bundles':bundles,'gates':{'complete':True,'required_support':True},'native_states':3})
    put('fresh_bundles',{'status':'PASS','results_sha256':records['results']['sha256']})
    checker = runner.ROOT/'tools/verify_grudeva2026_recovery_bytes_010.py'
    put('byte_plan',{'members':members,'records':[records['original_source']],
                    'source_commitment':records['original_source']['path'],
                    'checker_sha256':runner.sha256(checker),'executable_sha256':runner.sha256(sys.executable),
                    'helper_sha256':runner.sha256(runner.ROOT/'tools/diagnose_grudeva2026_transfer_010.py'),'python':sys.version})
    binding = {'authorization':adapter.AUTHORIZATION,'runtime':{'python':sys.executable},
               'recovered_anchor':{'row':'anchor','support_sha256':adapter.metadata_digest(support),'records':records}}
    return root,binding,matrix,obs


def test_adapter_uses_actual_receipts_without_fabricated_manifest(recovered):
    root,binding,matrix,_ = recovered
    stats = runner.validate_saved_row(root/'anchor',matrix,binding)
    assert stats['gates']['archive_evaluation']
    assert stats['recovery']['original_work_counters']=='UNAVAILABLE'
    assert stats['recovery']['admission']['original_write_succeeded'] is False
    assert not (root/'anchor').exists()
    assert len(runner.scientific_identities(root,'anchor',binding)['geometry'])==8
    assert list(root.glob('anchor-byte-read-*/exit.json'))


@pytest.mark.parametrize('fault',['stale','wrong_row','wrong_settings','wrong_content','wrong_support'])
def test_adapter_rejects_invalid_recovery(recovered,fault):
    root,binding,matrix,_ = recovered
    if fault=='stale':
        Path(binding['recovered_anchor']['records']['results']['path']).write_text('{}')
    elif fault=='wrong_row':
        binding['recovered_anchor']['row']='repeat'
    elif fault=='wrong_settings':
        matrix['rows']['anchor']={'fixture':False}
    elif fault=='wrong_content':
        plan=adapter.checked(binding['recovered_anchor']['records']['byte_plan'])
        path=Path(plan['members'][0]['source']); raw=path.read_bytes(); path.write_bytes(raw[:-1]+b'!')
    else:
        matrix['support']=copy.deepcopy(matrix['support']);matrix['support']['times'][1]=.5
    with pytest.raises((ValueError,RuntimeError)):
        runner.validate_saved_row(root/'anchor',matrix,binding)


def test_support_checks_coordinates_masks_and_nonfinite_required_values(tmp_path):
    support={'times':[0.,1.], 'z':[0.,1.], 'r':[0.,1.]}
    data={'times':np.array([0.,1.]),'z':np.array([0.,1.]),'r':np.array([0.,1.]),
          'wet':np.array([[False,False],[True,True]]),'liquid':np.array([[np.nan,np.nan],[1.,1.]]),
          'outlet':np.array([np.nan,1.]), 'grain_means':np.ones((2,2,2)),
          'grain_radial':np.ones((2,2,2,2)),'inventories':np.ones((2,4)),
          'integrals':np.zeros((2,2)),'boundary_flux':np.zeros((2,4))}
    path=tmp_path/'obs.npz';np.savez(path,**data)
    runner.validate_observation_support(path,support)
    for key,change in [('times',np.array([0.,.9])),('wet',~data['wet']),('liquid',np.full((2,2),np.nan))]:
        np.savez(path,**{**data,key:change})
        with pytest.raises(ValueError):runner.validate_observation_support(path,support)


@pytest.mark.parametrize('delta',[0.,1e-12])
def test_repeat_compares_content_not_provenance_and_preserves_failure(recovered,monkeypatch,delta):
    root,binding,matrix,obs=recovered
    repeat=root/'repeat';repeat.mkdir()
    changed={**obs,'outlet':obs['outlet'].copy()};changed['outlet'][1]+=delta
    np.savez_compressed(repeat/'observations.npz',**changed)
    ids=runner.scientific_identities(root,'anchor',binding)
    manifest={'geometry':{'arrays':{k:{'array':v,'file':'different-name'} for k,v in ids['geometry'].items()}},
              'segments':[{'arrays':{k:{'array':v,'file':'own-independent-file'} for k,v in ids[f'segment-{j}'].items()}} for j in range(2)]}
    (repeat/'trajectory').mkdir();runner.write_json(repeat/'trajectory/manifest.json',manifest)
    monkeypatch.setattr(runner,'validate_saved_row',lambda *a,**k:{'gates':{'required_support':True,'archive_evaluation':True}})
    monkeypatch.setattr(runner,'binding_digest',lambda b:'fixture-binding')
    if delta:
        with pytest.raises(ValueError,match='repeatability'):runner.repeat_check(root,matrix,binding)
    else:
        runner.repeat_check(root,matrix,binding)
    result=adapter.read(root/'REPEAT.json')
    assert result['status']==('FAIL' if delta else 'PASS')
    assert result['required_masks_equal'] and result['scientific_array_identity']
    assert result['exact_observations']==(not delta)
    assert isinstance(result['admission_identities'][0],dict)
    assert (result['metrics']['outlet']['max_change']>0)==bool(delta)


def test_remaining_guard_rejects_anchor_before_integrating(tmp_path,monkeypatch):
    monkeypatch.setattr(runner,'load_matrix',lambda *a:{'rows':{'anchor':{},'repeat':{}}})
    monkeypatch.setattr(adapter,'load_binding',lambda *a:{'new_row_order':['repeat']})
    monkeypatch.setattr(runner,'integrate',lambda *a:pytest.fail('Forbidden solver call'))
    with pytest.raises(ValueError,match='cannot execute an anchor'):
        runner.run_row(tmp_path,'anchor',remaining=True)


def test_partial_report_keeps_supported_finite_failures(recovered,monkeypatch):
    root,binding,matrix,obs=recovered
    names=['anchor','repeat','time_coarse','time_medium','axial_coarse','axial_medium']
    matrix.update(task='fixture',row_order=names,axes=['time','axial'])
    for name in names:matrix['rows'][name]={'fixture':True}
    for name in ('repeat','time_coarse','time_medium'):
        (root/name).mkdir()
        runner.write_json(root/name/'results.json',{})
        runner.write_json(root/name/'end.json',{})
        changed={**obs,'outlet':obs['outlet'].copy()}
        if name=='time_coarse':changed['outlet'][1:]+=.3
        if name=='time_medium':changed['outlet'][1:]+=.1
        np.savez_compressed(root/name/'observations.npz',**changed)
    monkeypatch.setattr(runner,'load_matrix',lambda *a:matrix)
    monkeypatch.setattr(adapter,'load_binding',lambda *a:binding)
    monkeypatch.setattr(runner,'binding_digest',lambda b:'fixture-binding')
    validations=[]
    def validate(path,*a,**k):
        validations.append((path.name,k['full_archive']))
        return {'gates':{'complete':True,'required_support':True,'archive_evaluation':True,'conservation':path.name!='time_medium'},
                'native_states':3 if path.name=='anchor' else 4,'recovery':{'fixture':True}}
    monkeypatch.setattr(runner,'validate_saved_row',validate)
    monkeypatch.setattr(runner,'scientific_identities',lambda *a:{'same':'content'})
    runner.report(root,remaining=True)
    report=adapter.read(next((root/'reports').glob('*.json')))
    assert report['disposition']=='FULL_REFERENCE_QUALIFICATION_INCOMPLETE'
    assert report['refinement']['time_medium_fine']['outlet']['max_change']>runner.LIMITS['outlet']
    assert report['failed_row_gates']=={'time_medium':['conservation']}
    assert report['combined_budgets']['outlet']['passed'] is None
    assert report['missing_rows']==['axial_coarse','axial_medium']
    assert report['accounting']['cumulative_full_trajectories']==3
    assert len(list((root/'reports').glob('*.json')))==1
    runner.report(root,remaining=True)
    assert len(list((root/'reports').glob('*.json')))==2
    assert all(not full for _,full in validations)
    names.extend(['combined_coarse','combined_medium'])
    matrix['axes'].append('combined')
    for name in ('axial_coarse','axial_medium','combined_coarse','combined_medium'):
        matrix['rows'][name]={'fixture':True}
        (root/name).mkdir()
        runner.write_json(root/name/'results.json',{})
        runner.write_json(root/name/'end.json',{})
        np.savez_compressed(root/name/'observations.npz',**obs)
    validations.clear()
    runner.report(root,remaining=True)
    assert validations==[(name,True) for name in names]


@pytest.mark.parametrize('side',['live','restored'])
@pytest.mark.parametrize('value',[np.nan,np.inf,-np.inf])
def test_remaining_fidelity_rejects_nonfinite_before_reduction(side,value):
    want,got=np.array([1.,2.]),np.array([1.,2.])
    (want if side=='live' else got)[1]=value
    with pytest.raises(ValueError,match=f'Nonfinite {side}.*count=1, first_flat_index=1'):
        runner.interpolant_error(want,got,.5)
