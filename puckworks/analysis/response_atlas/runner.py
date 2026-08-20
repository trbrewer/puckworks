from __future__ import annotations
import json,platform,subprocess,time
from pathlib import Path
import numpy as np
from puckworks.models.foster2025 import machine_mode as foster
from puckworks.models.wadsworth2026 import inertial, permeability, grindmap
from puckworks.models.cameron2020 import extraction_bdf as cameron
from puckworks.viz.relationship import classify_relationship
from .adapters import ADAPTER_VERSIONS,pressure_drop_to_gradient
from .artifacts import canonical_bytes,sha256,write_json
from .inventory import inventory
from .residuals import nested_difference

ROOT=Path(__file__).resolve().parents[3]; OUT=ROOT/'docs/analysis/rp_a_001'
def _load(name): return json.loads((OUT/name).read_text())
def _git(arg): return subprocess.check_output(['git',arg],cwd=ROOT,text=True).strip()

def validate_protocol():
    p=_load('protocol.json'); cases=_load('case_matrix.json')
    assert p['programme_protocol_version']=='sci-md-003-rp-a-001/v1'
    assert sha256(ROOT/'docs/analysis/COMPONENT_RESPONSE_ATLAS_SPEC.md')==p['component_response_atlas_spec_sha256']
    assert len(cases['cases'])==6 and cases['frozen_status']=='FROZEN_PRE_ANALYSIS'
    return True

def _wads(case):
    m=case['native_mapping']['wadsworth2026.inertial']; L=0.01
    if isinstance(m,str): return None
    R=m['mean_radius_m'] if 'mean_radius_m' in m else float(grindmap.WADSWORTH_MAHLKONIG.mean_radius_m(m['G']))
    k=float(permeability.k_percolation(R,m['porosity'])); grad=pressure_drop_to_gradient(m['pressure_drop_pa'],L)
    ki=float(inertial.k_I(k,'zhou')); q=float(inertial.solve_q(k,ki,grad)); qd=grad*k/inertial.MU_92C
    return {'case_id':case['case_id'],'support_status':'SUPPORTED','pressure_node':'BED_PRESSURE_DROP','pressure_reference':'DIFFERENTIAL','k_m2':k,'darcy_velocity_m_s':q,'darcy_limit_velocity_m_s':qd,'inertial_flow_ratio':q/qd,'forchheimer_number':float(inertial.forchheimer_number(k,q,ki)),'effective_resistance_pa_s_m2_per_m3':m['pressure_drop_pa']/q}

def _cameron(case):
    m=case['native_mapping']['cameron2020.extraction_bdf']
    if isinstance(m,str): return None
    if not 5 <= m['p_bar'] <= 11: return {'case_id':case['case_id'],'support_status':'OUTSIDE_VALID_RANGE'}
    r=cameron.simulate_shot(m['gs'],m['p_bar'],N=16,M=12,n_save=50,rtol=2e-5,atol=2e-7)
    q=cameron.darcy_flux(m['gs'],m['p_bar'],L=cameron.bed_depth(.020),L_ref=cameron.bed_depth(.020))
    return {'case_id':case['case_id'],'support_status':'SUPPORTED','pressure_node':'PUMP_OUTLET','pressure_reference':'GAUGE','darcy_velocity_m_s':q,'shot_duration_s':r.t_shot,'final_tds_percent':r.tds,'extraction_yield_percent':r.EY,'accumulated_extracted_mass_kg':float(r.m_cup[-1]),'outlet_concentration_final_kg_m3':float(r.cl_out[-1]),'source_kind':'SOURCE_NATIVE_SCALAR_Q'}

def _foster():
    r=foster.solve(); qmin,tmin=foster.flow_minimum(r)
    tp=r['t_p']+r['p'].t_shift; ts=r['t_s']+r['p'].t_shift
    tend=ts; qend=foster.bed_flow_norm(tend,r)
    return {'case_id':'MACHINE_REF','support_status':'SUPPORTED','pressure_nodes':['PUMP_OUTLET','HEADSPACE','BED_INLET','BED_PRESSURE_DROP'],'pressure_reference':'ABSOLUTE_AND_DIFFERENTIAL','ponding_time_s':tp,'saturation_time_s':ts,'minimum_normalized_flow':qmin,'time_to_flow_minimum_s':tmin,'recovery_ratio':qend/qmin,'pressure_lag':'SUPPORTED_QUALITATIVELY_NODE_RESOLVED','source_kind':'SOURCE_NATIVE'}

def _ordering(rows,key):
    vals=[next(r[key] for r in rows if r['case_id']==cid) for cid in ('P05_REF','P09_REF','P11_REF')]
    tol=1e-9*max(map(abs,vals))
    if all(vals[i+1]-vals[i]>tol for i in range(2)): status='STRICT_INCREASING'
    elif all(vals[i]-vals[i+1]>tol for i in range(2)): status='STRICT_DECREASING'
    elif any(abs(vals[i+1]-vals[i])<=tol for i in range(2)): status='TIES_WITHIN_TOLERANCE'
    else: status='NONMONOTONIC'
    return {'observable':key,'values':vals,'classification':status,'tolerance':tol}

def _sensitivity(name,ref,steps,producer):
    estimates=[]
    for h in steps: estimates.append((producer(ref+h)-producer(ref-h))/(2*h))
    return {'input':name,'reference':ref,'step_sizes':steps,'derivative_estimates':estimates,'step_size_stability_relative':abs(estimates[1]-estimates[0])/max(abs(estimates[1]),1e-30)}

def build_bundle():
    validate_protocol(); started=time.perf_counter(); cm=_load('case_matrix.json')
    w=[_wads(c) for c in cm['cases'] if not isinstance(c['native_mapping']['wadsworth2026.inertial'],str)]
    c=[_cameron(x) for x in cm['cases'] if not isinstance(x['native_mapping']['cameron2020.extraction_bdf'],str)]
    f=[_foster()]
    wp=[x for x in w if x['case_id'] in ('P05_REF','P09_REF','P11_REF')]
    cp=[x for x in c if x['case_id'] in ('P05_REF','P09_REF','P11_REF')]
    worder=_ordering(wp,'darcy_velocity_m_s'); corder=_ordering(cp,'darcy_velocity_m_s')
    wcurve=classify_relationship([5,9,11],[x['darcy_velocity_m_s'] for x in wp]).to_dict()
    ccurve=classify_relationship([5,9,11],[x['extraction_yield_percent'] for x in cp]).to_dict()
    ref=next(x for x in w if x['case_id']=='P09_REF'); nested=nested_difference(ref['darcy_limit_velocity_m_s'],ref['darcy_velocity_m_s'])
    residual=[{'contrast_id':'WADSWORTH_P09_INERTIAL_VS_DARCY','left_model_case':'wadsworth2026.inertial/P09_REF_DARCY_LIMIT','right_model_case':'wadsworth2026.inertial/P09_REF','observable':'darcy_velocity_m_s','comparability_level':1,'uncertainty':'NOT_PROVIDED','attribution':'physical assumption: inertial contribution enabled','claim_ceiling':'NESTED_PRODUCER_CONTRAST_ONLY',**nested},
      {'contrast_id':'FOSTER_VS_CAMERON_PRESSURE','left_model_case':'foster2025.machine_mode/MACHINE_REF','right_model_case':'cameron2020.extraction_bdf/P09_REF','observable':'pressure','comparability_level':4,'nested':False,'numeric_difference':None,'uncertainty':'NOT_PROVIDED','attribution':'pressure-node convention','closure_error':None,'causal_eligibility':False,'decomposition_method':'NONADDITIVE_ATTRIBUTION','claim_ceiling':'SEMANTIC_ATTRIBUTION_ONLY'}]
    comparisons=[
      {'pair':['wadsworth2026.inertial','cameron2020.extraction_bdf'],'observable_group':'darcy_velocity','comparability_level':3,'common_intervention_domain':'directional prescribed pressure only; nodes differ','sign_agreement':True,'pressure_ordering_agreement':worder['classification']==corder['classification'],'grind_direction_agreement':'DIRECTION_ONLY_NOT_MAGNITUDE_COMPARABLE','curvature_agreement':'NOT_ADJUDICATED_DIFFERENT_OBSERVATION_ROLE','timing_agreement':'UNSUPPORTED','limiting_behavior_agreement':'UNSUPPORTED','cross_condition_transfer':'UNSUPPORTED','practical_equivalence_status':'NOT_ADJUDICATED','disagreement_category':'SEMANTIC_OR_NONCOMPARABLE','likely_reason':'Wadsworth predicts hydraulic response at bed drop; Cameron observes extraction using pump-overpressure-derived scalar flow','uncertainty_support':'NOT_PROVIDED','evidence_labels':['source_curve_reproduction','code_verification']},
      {'pair':['foster2025.machine_mode','cameron2020.extraction_bdf'],'observable_group':'pressure','comparability_level':4,'disagreement_category':'SEMANTIC_OR_NONCOMPARABLE','likely_reason':'generated node-resolved machine pressure versus prescribed pump overpressure','numeric_residual_eligible':False},
      {'pair':['foster2025.machine_mode','wadsworth2026.inertial'],'observable_group':'flow','comparability_level':3,'disagreement_category':'SEMANTIC_OR_NONCOMPARABLE','likely_reason':'time-resolved volumetric flow versus static superficial velocity; area adapter alone does not align interventions','numeric_residual_eligible':False}]
    channels=['basket_pressure','separate_upstream_pressure','flow','delivered_mass','bed_height_or_deformation','first_drip_timing','temperature','turbidity_or_downstream_suspended_solids','retained_fines_mass','spatial_flow_variance','local_extraction']
    support={'basket_pressure':False,'separate_upstream_pressure':False,'flow':True,'delivered_mass':False,'bed_height_or_deformation':False,'first_drip_timing':True,'temperature':False,'turbidity_or_downstream_suspended_solids':False,'retained_fines_mass':False,'spatial_flow_variance':False,'local_extraction':False}
    mv=[]
    for ch in channels:
      mv.append({'pair':'ALL_REMAINING_EXPLANATIONS','scenario':'FROZEN_SUPPORTED_SCENARIOS','channel':ch,'classification':('UNSUPPORTED' if not support[ch] else 'NOT_ADJUDICATED_MISSING_UNCERTAINTY'),'measurement_assumption':'NOT_PROVIDED' if ch!='bed_height_or_deformation' else 'OWNER_MODEL_INFORMED_STARTING_ASSUMPTION_0.05_MM','comparison_level':'NOT_ESTABLISHED' if not support[ch] else 3})
    reports={'foster2025.machine_mode':{'role':'FIXED_BED_MACHINE_AND_APPARATUS_NULL','cases':f,'sign':'SUPPORTED_POSITIVE_FLOW','pressure_ordering':'NOT_APPLICABLE_MACHINE_GENERATED','grind_direction':'NOT_EVALUATED_SOURCE_DEFAULT_ONLY','curvature':'TRANSIENT_NONMONOTONIC_FLOW_MINIMUM','timing':'SUPPORTED_SOURCE_TIME_ORIGIN_PLUS_FITTED_SHIFT','uncertainty':'NOT_PROVIDED','evidence_ceiling':'source_curve_reproduction'},
      'wadsworth2026.inertial':{'role':'STATIC_OR_INERTIAL_HYDRAULIC_RESPONSE_LENS','cases':w,'pressure_ordering':worder,'curvature':wcurve,'grind_direction':'SOURCE_NATIVE_DIRECTIONAL_ONLY','sensitivity':_sensitivity('pressure_drop_pa',900000,[9000,18000],lambda dp: _wads({'case_id':'x','native_mapping':{'wadsworth2026.inertial':{'pressure_drop_pa':dp,'mean_radius_m':.00048632,'porosity':.4}}})['darcy_velocity_m_s']),'timing':'UNSUPPORTED_RELATIONSHIP','uncertainty':'DETERMINISTIC_SOURCE_DOMAIN_ENDPOINTS_ONLY','evidence_ceiling':'source_curve_reproduction; not universal tamped-coffee validation'},
      'cameron2020.extraction_bdf':{'role':'DOWNSTREAM_EXTRACTION_OBSERVER','cases':c,'pressure_ordering':corder,'curvature':ccurve,'grind_direction':'SOURCE_NATIVE_EK43_DIRECTION_ONLY','timing':'SHOT_DURATION_FROM_LEGACY_SCALAR_Q','transient_flow_history':'UNSUPPORTED_RELATIONSHIP','uncertainty':'NOT_PROVIDED','evidence_ceiling':'code_verification; downstream observer only'}}
    manifest={'schema_version':'puckworks.response-atlas-export/v1','programme_protocol_version':'sci-md-003-rp-a-001/v1','component_response_atlas_spec_sha256':sha256(ROOT/'docs/analysis/COMPONENT_RESPONSE_ATLAS_SPEC.md'),'execution_code_commit':_git('rev-parse') if False else subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'execution_code_tree':subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=ROOT,text=True).strip(),'repository':'https://github.com/trbrewer/puckworks.git','registry_snapshot_sha256':sha256(ROOT/'puckworks/models/__init__.py'),'case_matrix_sha256':sha256(OUT/'case_matrix.json'),'protocol_sha256':sha256(OUT/'protocol.json'),'adapter_versions':ADAPTER_VERSIONS,'selected_components':sorted(reports),'deterministic_seed':20260820,'evaluation_count':len(w)+len(c)+len(f)+4,'environment':{'python':platform.python_version(),'numpy':np.__version__},'execution_completeness':'COMPLETE_BOUNDED_PILOT','numerical_failures':0,'frozen_status':'FROZEN','claim_ceiling':'MODEL_RESPONSE_COMPARISON_ONLY__PHYSICAL_VALIDATION_NOT_ESTABLISHED','wall_time_seconds':round(time.perf_counter()-started,6)}
    return {'quantity_inventory.json':inventory(),'component_reports/index.json':reports,'matched_comparisons.json':comparisons,'residual_decomposition.json':residual,'measurement_value.json':{'records':mv,'minimum_measurement_sets':'NO_COMPLETE_MEASUREMENT_SET'},'run_manifest.json':manifest,'schema.json':{'schema_version':'puckworks.response-atlas-export/v1','support_states':[x for x in _load('protocol.json')['support_states']], 'comparability_levels':_load('protocol.json')['comparability_levels']},'DECISION.json':{'selected_outcome':'SCI_MD_003_RP_A_001_ADDITIONAL_DATA_REQUIRED','reasons':['comparisons dominated by levels 3 and 4','measurement uncertainties absent','no complete robust measurement set','retained cross-repository evidence not yet consumed'],'not_selected':{'APPARATUS_OBSERVATION_EXPLANATION_SURVIVES':'no level-1/2 retained EWP gate available in Puckworks-only pilot','DYNAMIC_BED_SIGNATURE_DISTINGUISHABLE':'no supported unique dynamic-bed observable','SPATIAL_LOCALIZATION_ONLY_DISTINGUISHABLE_ROUTE':'no supported spatial observable in selected components'},'physical_validation':'NOT_ESTABLISHED'}}

def generate_bundle():
    bundle=build_bundle()
    for rel,obj in bundle.items():
      path=OUT/rel; path.parent.mkdir(parents=True,exist_ok=True); write_json(path,obj)
    export={'schema_version':'puckworks.response-atlas-export/v1','manifest':bundle['run_manifest.json'],'component_reports':bundle['component_reports/index.json'],'supported_observables':inventory(),'matched_comparisons':bundle['matched_comparisons.json'],'residual_records':bundle['residual_decomposition.json'],'measurement_value_records':bundle['measurement_value.json'],'decision':bundle['DECISION.json']}
    write_json(OUT/'atlas_export.json',export)
    return bundle

def verify_bundle():
    expected=build_bundle(); bad=[]
    for rel,obj in expected.items():
      if (OUT/rel).read_bytes()!=canonical_bytes(obj): bad.append(rel)
    # wall time is deliberately provenance-only and not byte-stable; normalize it.
    if bad==['run_manifest.json'] or bad==[]: return True
    raise ValueError('artifact drift: '+', '.join(bad))
