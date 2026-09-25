"""Frozen-output audit/reporting checks using synthetic curves only."""
import numpy as np
import pytest
from puckworks.analysis import moroney_transfer as model, moroney_transfer_run as run
from puckworks.analysis import moroney_transfer_report as report


@pytest.fixture
def bundle(tmp_path,monkeypatch):
    doc=tmp_path/'doc';doc.mkdir();out=tmp_path/'results';out.mkdir()
    monkeypatch.setattr(run,'DOC',doc);monkeypatch.setattr(run,'ROOT',tmp_path)
    marker=tmp_path/'source';marker.write_text('synthetic')
    run.write_json(doc/'freeze.json',{'files':{'source':run.digest(marker)},'runtime':run.runtime_identity(),'source_ready':True})
    family={'id':'f','basis':'dose','profile':'uniform','amplitude':.5}
    run.write_json(doc/'protocol.json',{'families':[family],'source_perturbations':[{'id':'central','mass_factor':1.}],'resolutions':[2,3,4]})
    run.write_json(doc/'target_support.json',{'exit_mass':[5,25,100],'pot_mass':[5,25,100]})
    pars=[.1833,.0447,.77];m=np.array([0.,5,10,25,30,100]);preds={};observed={};scores={};numer={}
    for name,c in [('deep',model.DEEP),('shallow',model.SHALLOW)]:
        p=model.solve(c,m,n=4,alpha=pars[0],beta=pars[1],split=pars[2],amplitude=.5)
        key='central/f/0/'+name;preds[key]={k:p[k].tolist() for k in ['mass_g','exit_mg_g','delivered_g']}
        mass=np.array([10.,30,100]) if name=='deep' else np.array([5.,25,100])
        observed[name]={'exit_mass':mass,'pot_mass':mass,'exit_obs':np.interp(mass,m,p['exit_mg_g']),'pot_obs':np.interp(mass,m,p['pot_mg_g'])}
        scores[key]={'outlet_rmse_mg_g':0.,'cumulative_max_ey_pp':0.}
        numer[key]={'balance_relative':p['balance_relative'],'nfev':p['nfev'],'solver_calls':1,'refinement':[{'outlet_rmse_mg_g':0.,'delivery_max_ey_pp':0.}]*3}
    cost={'solver_calls':0,'nfev':0,'failures':0}
    fits={'central/f':{'selected':0,'admitted':[0],'records':[{'start':0,'parameters':pars,'success':True,'boundary':[0,0,0]}],'cost':cost},
          'central/empirical':{'selected':None,'admitted':[],'records':[{'start':0,'success':False}],'cost':cost}}
    for name,value in [('predictions.json',preds),('calibration.json',fits),('numerics.json',numer)]:run.write_json(out/name,value)
    run.write_json(out/'prediction_freeze.json',{'protocol_freeze_sha256':run.digest(doc/'freeze.json'),'files':{name:run.digest(out/name) for name in ['predictions.json','calibration.json','numerics.json']},'elapsed_s':0.})
    run.write_json(out/'scores.json',{'prediction_freeze_sha256':run.digest(out/'prediction_freeze.json'),'scores':scores})
    run.write_json(out/'decisions.json',{'overall':'SYNTHETIC_TEST_ONLY'})
    monkeypatch.setattr(run,'observations',lambda name:observed[name]);monkeypatch.setattr(run,'rows',lambda name:[])
    return out,observed


def test_inventory_replay_preserves_reservoir_budget_and_never_reads_target(bundle,monkeypatch):
    out,observed=bundle
    def deep_only(name):
        assert name=='deep', 'target concentration read during inventory audit'
        return observed[name]
    monkeypatch.setattr(run,'observations',deep_only)
    report.inventory(out);audit=report.read(out,'inventory_audit.json')
    assert audit['solver_calls']==2
    for r in audit['records'].values():
        total=sum(np.asarray(r[k]) for k in ['retained_mobile_g','retained_internal_g','remaining_surface_g','remaining_kernel_solid_g','delivered_g','losses_g'])
        assert np.allclose(total,r['initial_inventory_g'],rtol=1e-8)
        assert r['trajectory_replay_max_difference']==0
    with pytest.raises(ValueError,match='already exists'):report.inventory(out)
    (out/'predictions.json').write_text('{}')
    with pytest.raises(ValueError,match='changed frozen'):report.checked(out)


def test_report_and_three_figures_use_frozen_outputs(bundle):
    pytest.importorskip('matplotlib')
    out,_=bundle
    before=run.digest(out/'predictions.json')
    report.summarize(out);report.figures(out)
    assert run.digest(out/'predictions.json')==before
    assert report.read(out,'summary.json')['overall']=='SYNTHETIC_TEST_ONLY'
    assert all((out/f'figure{i}.png').stat().st_size>1000 for i in [1,2,3])
    assert len(report.read(out,'viz_specs.json'))==3
