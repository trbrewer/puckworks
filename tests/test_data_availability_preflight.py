import importlib.util, json, pathlib, pytest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("pre",ROOT/"tools/data_availability_preflight.py"); pre=importlib.util.module_from_spec(spec); spec.loader.exec_module(pre)
def base():
 d={"schema_version":1,"task_id":"G0","scientific_question":"n/a","decision_to_change":"n/a","governance_class":"G0","model_stage":[],"required_observables":[],"required_independence":"n/a","puckworks_authority":{"commit":"x","tree":"x","manifest_sha256":"x","available_data_register_sha256":"x"},"external_data_check":{"performed":True},"datasets_reviewed":[],"prior_tasks_reviewed":[],"existing_data_routes_considered":{},"usable_existing_evidence":[],"remaining_scoped_gaps":[],"data_sufficiency_status":"NOT_APPLICABLE","data_starvation_scope":[],"home_lab_recommendation":{"status":"NOT_APPLICABLE","operational_authorization":False},"next_action":"none","prepared_by":"test","evidence":[]}; return d
def test_g0_and_known_unmounted(monkeypatch,tmp_path):
 monkeypatch.setenv("XDG_CONFIG_HOME",str(tmp_path)); pre.validate(base(),pre.load_register()); p=next(f for f in pre.load_register()["families"] if f["family_id"]=="PANNUSCH2024"); assert pre.external_status(p)=="KNOWN_EXTERNAL_CORPUS_NOT_CURRENTLY_MOUNTED"
@pytest.mark.parametrize("mutation",[lambda d:d.update(data_sufficiency_status="DATA_STARVED"),lambda d:d["datasets_reviewed"].append("missing/id"),lambda d:d["puckworks_authority"].update(commit=""),lambda d:d["home_lab_recommendation"].update(status="REDESIGN_FOR_SPECIFIC_REMAINING_GAP")])
def test_rejects_invalid(mutation):
 d=base(); mutation(d)
 with pytest.raises(ValueError): pre.validate(d,pre.load_register())
