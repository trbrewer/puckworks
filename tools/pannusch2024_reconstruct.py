#!/usr/bin/env python3
"""Deterministic, hash-bound reconstruction of the external Pannusch source package."""
from __future__ import annotations
import argparse,csv,hashlib,json,tempfile
from pathlib import Path

DATA_FILES=(
 "experiment_register.csv","fit_fraction_replicates.csv","experimental_kinetics.csv",
 "exclusion_register.csv","experiment_grind_assignments.csv","psd_summary.csv",
 "prediction_fraction_replicates.csv","prediction_conditions.csv",
 "reference_extraction_exp46_fractions.csv","reference_extraction_exp46_summary.json",
 "analytical_method_register.csv","telemetry_inventory.csv",
 "experimental_kinetics_correction_ledger.json")
LEGACY_KINETICS_SHA256="735c8aa86e06ff1c46f13335924d91636e77da161962a1b7e9394421dbdd28ca"
SAMP=(0,1,2,4,6,9); FIDS=(1,2,3,5,7,10)
SPILLS={(3,1,2),(11,3,2),(14,3,2)}
ANALYTES=("caffeine","trigonelline","5CQA","CQA_sum","TDS")
COL={"caffeine":0,"trigonelline":1,"5CQA":2,"CQA_sum":3}

def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def rows(p):
 with p.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def write_csv(p,fields,data):
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(data)
def write_json(p,obj):p.write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+'\n',encoding='utf-8')
def fmt(x,n=8):
 s=f'{float(x):.{n}f}'
 return s.rstrip('0').rstrip('.') if '.' in s else s
def load_sources(root,manifest,strict):
 out={}; seen={}
 for r in rows(manifest):
  p=root/r['source_relpath'];
  if not p.is_file():raise FileNotFoundError(f"required source missing: {r['source_id']}")
  got=digest(p)
  if got!=r['sha256']:raise ValueError(f"source hash mismatch: {r['source_id']}: {got}")
  if got in seen and strict:raise ValueError(f"ambiguous duplicate source: {r['source_id']} and {seen[got]}")
  seen[got]=r['source_id'];out[r['source_id']]=p
 return out
def mat(path):
 from scipy.io import loadmat
 return loadmat(path,squeeze_me=True,struct_as_record=False)
def workbook(path):
 try:import openpyxl
 except ImportError as e:raise RuntimeError('install the reconstruct extra: pip install -e ".[reconstruct]"') from e
 return openpyxl.load_workbook(path,data_only=True,read_only=True)
def doe_conditions(path,expected,prediction=False):
 wb=workbook(path);ws=wb['ExpSheet'];out=[]
 for r in range(2,ws.max_row+1):
  exp=ws.cell(r,2).value
  if isinstance(exp,(int,float)) and int(exp)==exp and 1<=int(exp)<=expected:
   out.append(dict(exp=int(exp),flow0=float(ws.cell(r,4).value),flow1=float(ws.cell(r,5).value) if prediction else float(ws.cell(r,4).value),grind=float(wb['DoE'].cell(45+int(exp),6).value) if prediction else float(ws.cell(r,5).value),
    temp0=float(ws.cell(r,6).value),temp1=float(ws.cell(r,7).value) if prediction else float(ws.cell(r,6).value),
    dose=float(ws.cell(r,10).value),date=str(ws.cell(r,11).value or 'UNKNOWN')[:10]))
 return sorted({x['exp']:x for x in out}.values(),key=lambda x:x['exp'])
def shot_dates(path,expected):
 ws=workbook(path)['ExpSheet'];out={};current=None
 for r in range(2,ws.max_row+1):
  if isinstance(ws.cell(r,2).value,(int,float)):current=int(ws.cell(r,2).value)
  shot=ws.cell(r,3).value;date=ws.cell(r,11).value
  if current and current<=expected and isinstance(shot,(int,float)) and int(shot) in (1,2,3):
   out[(current,int(shot))]=str(date or 'UNKNOWN')[:10]
 return out
def grind_map(fit,pred):
 pars={1.4:(.19,332),1.7:(.23,330),2.0:(.22,301)};out=[]
 for camp,cs in [('FIT_2021_12',fit),('PREDICTION_2022_03',pred)]:
  for c in cs:
   psi,ds=pars[c['grind']];prediction=camp.startswith('PREDICTION')
   location=f"DoE!F{45+c['exp']}" if prediction else 'ExpSheet grind column'
   out.append({'campaign_id':camp,'source_experiment_id':c['exp'],'grind_setting':fmt(c['grind'],1),'psi':fmt(psi,2),'d_s2_um':ds,'source_statement':f"{location}={fmt(c['grind'],1)}",'source_id':'P24-DOE-PRED' if prediction else 'P24-DOE-FIT','source_location':location,'mapping_kind':'DIRECTLY_STATED','mapping_confidence':'HIGH','unresolved_fields':''})
 return out
def reconstruct(source_root,out,manifest,strict=True):
 import numpy as np
 src=load_sources(source_root,manifest,strict);out.mkdir(parents=True,exist_ok=True)
 fitc=doe_conditions(src['P24-DOE-FIT'],15);predc=doe_conditions(src['P24-DOE-PRED'],8,True)
 fitdates=shot_dates(src['P24-DOE-FIT'],15);preddates=shot_dates(src['P24-DOE-PRED'],8)
 if len(fitc)!=15 or len(predc)!=8:raise ValueError('condition count mismatch')
 fit=np.atleast_1d(mat(src['P24-MAT-FIT'])['ExperimentalData']);pred=np.atleast_1d(mat(src['P24-MAT-PRED'])['ExperimentalData'])
 expreg=[];fitlong=[];legacy=[];valid=[]
 for c in fitc:
  runs=np.atleast_1d(fit[c['exp']-1].run)
  if len(runs)!=3:raise ValueError('fit replicate count mismatch')
  for j,run in enumerate(runs,1):
   c['date']=fitdates[(c['exp'],j)]
   sid=f"FIT-E{c['exp']:02d}-R{j}"
   expreg.append({'campaign_id':'FIT_2021_12','source_experiment_id':c['exp'],'condition_id':f"FIT-C{c['exp']:02d}",'shot_id':sid,'physical_replicate_id':j,'source_role':'SOURCE_FIT_DATA','collection_date':c['date'],'coffee_product':'SOURCE_COMMERCIAL_PRODUCT','coffee_lot_id':'UNKNOWN','roast_batch_id':'UNKNOWN','grinder':'E65S','burr_set':'UNKNOWN','grind_setting':fmt(c['grind'],1),'machine':'DE1','basket':'UNKNOWN','dose_g':fmt(c['dose'],1),'nominal_temperature_program_id':f"CONST-{fmt(c['temp0'],0)}C",'nominal_flow_program_id':f"CONST-{fmt(c['flow0'],1)}ML_S",'measurement_validity':'VALID_WITH_DECLARED_FRACTION_EXCLUSIONS' if any(x[0]==c['exp'] and x[1]==j for x in SPILLS) else 'VALID','exclusion_reason':'SEE_EXCLUSION_REGISTER' if any(x[0]==c['exp'] and x[1]==j for x in SPILLS) else '','source_id':'P24-MAT-FIT;P24-DOE-FIT'})
   for k,(mi,fid) in enumerate(zip(SAMP,FIDS)):
    lo=0 if mi==0 else float(run.tE[mi-1]);hi=float(run.tE[mi]);mass=float(run.mE[mi])
    for a in ANALYTES:
     conc=float(run.TdS[k]) if a=='TDS' else float(run.cAlcaloids[k,COL[a]])
     bad=(c['exp'],j,fid) in SPILLS and a!='TDS'
     fitlong.append({'campaign_id':'FIT_2021_12','condition_id':f"FIT-C{c['exp']:02d}",'source_experiment_id':c['exp'],'shot_id':sid,'physical_replicate_id':j,'fraction_id':fid,'fraction_start_s':fmt(lo,8),'fraction_end_s':fmt(hi,8),'fraction_liquid_g_or_ml':fmt(mass,8),'fraction_basis':'MEASURED_MASS_G','analyte':a,'concentration_value':'' if bad else fmt(conc,8),'concentration_unit':'percent' if a=='TDS' else 'mg/g','analyte_mass_mg':'' if bad else fmt(conc/100*mass*1000 if a=='TDS' else conc*mass,8),'mass_derivation':'DERIVED_FROM_CONCENTRATION_AND_MEASURED_LIQUID','validity':'INVALID' if bad else 'VALID','exclusion_reason':'INVALID_SPILL' if bad else '','source_id':'P24-MAT-FIT','source_object_or_cell':f"ExperimentalData({c['exp']}).run({j}) fraction {fid}",'measurement_kind':'SOURCE_DERIVED_ANALYTICAL'})
  rr=[]
  for k,fid in enumerate(FIDS):
   allruns=np.atleast_1d(fit[c['exp']-1].run);d={'exp':c['exp'],'Temp_C':fmt(np.mean([r.Temp for r in allruns]),2),'flow_mL_s':fmt(np.mean([r.flow for r in allruns]),3),'grind_setting':fmt(c['grind'],1),'fraction':fid,'t_lower_s':fmt(np.mean([0 if SAMP[k]==0 else r.tE[SAMP[k]-1] for r in allruns]),3),'t_upper_s':fmt(np.mean([r.tE[SAMP[k]] for r in allruns]),3)}
   for a,key in [('caffeine','c_caffeine_mg_g'),('trigonelline','c_trigonelline_mg_g'),('5CQA','c_5CQA_mg_g')]:
    vals=[float(r.cAlcaloids[k,COL[a]]) for r in allruns];d[key]=fmt(np.mean(vals),4);good=[v for n,v in enumerate(vals,1) if (c['exp'],n,fid) not in SPILLS];d[key+'_valid']=fmt(np.mean(good),4)
   vals=[float(r.TdS[k]) for r in allruns];d['TDS_pct']=fmt(np.mean(vals),4);d['TDS_pct_valid']=d['TDS_pct'];rr.append(d)
  legacy.extend(rr);valid.extend(rr)
 fields=['exp','Temp_C','flow_mL_s','grind_setting','fraction','t_lower_s','t_upper_s','c_caffeine_mg_g','c_trigonelline_mg_g','c_5CQA_mg_g','TDS_pct']
 accepted=[{k:(r[k+'_valid'] if k.endswith('_mg_g') and k+'_valid' in r else r[k]) for k in fields} for r in valid]
 # prediction physical shots and long observations
 predlong=[]
 for c in predc:
  runs=np.atleast_1d(pred[c['exp']-1].run)
  for j,run in enumerate(runs,1):
   sid=f"PRED-E{c['exp']:02d}-R{j}";expreg.append({'campaign_id':'PREDICTION_2022_03','source_experiment_id':c['exp'],'condition_id':f"PRED-C{c['exp']:02d}",'shot_id':sid,'physical_replicate_id':j,'source_role':'SOURCE_DESIGNATED_PREDICTION','collection_date':'2022-03','coffee_product':'SOURCE_COMMERCIAL_PRODUCT','coffee_lot_id':'UNKNOWN','roast_batch_id':'UNRESOLVED_POTENTIALLY_DIFFERENT','grinder':'E65S','burr_set':'UNKNOWN','grind_setting':fmt(c['grind'],1),'machine':'DE1','basket':'UNKNOWN','dose_g':fmt(c['dose'],1),'nominal_temperature_program_id':f"{fmt(c['temp0'],0)}-{fmt(c['temp1'],0)}C",'nominal_flow_program_id':f"SOURCE_PROGRAM_E{c['exp']:02d}",'measurement_validity':'VALID','exclusion_reason':'','source_id':'P24-MAT-PRED;P24-DOE-PRED'})
   for k,(mi,fid) in enumerate(zip(SAMP,FIDS)):
    lo=0 if mi==0 else float(run.tE[mi-1]);hi=float(run.tE[mi]);mass=float(run.mE[mi])
    for a in ANALYTES:
     conc=float(run.TdS[k]) if a=='TDS' else float(run.cAlcaloids[k,COL[a]])
     predlong.append({'campaign_id':'PREDICTION_2022_03','condition_id':f"PRED-C{c['exp']:02d}",'shot_id':sid,'physical_replicate_id':j,'fraction_id':fid,'fraction_start_s':fmt(lo,8),'fraction_end_s':fmt(hi,8),'fraction_liquid_g_or_ml':fmt(mass,8),'analyte':a,'measured_concentration':fmt(conc,8),'concentration_unit':'percent' if a=='TDS' else 'mg/g','derived_analyte_mass_mg':fmt(conc/100*mass*1000 if a=='TDS' else conc*mass,8),'derivation':'CONCENTRATION_X_MEASURED_FRACTION_MASS','temperature_start_C':fmt(c['temp0'],1),'temperature_end_C':fmt(c['temp1'],1),'flow_start_mL_s':fmt(c['flow0'],1),'flow_end_mL_s':fmt(c['flow1'],1),'input_status':'PROGRAMMED','validity':'VALID','source_role':'SOURCE_DESIGNATED_PREDICTION','target_exposure_class':'TARGET_EXPOSED;SOURCE_INTERNAL','source_id':'P24-MAT-PRED'})
 # experiment 46
 h=workbook(src['P24-HPLC-FIT'])['46'];ref=[];cum={a:0. for a in ANALYTES[:-1]};cm=0.
 for i,r in enumerate(range(10,22),1):
  sr=r+5;mass=float(h.cell(sr,2).value);cm+=mass
  vals={'trigonelline':float(h.cell(r,20).value),'caffeine':float(h.cell(r,22).value),'5CQA':float(h.cell(r,25).value),'CQA_sum':float(h.cell(r,33).value)}
  for a,v in vals.items():cum[a]+=v
  ref.append({'fraction_id':i,'recovered_liquid_g':fmt(mass,2),'cumulative_liquid_g':fmt(cm,2),**{a+'_mass_mg':fmt(vals[a],9) for a in vals},**{'cumulative_'+a+'_mg':fmt(cum[a],9) for a in vals},'mass_class':'DERIVED_FROM_CONCENTRATION_AND_MEASURED_LIQUID','source_id':'P24-HPLC-FIT','source_location':f"46 rows {r}/{sr}"})
 x46=fit[15].run;tot=[float(x) for x in x46.m0_Alcaloids];tds=float(x46.m0_TdS)
 summary={'estimand':'N1_OPERATIONAL_REFERENCE_ESTIMATE','direct_recovered_mass':True,'physical_reference_replicates':1,'operational_reference_estimate':True,'dose_g':20.0,'fractions':12,'recovered_liquid_g':float(sum(x46.mE)),'totals_mg':{'caffeine':tot[0],'trigonelline':tot[1],'5CQA':tot[2],'CQA_sum':tot[3],'TDS':tds},'tds_yield_percent':tds/200.,'tail_boundary_g':212.68,'measured_tail_percent':{a:(cum[a]-float(ref[2]['cumulative_'+a+'_mg']))/cum[a]*100 for a in cum},'tail_class':'EMPIRICALLY_RESOLVED_MEASURED_TAIL','total_roasted_content_established':False,'analytical_exhaustion_established':False,'production_M0_established':False,'cs0_replacement_established':False,'same_lot_status':'UNRESOLVED','same_roast_batch_status':'UNRESOLVED','spent_puck_assay_present':False,'retained_liquid_correction_present':False,'recovery_study_present':False,'moisture_basis_present':False,'lod_loq_present':False}
 # write
 write_csv(out/'experiment_register.csv',list(expreg[0]),expreg)
 write_csv(out/'fit_fraction_replicates.csv',list(fitlong[0]),fitlong)
 write_csv(out/'experimental_kinetics.csv',fields,accepted)
 exc=[{'campaign_id':'FIT_2021_12','source_experiment_id':e,'shot_id':f"FIT-E{e:02d}-R{j}",'fraction_id':f,'analyte_or_measurement':'ALL_HPLC_ANALYTES','source_status':'SET_TO_ZERO_AS_INVALID_BY_SOURCE_CODE','normalized_status':'INVALID_SPILL','exclusion_reason':'INVALID_SPILL','source_evidence':"P24-M-PREP-FIT explicit assignment; P24-DOE-FIT SampleWeights spill","effect_on_aggregate":'excluded from valid-only mean','notes':'not a nondetect or valid zero'} for e,j,f in sorted(SPILLS)]
 write_csv(out/'exclusion_register.csv',list(exc[0]),exc)
 gm=grind_map(fitc,predc);write_csv(out/'experiment_grind_assignments.csv',list(gm[0]),gm)
 write_csv(out/'psd_summary.csv',['grind_id','source_sheet_sample','reported_or_derived','descriptor','value','unit','source_id','instrument_method','limitations'],[{'grind_id':g,'source_sheet_sample':'workbook sheet metadata','reported_or_derived':'FITTED_TABLE2_NOT_RECALCULATED','descriptor':d,'value':v,'unit':u,'source_id':'P24-PSD','instrument_method':'Sympatec HELOS H2607 / RODOS dry dispersion','limitations':'raw PSD retained externally; fitted psi/d_s2 equivalence not asserted'} for g,p,d2 in [(1.4,.19,332),(1.7,.23,330),(2.0,.22,301)] for d,v,u in [('psi',p,'1'),('d_s2',d2,'um')]])
 write_csv(out/'prediction_fraction_replicates.csv',list(predlong[0]),predlong)
 pcs=[]
 for c in predc:
  tr=c['temp0']!=c['temp1'];fr=c['flow0']!=c['flow1'];pcs.append({'condition_id':f"PRED-C{c['exp']:02d}",'classification':'TEMPERATURE_RAMP' if tr else ('FLOW_RAMP' if fr else 'CONSTANT'),'temperature_start_C':fmt(c['temp0'],1),'temperature_end_C':fmt(c['temp1'],1),'temperature_schedule':'LINEAR_PROGRAMMED' if tr else 'CONSTANT_PROGRAMMED','flow_start_mL_s':fmt(c['flow0'],1),'flow_end_mL_s':fmt(c['flow1'],1),'flow_schedule':'LINEAR_PROGRAMMED' if fr else 'CONSTANT_PROGRAMMED','schedule_coordinate':'SOURCE_PROGRAM_TIME','input_status':'PROGRAMMED_NOT_PUCK_FACE_MEASURED','shot_count':3,'fraction_count':6,'source_role':'SOURCE_DESIGNATED_PREDICTION','target_exposed':True,'ewp_current_physics_eligibility':'BLOCKED_TEMPERATURE_PHYSICS' if tr else 'CONDITIONALLY_ELIGIBLE'})
 write_csv(out/'prediction_conditions.csv',list(pcs[0]),pcs);write_csv(out/'reference_extraction_exp46_fractions.csv',list(ref[0]),ref);write_json(out/'reference_extraction_exp46_summary.json',summary)
 write_csv(out/'analytical_method_register.csv',['method_id','source_id','analytes','calibration_status','blank_status','lod_status','loq_status','recovery_status','analytical_repeats','unresolved'],[{'method_id':'HPLC-ALK-CQA','source_id':'P24-HPLC-FIT;P24-HPLC-PRED','analytes':'caffeine;trigonelline;5CQA;CQA_sum','calibration_status':'SOURCE_CALIBRATION_EQUATIONS_PRESENT','blank_status':'NOT_ESTABLISHED','lod_status':'NOT_ESTABLISHED','loq_status':'NOT_ESTABLISHED','recovery_status':'NOT_ESTABLISHED','analytical_repeats':'workbook-level analytical processing','unresolved':'recovery/censoring uncertainty'},{'method_id':'RI-TDS','source_id':'P24-RI-FIT;P24-RI-PRED','analytes':'TDS','calibration_status':'SOURCE_CALIBRATION_PRESENT','blank_status':'NOT_ESTABLISHED','lod_status':'NOT_ESTABLISHED','loq_status':'NOT_ESTABLISHED','recovery_status':'NOT_ESTABLISHED','analytical_repeats':'source workbook','unresolved':'recovery/censoring uncertainty'}])
 write_csv(out/'telemetry_inventory.csv',['telemetry_id','source_id','shot_join','channels','sample_interval','pressure_node','temperature_meaning','flow_meaning','beverage_mass_availability','input_class','time_origin_status','eligibility_status'],[{'telemetry_id':'PRED-MASS-FITS','source_id':'P24-MASS-PRED','shot_join':'24 source-order joins','channels':'quadratic beverage mass fit coefficients','sample_interval':'DERIVED','pressure_node':'NOT_APPLICABLE','temperature_meaning':'NOT_APPLICABLE','flow_meaning':'BEVERAGE_MASS_DERIVED_OUTFLOW_TIMING','beverage_mass_availability':'FITTED_24','input_class':'DERIVED_NOT_INLET_FLOW','time_origin_status':'SOURCE_RECONSTRUCTED','eligibility_status':'CONTEXT_ONLY'}])
 changes=[]
 for o,n in zip(legacy,accepted):
  for k in ['c_caffeine_mg_g','c_trigonelline_mg_g','c_5CQA_mg_g']:
   if o[k]!=n[k]:changes.append({'key':f"exp={o['exp']};fraction={o['fraction']};field={k}",'old':o[k],'corrected':n[k]})
 ledger={'base_file_sha256':LEGACY_KINETICS_SHA256,'candidate_file_sha256':digest(out/'experimental_kinetics.csv'),'affected_keys':changes,'source_evidence':['P24-M-PREP-FIT','P24-DOE-FIT','P24-MAT-FIT'],'correction_reason':'INVALID_SPILL_EXCLUDED_FROM_VALID_ONLY_MEAN','downstream_metrics_affected':True,'no_parameter_refit':True}
 write_json(out/'experimental_kinetics_correction_ledger.json',ledger)
 return {'fit_experiments':15,'fit_physical_shots':45,'prediction_conditions':8,'prediction_physical_shots':24,'spill_records':3,'reference_fractions':12}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-root',type=Path);ap.add_argument('--output-root',type=Path,required=True);ap.add_argument('--source-manifest',type=Path,required=True);ap.add_argument('--check',action='store_true');ap.add_argument('--strict',action='store_true');a=ap.parse_args()
 if a.check:
  if not a.source_root:raise SystemExit('--check requires --source-root')
  with tempfile.TemporaryDirectory() as td:
   t=Path(td);reconstruct(a.source_root,t,a.source_manifest,a.strict)
   bad=[n for n in DATA_FILES if not (a.output_root/n).is_file() or (a.output_root/n).read_bytes()!=(t/n).read_bytes()]
   if bad:raise SystemExit('reconstruction drift: '+', '.join(bad))
   print('check OK: committed outputs are byte-identical')
 else:
  if not a.source_root:raise SystemExit('--source-root is required')
  print(json.dumps(reconstruct(a.source_root,a.output_root,a.source_manifest,a.strict),sort_keys=True))
if __name__=='__main__':main()
