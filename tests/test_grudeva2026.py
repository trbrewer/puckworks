"""Analytical oracles do not import the production modal spectrum/flux helper."""
import dataclasses
import json
import math
import numpy as np
import pytest
from scipy.integrate import solve_ivp

from puckworks.models.grudeva2026 import (Controls, Parameters, Scaling, bed_inventory, bed_to_grain,
                   dimensional_outputs, front_speed, grain_to_bed, simulate, spherical_history)


def analytic_sphere(age, initial, boundary0, slope, diffusivity, q_b):
    # Independently evaluated infinite-series moments: sum 1/n^2=pi^2/6,
    # sum 1/n^4=pi^4/90. Positive-age exponential remainder is negligible.
    n = np.arange(1, 10001, dtype=float)
    lam = diffusivity * np.pi**2 * n**2
    e = np.exp(-lam * age)
    flux = 2*diffusivity/q_b*((initial-boundary0)*e.sum()
            - slope*(1/(6*diffusivity)-(e/lam).sum()))
    mean = boundary0+slope*age + 6/np.pi**2*((initial-boundary0)*(e/n**2).sum()
            - slope*(np.pi**2/(90*diffusivity)-(e/(lam*n**2)).sum()))
    return flux, mean


@pytest.mark.parametrize('C', [0., .2, .6, .95])
def test_front_grouping_and_localized_constant_boundary_arrival(C):
    p = Parameters()
    expected = 1/(p.gamma+p.beta*(p.c_f_init-C)/(1-C))
    wrong = 1/((p.gamma+p.beta)*(p.c_f_init-C)/(1-C))
    assert front_speed(C, p) == pytest.approx(expected, rel=1e-14)
    assert abs(expected-wrong) > .001
    def event(t, y):
        return y[0]-1
    event.terminal = True
    r=solve_ivp(lambda t,y:[front_speed(C,p)], [0,1/expected+1],[0.],events=event,rtol=1e-12,atol=1e-14)
    arrival=float(r.t_events[0][0])
    assert arrival == pytest.approx(1/expected, rel=1e-12)
    assert arrival-1 == pytest.approx(1/expected-1, rel=1e-12)


@pytest.mark.parametrize('slope,initial,boundary', [(0.,1.6,.2),(.3,1.3,.1),(.5,.2,.2)])
def test_spherical_flux_inventory_varying_boundary_and_time_translation(slope,initial,boundary):
    ages=np.array([0,.002,.02,.1,.3,.7])
    t0=4.3
    r=spherical_history(t0+ages,boundary+slope*ages,initial,diffusivity=.7,q_b=.4,modes=128)
    shift=spherical_history(t0+11+ages,boundary+slope*ages,initial,diffusivity=.7,q_b=.4,modes=128)
    for i,age in enumerate(ages[1:],1):
        flux,mean=analytic_sphere(age,initial,boundary,slope,.7,.4)
        assert r['flux'][i] == pytest.approx(flux,abs=2e-4)
        assert r['mean'][i] == pytest.approx(mean,abs=2e-5)
        assert r['flux'][i] == pytest.approx(shift['flux'][i],abs=1e-10)
        assert r['mean'][i]+r['transferred_per_grain_volume'][i] == pytest.approx(initial,abs=2e-15)
    if initial==boundary and slope>0:
        assert r['flux'][-1]<0  # boundary-driven uptake is allowed


def test_equilibrium_and_explicit_short_age_regularization():
    r=spherical_history([9,9.001,10],[1.4]*3,1.4)
    assert r['flux']==[0.]*3
    assert r['mean']==[1.4]*3  # grain concentrations need not be <= 1
    errors=[]
    for modes in [4,8,16,32]:
        v=spherical_history([0,.0005],[0,0],1,modes=modes)
        assert v['flux'][0] is None
        assert v['mean'][0]==1
        exact,_=analytic_sphere(.0005,1,0,0,1,1)
        errors.append(abs(v['flux'][-1]-exact))
    assert errors[-1]<errors[0]/100


def test_phase_volume_round_trip_and_no_double_pore_count():
    c=np.array([0.,.7,1.8,310.])
    assert np.allclose(bed_to_grain(grain_to_bed(c,.16),.16),c,rtol=1e-15,atol=0)
    p=Parameters(varphi_lb=.25,source_id='SYNTHETIC')
    old=bed_inventory(1,p.c_f_init,p.c_b_init,p)
    filled=bed_inventory(1,p.c_f_init,p.c_b_init+.25,p)
    assert filled-old == pytest.approx(p.phi_b*.25)
    # Donor loses precisely the pore-refill solute in a closed transfer.
    closed=bed_inventory(1-p.phi_b*.25/p.phi_l,p.c_f_init,p.c_b_init+.25,p)
    assert closed == pytest.approx(old)


@pytest.fixture(scope='module')
def early():
    return simulate(controls=Controls(cells=64,modes=16),times=[0,.1,.4,.9,1,1.01],profile_z=[0,.01,.2,.5,1])


def test_no_dry_extraction_discharge_and_separate_clocks(early):
    assert early.status=='COMPLETED'
    assert early.events['first_drip']==1
    assert early.events['desaturation_exit'] is None
    assert early.events['saturation_plateau_duration'] is None
    assert early.events['desaturation_at_profile_z'][1]>.01
    assert early.cumulative_discharged_solute[:5]==pytest.approx([0]*5,abs=1e-14)
    assert early.cumulative_discharged_solute[-1]==pytest.approx(.01,abs=1e-12)
    assert early.liquid_profiles[2][-1]==0
    assert early.fines_profiles[2][-1]==1.388
    assert early.boulder_mean_profiles[2][-1]==1.388
    assert early.diagnostics['max_normalized_conservation_residual']<1e-6
    json.loads(early.canonical_json(),parse_constant=lambda s:pytest.fail(s))


@pytest.mark.slow
@pytest.mark.parametrize('pores',[0.,.25])
def test_global_conservation_after_localized_exit_and_pore_refill(pores):
    p=Parameters(varphi_lb=pores,source_id='SYNTHETIC' if pores else Parameters().source_id)
    times=[0,.4,1,2,4,5.5,6.4,6.6,7,8]
    r=simulate(p,Controls(cells=128,modes=16),times=times,profile_z=[0,.5,1])
    assert r.status=='COMPLETED'
    event=r.events['desaturation_exit']
    assert event is not None and event not in times
    assert r.events['desaturation_at_profile_z'][-1]==event
    assert r.events['saturation_plateau_duration']==event-1
    assert r.s_d[-1]==pytest.approx(1,abs=1e-12)
    assert r.outlet_concentration[-1]<r.outlet_concentration[-2]
    assert r.diagnostics['max_normalized_conservation_residual']<1e-6
    assert r.diagnostics['aqueous_min']>=-1e-8
    assert np.max(r.fines_profiles)>=1.388
    again=simulate(p,Controls(cells=128,modes=16),times=times,profile_z=[0,.5,1])
    assert again.canonical_json()==r.canonical_json()
    around=simulate(p,Controls(cells=128,modes=16),
                    times=[0.,event-1e-6,event,event+1e-6,8.],profile_z=[0.,1.])
    # Cup inventory remains continuous when the exit concentration jumps.
    assert 0 <= around.cumulative_discharged_solute[3]-around.cumulative_discharged_solute[1] <= 2.01e-6
    assert around.cumulative_discharged_solute[2] == pytest.approx(event-1,abs=1e-7)


def test_dimensionless_no_invented_geometry_and_mass_semantics(early):
    missing=dimensional_outputs(early,Scaling())
    assert missing['ey_percent'] is None and missing['tds_mass_percent'] is None
    scale=Scaling(bed_depth_m=.01,bed_area_m2=.002,darcy_flux_m_s=.001,c_sat_kg_m3=224,
                  dry_coffee_mass_kg=.02,beverage_density_kg_m3=1000)
    d=dimensional_outputs(early,scale)
    tw=.2*.01/.001
    expected=.002*.001*224*tw*.01
    assert d['solute_mass_kg']==pytest.approx(expected,rel=1e-10)
    assert d['ey_percent']==pytest.approx(100*expected/.02)
    assert d['tds_mass_percent']==pytest.approx(22.4)
    assert d['outlet_volume_flow_m3_s'][0]==0
    zero=dimensional_outputs(early,dataclasses.replace(scale,dry_coffee_mass_kg=0,beverage_density_kg_m3=None,beverage_mass_kg=0))
    assert zero['ey_percent'] is None and zero['tds_mass_percent'] is None


@pytest.mark.parametrize('status,empty', [('NUMERICAL_VERIFICATION_FAILED', False),
                                        ('UNSUPPORTED_REGIME', True), ('NUMERICAL_FAILURE', True)])
def test_dimensional_outputs_reject_unqualified_results(early, status, empty):
    """Synthetic negative-path replacement, not a new solver observation."""
    from puckworks.models.grudeva2026.reduced import Result
    reasons = {'simulation': 'Synthetic failure for output-qualification testing'}
    result = (Result(status, early.parameters, early.controls, unavailable_reasons=reasons) if empty
              else dataclasses.replace(early, status=status, unavailable_reasons=reasons))
    original = result.canonical_json()
    scale = Scaling(bed_depth_m=.01, bed_area_m2=.002, darcy_flux_m_s=.001,
                    c_sat_kg_m3=224, dry_coffee_mass_kg=.02, beverage_mass_kg=.04)
    report = dimensional_outputs(result, scale)
    for key in ('time_s', 'outlet_concentration_kg_m3', 'outlet_volume_flow_m3_s', 'solute_mass_kg',
                'beverage_volume_m3', 'beverage_mass_kg', 'ey_percent', 'tds_mass_percent'):
        assert report[key] is None
        assert status in report['unavailable_reasons'][key]
        assert reasons['simulation'] in report['unavailable_reasons'][key]
    assert report['numerical_status'] == status
    assert report['numerical_unavailable_reasons'] == reasons
    assert report['physical_validation'] == 'NOT_ESTABLISHED'
    assert result.canonical_json() == original  # diagnostic arrays are untouched
    json.dumps(report, allow_nan=False)


def test_dimensional_outputs_completed_censored_and_zero_discharge(early):
    assert early.status == 'COMPLETED' and early.events['desaturation_exit'] is None
    assert early.convergence_status == 'NOT_ASSESSED_SINGLE_RUN'
    scale = Scaling(bed_depth_m=.01, bed_area_m2=.002, darcy_flux_m_s=.001,
                    c_sat_kg_m3=224, dry_coffee_mass_kg=.02, beverage_density_kg_m3=1000)
    report = dimensional_outputs(early, scale)
    assert report['numerical_status'] == 'COMPLETED'
    assert report['numerical_unavailable_reasons'] == early.unavailable_reasons
    assert report['convergence_status'] == early.convergence_status
    assert report['solute_mass_kg'] > 0 and report['ey_percent'] > 0
    # A completed observation window ending before drip has zero discharge.
    predrip = simulate(controls=Controls(cells=8, modes=2), times=[0., .1, .4], profile_z=[0., 1.])
    assert predrip.status == 'COMPLETED'
    zero = dimensional_outputs(predrip, scale)
    assert zero['outlet_concentration_kg_m3'] == [0.] * 3
    assert zero['outlet_volume_flow_m3_s'] == [0.] * 3
    assert zero['solute_mass_kg'] == zero['beverage_mass_kg'] == zero['ey_percent'] == 0
    assert zero['tds_mass_percent'] is None  # zero beverage denominator, not zero TDS
    missing = dimensional_outputs(predrip, Scaling())
    assert missing['solute_mass_kg'] is None and missing['beverage_mass_kg'] is None
    assert missing['ey_percent'] is None and missing['tds_mass_percent'] is None
    measured = dimensional_outputs(predrip, dataclasses.replace(
        scale, beverage_density_kg_m3=None, beverage_mass_kg=.02))
    assert measured['tds_mass_percent'] == 0


def test_invalid_and_unsupported_inputs():
    for kwargs in [{'phi_f':.6},{'d_sb':0},{'varphi_lb':1},{'c_b_init':math.nan}]:
        with pytest.raises(ValueError):Parameters(**kwargs)
    for kwargs in [{'cells':7},{'modes':True},{'rtol':0}]:
        with pytest.raises(ValueError):Controls(**kwargs)
    with pytest.raises(ValueError):front_speed(.5,Parameters(c_f_init=1))
    assert front_speed(1)==0
    r=simulate(Parameters(c_f_init=.9),times=[0,1])
    assert r.status=='UNSUPPORTED_REGIME' and r.unavailable_reasons
    p=Parameters(phi_f=.05,phi_b=.75,phi_l=.2,varphi_lb=.9,c_f_init=1.01)
    assert simulate(p,times=[0,1]).status=='UNSUPPORTED_REGIME'
    with pytest.raises(ValueError):simulate(times=[0,0])
    with pytest.raises(ValueError):simulate(times=[0,1],profile_z=[1,0])
    with pytest.raises(ValueError):grain_to_bed(1,0)


def test_quick_gate_executes_reference_arithmetic_and_coupled_solver():
    from puckworks.validation.gates import gate_grudeva2026_reduced
    gate=gate_grudeva2026_reduced()
    assert gate['passed']
    assert gate['publication_reproduction']=='NOT_EARNED_BY_THIS_QUICK_GATE'
    assert gate['metrics']['coupled_status']=='COMPLETED'


def test_registry_card_rights_route_and_quantity_isolation():
    import puckworks
    from puckworks import rights
    from puckworks.product import lab_catalog, lab_runners, lab_tour, quantity_semantics
    c=next(c for c in puckworks.components() if c.name=='grudeva2026.reduced')
    assert (c.execution_role,c.provenance_class,c.evidence_strength)==('runtime','published_port','code_verification')
    assert lab_catalog.catalog_entry(c).card_path=='docs/cards/grudeva2026_2.md'
    assert lab_runners._evidence(c.name)['card']=='docs/cards/grudeva2026_2.md'
    assert lab_runners.runtime_class(c.name)=='batch-only'
    assert lab_tour.verify_tour_manifest()==[]
    assert c.name in lab_tour.native_reference_ids()
    assert rights.rights_record(c.name).code_rights_state=='INDEPENDENT_REIMPLEMENTATION'
    assert quantity_semantics.shared_scenario_execution_readiness(c.name)['execution_readiness']=='INPUT_ADAPTER_REQUIRED'
    assert quantity_semantics.candidate_comparability(c.name)!='DIRECTLY_OVERLAID'


def test_source_preflight_precedes_scientific_producer(monkeypatch):
    from puckworks import rights
    from puckworks.product.lab_reference_producers import grudeva2026_reference_summary
    import puckworks.models.grudeva2026 as model
    original=rights.may_publish_outputs('grudeva2026.reduced')
    monkeypatch.setattr(rights,'may_publish_outputs',lambda cid:dataclasses.replace(original,allowed=False))
    monkeypatch.setattr(model,'simulate',lambda *a,**k:pytest.fail('producer ran before preflight'))
    with pytest.raises(PermissionError):grudeva2026_reference_summary()


@pytest.mark.slow
def test_native_runner_actual_case_serialization_and_rendered_card_link():
    from puckworks.product import lab, lab_service
    req=lab.ScenarioRequest('pv19_named',lens_selection_policy='none',reference_selection_policy='selected',
                            requested_reference_runner_ids=('grudeva2026.reduced',))
    result=lab_service.execute_lab_request(req,execution_context='PUBLIC_ARTIFACT')
    assert not result.blocked
    report=result.report
    runner=report['executed_reference_results'][0]
    assert runner['status']=='executed'
    assert runner['scientific_result']['status']=='COMPLETED'
    assert runner['reference_qualification']['figure5']['status']=='FIG5_REFERENCE_INCOMPLETE'
    assert not report['executed_lenses']
    markdown=lab.render_markdown(report)
    assert '[Canonical model card](docs/cards/grudeva2026_2.md)' in markdown
    assert 'NOT A COMMON-SCENARIO PREDICTION' in markdown
    assert 'NOT EXPERIMENTAL VALIDATION' in markdown
    assert 'figure3: FAIL' in markdown and 'FIG5_REFERENCE_INCOMPLETE' in markdown
    from puckworks.product.lab_runners import _sci_hash
    assert _sci_hash(runner)==runner['scientific_payload_hash']
    json.dumps(runner,allow_nan=False)


def test_import_has_no_solver_execution_and_does_not_read_old_implementation():
    import ast
    from pathlib import Path
    folder=Path(__file__).parents[1]/'puckworks/models/grudeva2026'
    for source in folder.glob('*.py'):
        tree=ast.parse(source.read_text())
        imports=[node.module for node in ast.walk(tree) if isinstance(node,ast.ImportFrom)]
        assert not any(name and ('grudeva2025' in name or 'espresso-model' in name) for name in imports)
    # Actual import in a fresh process, with numerical execution forbidden.
    import subprocess,sys
    code="import scipy.integrate; scipy.integrate.solve_ivp=lambda *a,**k: (_ for _ in ()).throw(RuntimeError('import execution')); import puckworks.models.grudeva2026"
    subprocess.run([sys.executable,'-c',code],check=True,capture_output=True)
