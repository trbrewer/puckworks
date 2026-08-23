import tempfile
from decimal import Decimal
from pathlib import Path
from puckworks.analysis import angeloni2023_multispecies as adapter
from puckworks.data import angeloni_bioactives

def test_counts_roles_and_separation():
 c=adapter.build_inputs(); i=adapter.build_inventories(); t=adapter.build_targets(); contract=adapter.build_contract()
 assert len(c)==66 and len(i)==16 and len(t)==858
 assert sum(x['variety']=='Arabica' for x in c)==33 and sum(x['variety']=='Robusta' for x in c)==33
 assert sum(x['source_on_grid'] for x in c)==54 and len({x['sample_id'] for x in c})==66
 assert all(x['protected_target'] is True for x in t)
 assert contract['holdout_status']==adapter.HOLDOUT and contract['preexisting_exposure'] is True
 assert {x['species_id'] for x in i if x['species_id'] in ('caffeine','trigonelline')}=={'caffeine','trigonelline'}

def test_units_uncertainty_and_cqa_distinction():
 i=adapter.build_inventories(); t=adapter.build_targets()
 assert all(x['canonical_value']==x['source_value']*1e-6 for x in i)
 assert all(x['canonical_value']==x['source_value'] for x in t if x['source_unit']=='g/L')
 assert all(x['canonical_value']==x['source_value']*10 for x in t if x['source_unit']=='g/100 mL')
 assert all(x['uncertainty_value'] is None for x in t if x['observable_id']=='bioactives')
 assert any(x['uncertainty_status']=='PRINTED_ZERO_RSD_VARIANCE_FLOOR_REQUIRED' for x in t)
 assert any(x['source_species_code']=='totCQA' for x in t) and any(x['source_species_code']=='5CQA' for x in t)

def test_aggregate_identities_source_precision():
 for r in angeloni_bioactives():
  assert abs(Decimal(str(r['totCQA']))-sum(Decimal(str(r[k])) for k in ('3CQA','5CQA','3_5diCQA'))) <= Decimal('0.01')
  assert abs(Decimal(str(r['totOA']))-sum(Decimal(str(r[k])) for k in ('TA','AA','CA'))) <= Decimal('0.01')

def test_deterministic_bundle_and_no_model_products():
 with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
  adapter.write_bundle(a); adapter.write_bundle(b); assert adapter.verify_bundle(a) and adapter.verify_bundle(b)
  for name in ('data_contract.json','angeloni_conditions.csv','angeloni_inventories_long.csv','angeloni_targets_long.csv','bundle_manifest.json','STAGE_A_CONTRACT.md'):
   assert (Path(a)/name).read_bytes()==(Path(b)/name).read_bytes()
  assert not any(x in {p.name for p in Path(a).iterdir()} for x in ('predictions.csv','scores.json','residuals.csv'))
