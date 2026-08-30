import csv, json, os, subprocess, sys
from pathlib import Path
import pytest

ROOT=Path(__file__).parents[1]; DATA=ROOT/'puckworks/data/pannusch2024'
sys.path.insert(0,str(ROOT/'tools'))
from pannusch2024_reconstruct import load_sources, write_csv  # noqa: E402
def read(name):
    with (DATA/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))

def test_counts_keys_and_spills():
    reg=read('experiment_register.csv'); fit=[r for r in reg if r['campaign_id']=='FIT_2021_12']; pred=[r for r in reg if r['campaign_id']=='PREDICTION_2022_03']
    assert len(fit)==len({r['shot_id'] for r in fit})==45
    assert len(pred)==len({r['shot_id'] for r in pred})==24
    assert len(read('experimental_kinetics.csv'))==90
    assert len(read('fit_fraction_replicates.csv'))==45*6*5
    assert len(read('prediction_fraction_replicates.csv'))==24*6*5
    exc=read('exclusion_register.csv')
    assert {(r['source_experiment_id'],r['shot_id'],r['fraction_id']) for r in exc}=={('3','FIT-E03-R1','2'),('11','FIT-E11-R3','2'),('14','FIT-E14-R3','2')}
    invalid=[r for r in read('fit_fraction_replicates.csv') if r['validity']=='INVALID']
    assert len(invalid)==12 and all(not r['concentration_value'] and r['exclusion_reason']=='INVALID_SPILL' for r in invalid)

def test_grind_mapping_is_explicit_and_fails_closed(monkeypatch):
    from puckworks.models.pannusch2024 import solver as ps
    fit=[r for r in read('experiment_grind_assignments.csv') if r['campaign_id']=='FIT_2021_12']
    assert len(fit)==15 and {int(r['source_experiment_id']) for r in fit}==set(range(1,16))
    assert {float(r['grind_setting']) for r in fit}=={1.4,1.7,2.0}; assert set(ps._source_grinds())==set(range(1,16))
    monkeypatch.setattr('puckworks.data.pannusch_experiment_grinds',lambda:fit[:-1])
    with pytest.raises(ValueError,match='requires one explicit'):ps._source_grinds()

def test_exp46_estimand_and_totals():
    x=json.loads((DATA/'reference_extraction_exp46_summary.json').read_text())
    assert x['recovered_liquid_g']==pytest.approx(819.70)
    assert x['totals_mg']==pytest.approx({'caffeine':251.598442,'trigonelline':168.643265,'5CQA':144.520754,'CQA_sum':280.257266,'TDS':5241.913218},rel=2e-8)
    assert x['tds_yield_percent']==pytest.approx(26.2096,rel=2e-6)
    assert x['estimand']=='N1_OPERATIONAL_REFERENCE_ESTIMATE' and x['tail_class']=='EMPIRICALLY_RESOLVED_MEASURED_TAIL'
    for f in ('total_roasted_content_established','analytical_exhaustion_established','production_M0_established','cs0_replacement_established'):assert x[f] is False
    assert len(read('reference_extraction_exp46_fractions.csv'))==12

def test_eligibility_fails_closed():
    x=json.loads((DATA/'pannusch_transfer_eligibility.json').read_text())
    assert len(x['conditions'])==8 and not x['target_blind'] and not x['independent_external_validation'] and not x['hydraulic_validation']
    assert not x['absolute_mass']['inventory_mapping_established']
    assert {r['condition_id'] for r in x['conditions'] if r['ewp']=='BLOCKED_TEMPERATURE_PHYSICS'}=={'PRED-C03','PRED-C04'}

def test_payloads_have_no_absolute_paths_or_volatile_timestamps():
    for p in DATA.iterdir():
        if p.suffix in {'.csv','.json'}:
            text=p.read_text(); assert '/home/tim' not in text; assert 'created_at' not in text

def test_source_contract_fails_on_missing_hash_and_ambiguity(tmp_path):
    import hashlib
    source=tmp_path/'source'; source.mkdir(); (source/'a').write_bytes(b'a'); (source/'b').write_bytes(b'a')
    fields=['source_id','source_relpath','sha256']; manifest=tmp_path/'manifest.csv'
    good=hashlib.sha256(b'a').hexdigest()
    write_csv(manifest,fields,[{'source_id':'A','source_relpath':'missing','sha256':good}])
    with pytest.raises(FileNotFoundError):load_sources(source,manifest,True)
    write_csv(manifest,fields,[{'source_id':'A','source_relpath':'a','sha256':'0'*64}])
    with pytest.raises(ValueError,match='hash mismatch'):load_sources(source,manifest,True)
    write_csv(manifest,fields,[{'source_id':'A','source_relpath':'a','sha256':good},{'source_id':'B','source_relpath':'b','sha256':good}])
    with pytest.raises(ValueError,match='ambiguous duplicate'):load_sources(source,manifest,True)

@pytest.mark.external_data
def test_external_reconstruction_matches_and_is_deterministic(tmp_path):
    source=os.environ.get('PUCKWORKS_PANNUSCH_SOURCE_ROOT')
    if not source:pytest.skip('external Pannusch source root not configured')
    command=[sys.executable,str(ROOT/'tools/pannusch2024_reconstruct.py'),'--source-root',source,'--source-manifest',str(DATA/'source_inputs.csv'),'--strict']
    outs=[tmp_path/'one',tmp_path/'two']
    for out in outs:subprocess.run(command+['--output-root',str(out)],check=True)
    for p in outs[0].iterdir():assert p.read_bytes()==(outs[1]/p.name).read_bytes()==(DATA/p.name).read_bytes()
