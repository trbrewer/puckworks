"""Canonical SCI-MD-004 Angeloni input/target adapter (data only; no scoring)."""
from __future__ import annotations

import csv, hashlib, io, json
from pathlib import Path
from puckworks.data import angeloni_bioactives, angeloni_inventories, angeloni_lipids, angeloni_total_solids

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "puckworks/data/angeloni2023"
SCHEMA = "puckworks.angeloni2023-multispecies/v1"
HOLDOUT = "PROTECTED_EXTERNAL_NO_RETUNING_ENDPOINT_HOLDOUT"
SOURCE_FILES = ("inventories.csv", "bioactives.csv", "total_solids.csv", "lipids.csv", "MANIFEST_UNCERTAINTY.md")
SHOT_TIME = {"O": 20.0, "C": 13.0, "F": 35.0}
SPECIES = {
 "CF": ("caffeine", "PRIMARY_ADJUDICATIVE_SPECIES"), "TR": ("trigonelline", "PRIMARY_ADJUDICATIVE_SPECIES"),
 "CQA": ("total_chlorogenic_acids", "SECONDARY_ADAPTER_READY_NONADJUDICATIVE"),
 "TA": ("tartaric_acid", "SOURCE_PRESERVED_DEFERRED"), "AA": ("acetic_acid", "SOURCE_PRESERVED_DEFERRED"),
 "CA": ("citric_acid", "SOURCE_PRESERVED_DEFERRED"), "3CQA": ("3_caffeoylquinic_acid", "SOURCE_PRESERVED_DEFERRED"),
 "5CQA": ("5_caffeoylquinic_acid", "SOURCE_PRESERVED_DEFERRED"), "FA": ("ferulic_acid", "SOURCE_PRESERVED_DEFERRED"),
 "3_5diCQA": ("3_5_dicaffeoylquinic_acid", "SOURCE_PRESERVED_DEFERRED"), "totCQA": ("total_chlorogenic_acids", "SECONDARY_ADAPTER_READY_NONADJUDICATIVE"),
 "totOA": ("total_organic_acids", "SOURCE_PRESERVED_DEFERRED"), "LP": ("total_lipids", "DEFERRED_MULTIPHASE_CHANNEL")}

def _sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def _flag(v) -> bool: return str(v).lower() == "true"
def _csv(rows):
    if not rows: return b""
    s=io.StringIO(newline=""); w=csv.DictWriter(s, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
    return s.getvalue().encode()
def _json(v): return (json.dumps(v, indent=2, sort_keys=True, ensure_ascii=False)+"\n").encode()

def build_inputs():
    bio=angeloni_bioactives(); seen={};
    for r in bio:
        sid=str(r["sample"]); seen[sid]={
          "sample_id":sid,"variety":r["variety"],"temperature_C_source":r["T_degC"],"temperature_K":r["T_degC"]+273.15,
          "pressure_bar_source":r["p_bar"],"pressure_Pa":r["p_bar"]*100000,"pressure_reference":"MACHINE_OVERPRESSURE_GAUGE_REPORTED",
          "grind_code_source":r["granulometry"],"source_on_grid":_flag(r["on_grid"]),"source_shot_duration_s":SHOT_TIME[r["granulometry"]],
          "basket_radius_m":0.02925,"bed_height_m":0.01388,"dose_nominal_kg":0.020,"dose_tolerance_kg":0.0001,
          "beverage_mass_nominal_kg":0.040,"beverage_mass_tolerance_kg":0.002,"tamp_condition":"20 kgF reported",
          "source_dataset_id":"angeloni2023","source_path":"puckworks/data/angeloni2023/bioactives.csv","source_row_lineage":sid}
    return [seen[k] for k in sorted(seen)]

def build_inventories():
    out=[]
    for r in angeloni_inventories():
        code=str(r["species"]); sid=SPECIES[code][0]
        out.append({"variety":r["variety"],"species_id":sid,"source_species_code":code,"source_value":r["C0_s_mg_L"],
         "source_unit":"mg/L (= mg/kg under source 1 kg = 1 L assumption)","source_basis":"roast_and_ground_dry_coffee; source density assumption",
         "canonical_value":r["C0_s_mg_L"]*1e-6,"canonical_unit":"kg/kg","canonical_basis":"dry_coffee_mass_fraction",
         "conversion_rule":"mass_fraction_kg_per_kg_dry = source_mg_per_kg * 1e-6","assumption_identifiers":"ANGELONI_1_KG_EQUALS_1_L",
         "input_role":SPECIES[code][1],"source_path":"puckworks/data/angeloni2023/inventories.csv","source_row_lineage":f'{r["variety"]}:{code}'})
    return sorted(out,key=lambda x:(x["variety"],x["species_id"]))

def build_targets():
    out=[]
    def add(r, obs, code, val, unit, factor, uncertainty=None, ustatus="VARIETY_RANGE_ONLY_NOT_CONDITION_SPECIFIC"):
      out.append({"sample_id":str(r["sample"]),"variety":r["variety"],"observable_id":obs,"species_id":SPECIES.get(code,("",))[0] if code else "",
       "source_species_code":code or "","source_value":val,"source_unit":unit,"source_basis":"directly_reported_beverage_volumetric_concentration",
       "canonical_value":val*factor,"canonical_unit":"kg/m^3","canonical_basis":"beverage_volume",
       "uncertainty_value":uncertainty,"uncertainty_type":"RSD_PERCENT" if uncertainty is not None else "",
       "uncertainty_scope":"CONDITION_LEVEL" if uncertainty is not None else "VARIETY_LEVEL_RANGE_METADATA_ONLY","uncertainty_status":ustatus,
       "source_derived":False,"protected_target":True,"source_path":f'puckworks/data/angeloni2023/{obs}.csv',"source_row_lineage":str(r["sample"])})
    for r in angeloni_bioactives():
      for code in ("TR","TA","AA","CA","3CQA","5CQA","CF","FA","3_5diCQA","totCQA","totOA"): add(r,"bioactives",code,r[code],"g/L",1)
    for r in angeloni_total_solids(): add(r,"total_solids",None,r["TS_g_100mL"],"g/100 mL",10,r["RSD_pct"],"PRINTED_ZERO_RSD_VARIANCE_FLOOR_REQUIRED" if r["RSD_pct"]==0 else "CONDITION_LEVEL_RSD_RETAINED")
    for r in angeloni_lipids(): add(r,"lipids","LP",r["total_lipids_g_100mL"],"g/100 mL",10,r["RSD_pct"],"PRINTED_ZERO_RSD_VARIANCE_FLOOR_REQUIRED" if r["RSD_pct"]==0 else "CONDITION_LEVEL_RSD_RETAINED")
    return sorted(out,key=lambda x:(x["sample_id"],x["observable_id"],x["source_species_code"]))

def build_contract():
    targets=build_targets()
    registry=[{"species_id":v[0],"source_code":k,"role":v[1]} for k,v in sorted(SPECIES.items())]
    registry += [{"species_id":"residual_extractables","source_code":None,"role":"STRUCTURAL_BALANCE_SPECIES","chemical_identity":False},
                 {"species_id":"total_solids","source_code":None,"role":"AGGREGATE_DIAGNOSTIC","chemical_species":False}]
    return {"schema_version":SCHEMA,"authorization":"SCI-MD-004-STAGE-A-OWNER-AUTHORIZATION-MULTISPECIES-DATA-CONTRACT-ANGELONI-PROTECTED-EXTERNAL-ENDPOINT-HOLDOUT-AND-EXACT-ONE-SPECIES-REDUCTION-DESIGN-2026-08-23",
     "change_declaration":"NO_GOVERNING_PHYSICS_CHANGE","holdout_status":HOLDOUT,"preexisting_exposure":True,
     "source_dataset_identifiers":["angeloni2023/inventories","angeloni2023/bioactives","angeloni2023/total_solids","angeloni2023/lipids"],
     "source_files":[{"path":f"puckworks/data/angeloni2023/{n}","sha256":_sha(DATA/n)} for n in SOURCE_FILES],
     "source_rights_provenance":["docs/cards/angeloni2023.md","puckworks/data/MANIFEST.csv","puckworks/data/angeloni2023/MANIFEST_UNCERTAINTY.md"],
     "species_registry":registry,"observable_registry":{"primary":["caffeine_beverage_concentration","trigonelline_beverage_concentration"],"aggregate":["total_solids"],"deferred":["total_lipids"]},
     "units":{"temperature":"K","pressure":"Pa","inventory":"kg/kg dry coffee","targets":"kg/m^3 beverage volume"},"mass_and_volume_bases":{"dose":"dry coffee mass","beverage":"nominal mass; not volume","density_assumption":None},
     "permitted_derivations":["declared SI conversions","aggregate identity verification","future nominal-yield derived mass with explicit density and propagated uncertainty"],
     "forbidden_derivations":["bed-volume inventory without dry bulk density","mass fraction cumulativeTds from total solids","prediction","model-versus-target score","holdout parameterization","fabricated time histories"],
     "uncertainty_semantics":{"analytes":"VARIETY_RANGE_ONLY_NOT_CONDITION_SPECIFIC","total_solids_lipids":"condition-level RSD; reconstructed SD permitted","nominal_replicates":"almost in duplicate (n=2), qualified","variance_floor":"POSITIVE_FLOOR_MUST_BE_FROZEN_BEFORE_WEIGHTING"},
     "classification":{"conditions_and_inventories":"ALLOWED_INPUT_SIDE_DATA","all_66_beverage_rows":"PROTECTED_TARGET_SIDE_DATA"},
     "target_bundle_sha256":hashlib.sha256(_csv(targets)).hexdigest(),"deterministic_sort_order":{"conditions":"sample_id","inventories":"variety,species_id","targets":"sample_id,observable_id,source_species_code"},
     "missing_value_policy":"JSON null/empty CSV cell; never zero imputation","additivity_double_counting_groups":{"CQA":["3CQA","5CQA","3_5diCQA","totCQA"],"OA":["TA","AA","CA","totOA"]},
     "claim_ceiling":"SCI-MD-004 may establish software verification of an indexed passive-species extraction implementation and may test cup-level endpoint predictions conditional on measured roast-and-ground species inventories and the exact predeclared hydraulic/scenario inputs. It cannot, from the Angeloni endpoint data alone, validate internal transient concentration fields, spatial species distributions, thermal physics, lipid transport, reaction chemistry, bean/roast composition prediction, taste, or unrestricted transfer across coffees, grinders, baskets, machines, and recipes. Physical validation of the general Espresso Whole-Pull solver remains NOT_ESTABLISHED unless and until a later owner decision changes that claim ceiling on the basis of appropriate evidence."}

def build_manifest(artifacts=None): return {"schema_version":SCHEMA,"artifacts":artifacts or {},"deterministic":True}
def write_bundle(output_directory):
    d=Path(output_directory); d.mkdir(parents=True,exist_ok=True)
    items={"data_contract.json":_json(build_contract()),"angeloni_conditions.csv":_csv(build_inputs()),"angeloni_inventories_long.csv":_csv(build_inventories()),"angeloni_targets_long.csv":_csv(build_targets())}
    items["STAGE_A_CONTRACT.md"]=("# SCI-MD-004 Stage A contract\n\nData-only canonical adapter. All beverage observations are protected targets. No prediction, scoring, fitting, or solver physics is present. See `data_contract.json` for the normative contract.\n").encode()
    for n,b in items.items():(d/n).write_bytes(b)
    hashes={n:hashlib.sha256(b).hexdigest() for n,b in sorted(items.items())}; (d/"bundle_manifest.json").write_bytes(_json(build_manifest(hashes)))
    return hashes
def verify_bundle(output_directory):
    d=Path(output_directory); m=json.loads((d/"bundle_manifest.json").read_text());
    for n,h in m["artifacts"].items():
      if _sha(d/n)!=h: raise ValueError("BUNDLE_HASH_MISMATCH:"+n)
    return True
