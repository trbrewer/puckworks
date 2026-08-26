"""One-time, auditable transcription of open SCI-MD-007-R1 source tables.

This is deliberately separate from the analysis generator: it writes curated input
registers only when invoked by a curator, and the production reducer never invokes it.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).parents[1]
DATA = ROOT / "puckworks/data/sci_md_007"


def write(name, rows):
    path = DATA / name
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


sources = [
 dict(source_publication_id="bruno2026",doi="10.1038/s41598-026-43923-9",title="A preliminary model to establish a digital twin for coffee roasting",year=2026,authors="Bruno et al.",laboratory_id="lab_unicam_rich",institution="Universita di Camerino / RICH",source_dataset_id="bruno_table2",data_lineage_id="bruno2026_table2",analytical_method_family="HPLC-MS/MS",sample_preparation_method="aqueous extraction of roasted powder",calibration_method="external calibration",internal_standard="not reported",recovery="reported by method",lod="reported by method",loq="reported by method",replicate_design="mean SD n=3",source_locator="Table 2",license_access_status="CC_BY_4_0",source_card_path="docs/cards/bruno2026.md",source_screening_state="ATLAS_INCLUDED_NUMERIC_ROWS",exclusion_reason=""),
 dict(source_publication_id="dias2015",doi="10.3390/beverages1030127",title="Discrimination between Arabica and Robusta Coffees Using Hydrosoluble Compounds",year=2015,authors="Dias and Benassi",laboratory_id="lab_uel_benassi",institution="Universidade Estadual de Londrina",source_dataset_id="dias_table2",data_lineage_id="dias2015_table2",analytical_method_family="HPLC-DAD",sample_preparation_method="aqueous extraction",calibration_method="external calibration",internal_standard="not reported",recovery="89-104 percent",lod="reported",loq="reported",replicate_design="duplicate means and SD",source_locator="Table 2",license_access_status="CC_BY_4_0",source_card_path="docs/cards/dias2015.md",source_screening_state="ATLAS_INCLUDED_NUMERIC_ROWS",exclusion_reason=""),
 dict(source_publication_id="viencz2023",doi="10.1016/j.jfca.2023.105140",title="Caffeine trigonelline chlorogenic acids melanoidins and diterpenes contents of Coffea canephora coffees produced in the Amazon",year=2023,authors="Viencz et al.",laboratory_id="lab_uel_benassi",institution="Universidade Estadual de Londrina / Embrapa Rondonia",source_dataset_id="viencz_tables1_2",data_lineage_id="viencz2023_tables1_2",analytical_method_family="HPLC-DAD",sample_preparation_method="aqueous extraction",calibration_method="external six point calibration",internal_standard="not reported",recovery="reported",lod="reported",loq="reported",replicate_design="duplicate extraction and analysis n=4 SD",source_locator="Tables 1-2 and Tables S2-S3",license_access_status="PUBLIC_REPOSITORY_NORMALIZED_FACTS",source_card_path="docs/cards/viencz2023.md",source_screening_state="ATLAS_INCLUDED_NUMERIC_ROWS",exclusion_reason=""),
 dict(source_publication_id="acre2024",doi="10.21577/0103-5053.20240031",title="Composition of Coffea canephora Varieties from the Western Amazon",year=2024,authors="Acre et al.",laboratory_id="lab_uel_benassi",institution="Universidade Estadual de Londrina / Embrapa Rondonia",source_dataset_id="acre_tables1_2",data_lineage_id="acre2024_tables1_2",analytical_method_family="HPLC-DAD",sample_preparation_method="aqueous extraction",calibration_method="external six point calibration triplicate",internal_standard="not reported",recovery="reported",lod="reported",loq="reported",replicate_design="duplicate extraction and analysis n=4 SD",source_locator="Tables 1-2 and Table S1",license_access_status="OPEN_ACCESS_NORMALIZED_FACTS",source_card_path="docs/cards/acre2024.md",source_screening_state="ATLAS_INCLUDED_NUMERIC_ROWS",exclusion_reason=""),
 dict(source_publication_id="pannusch2024",doi="10.1016/j.jfoodeng.2023.111887",title="Model-based kinetic espresso brewing control chart for representative taste components",year=2024,authors="Pannusch et al.",laboratory_id="lab_tum_briesen",institution="Technical University of Munich",source_dataset_id="pannusch_table2",data_lineage_id="schmieder_pannusch_lineage",analytical_method_family="model fit to HPLC extraction kinetics",sample_preparation_method="espresso fractions",calibration_method="fitted model",internal_standard="not reported",recovery="not applicable",lod="not reported",loq="not reported",replicate_design="fitted source parameters",source_locator="Table 2",license_access_status="REGISTERED_EXISTING_SOURCE",source_card_path="docs/cards/pannusch2024.md",source_screening_state="ATLAS_INCLUDED_NUMERIC_ROWS",exclusion_reason="primary-ineligible fitted solid-phase concentration"),
 dict(source_publication_id="schmieder2023",doi="10.3390/foods12152871",title="Influence of Flow Rate Particle Size and Temperature on Espresso Extraction Kinetics",year=2023,authors="Schmieder et al.",laboratory_id="lab_tum_briesen",institution="Technical University of Munich",source_dataset_id="schmieder_cup_masses",data_lineage_id="schmieder_pannusch_lineage",analytical_method_family="HPLC plus fitted kinetic integration",sample_preparation_method="espresso fraction extraction",calibration_method="source method",internal_standard="not reported",recovery="not reported",lod="not reported",loq="not reported",replicate_design="multiple extraction programs from one coffee",source_locator="supplementary cup_masses.csv",license_access_status="REGISTERED_EXISTING_SOURCE",source_card_path="docs/cards/schmieder2023.md",source_screening_state="ATLAS_INCLUDED_NUMERIC_ROWS",exclusion_reason="primary-ineligible asymptotic extraction estimate"),
]

materials=[]; observations=[]
def material(mid, source, lineage, lab, species, fraction, cultivar, roast, category, metric_type="", metric="", moisture="", notes=""):
    materials.append(dict(base_coffee_material_id=mid,roast_batch_id=roast,source_publication_id=source,data_lineage_id=lineage,laboratory_id=lab,species_common=species,species_scientific=("Coffea arabica" if species=="Arabica" else "Coffea canephora" if species=="Robusta" else "Blend"),species_fraction=fraction,variety_cultivar=cultivar,origin_country="Brazil" if source != "bruno2026" else "",origin_region="",farm_estate_lot="",processing_method="",harvest_year="",material_form="ground",roast_category_published=category,roast_category_harmonized=category if category in {"light","medium","dark"} else "",roast_metric_type=metric_type,roast_metric_value=metric,roast_metric_units=("percent mass loss" if metric_type=="roast_mass_loss" else ""),colour_metric="",roast_temperature_history="",roast_duration="",roast_mass_loss=metric if metric_type=="roast_mass_loss" else "",moisture_value=moisture,moisture_basis="wet_basis" if moisture else "",dose_sample_mass_basis="dry roasted coffee" if source in {"dias2015","viencz2023","acre2024"} else "",descriptor_provenance=notes,descriptor_missingness_flags=""))

def obs(oid, mid, roast, source, lineage, lab, analyte, value, uncertainty, unit="g/100 g", basis="dry roasted coffee", semantics="TOTAL_ROASTED_CONTENT", provenance="DIRECT_ROASTED_MATERIAL_ASSAY", n=4, locator=""):
    factor={"g/100 g":10,"mg/100 g":.01,"mg/mL solid phase":1,"mg":1}[unit]
    supported=unit in {"g/100 g","mg/100 g"} and basis=="dry roasted coffee"
    observations.append(dict(observation_id=oid,base_coffee_material_id=mid,roast_batch_id=roast,analytical_batch_id=source,replicate_id="",source_publication_id=source,data_lineage_id=lineage,laboratory_id=lab,analyte=analyte,value_as_published=value,unit_as_published=unit,mass_basis_as_published=basis,uncertainty_value_as_published=uncertainty,uncertainty_type="SD" if uncertainty != "" else "unknown",number_of_analytical_replicates=n,target_semantics=semantics,measurement_provenance=provenance,canonical_value=(float(value)*factor if supported else ""),canonical_unit="mg/g dry roasted coffee" if supported else "",canonical_uncertainty=(float(uncertainty)*factor if supported and uncertainty != "" else ""),conversion_rule_id=("exact_"+unit.replace(" ","_") if supported else "NO_CONVERSION"),conversion_inputs="exact factor; source explicit dry basis" if supported else "",conversion_status="SUPPORTED_EXACT" if supported else "NOT_APPLICABLE_INELIGIBLE_SEMANTICS",rights_usable="true",duplicate_status="UNIQUE",roasted_unextracted="true" if provenance=="DIRECT_ROASTED_MATERIAL_ASSAY" else "false",analytical_method="HPLC-DAD" if source in {"dias2015","viencz2023","acre2024"} else "model/source method",source_locator=locator,primary_prediction_label_eligible="",exclusion_reason="",validation_group_id=""))

# Dias: two base coffees blended at known fractions and three roast realizations.
dias = {"trigonelline":[[.928,.489,.297],[.894,.462,.262],[.863,.458,.239],[.865,.456,.206],[.683,.380,.119]],"caffeine":[[1.33,1.35,1.36],[1.53,1.51,1.52],[1.62,1.55,1.57],[1.82,1.79,1.78],[2.25,2.10,2.20]]}
dias_sd={"trigonelline":[[.005,.007,.010],[.007,.009,.001],[.004,.022,.005],[.032,.005,.002],[.011,.015,.003]],"caffeine":[[.02,.05,.06],[.05,.00,.06],[.06,.07,.01],[.11,.04,.06],[.13,.14,.05]]}
for bi, robusta in enumerate((0,20,30,50,100)):
 for ri,(roast,loss) in enumerate(zip(("light","medium","dark"),(13,17,20))):
  mid=f"dias_r{robusta:03d}"; rb=f"{mid}_{roast}"
  if not any(m["base_coffee_material_id"]==mid and m["roast_batch_id"]==rb for m in materials): material(mid,"dias2015","dias2015_table2","lab_uel_benassi","Arabica" if robusta==0 else "Robusta" if robusta==100 else "Blend",robusta/100,"IAPAR59/Apoata",rb,roast,"roast_mass_loss",loss,"2 base coffees; blends share both parents")
  for a in ("caffeine","trigonelline"): obs(f"dias-{a[:3]}-{robusta}-{roast}",mid,rb,"dias2015","dias2015_table2","lab_uel_benassi",a,dias[a][bi][ri],dias_sd[a][bi][ri],n=2,locator="Table 2")

acre_caf=[[2227,1728,1929,2641,1981,1833,1995,2455,1952,2117],[2646,3301,2432,2534,2743,2092,2695,2472,2331,1879],[3618,2807,2977,2600,1918,3156,2267,3364,1956,1427]]
acre_caf_sd=[[2,103,141,151,46,46,141,44,15,46],[1,185,124,253,71,37,19,29,10,12],[23,48,115,18,153,100,46,20,14,41]]
acre_tri=[[294,540,422,620,496,398,445,474,316,316],[636,329,360,260,263,632,314,253,338,227],[554,570,559,620,285,709,705,646,683,804]]
acre_tri_sd=[[23,5,46,15,2,6,18,24,13,4],[23,21,50,29,15,26,15,6,10,7],[16,12,22,29,52,13,20,11,4,85]]
for gi,prefix in enumerate("CRH"):
 for i in range(10):
  code=f"{prefix}{i+1}"; mid=f"acre_{code.lower()}"; rb=mid+"_medium_light"
  material(mid,"acre2024","acre2024_tables1_2","lab_uel_benassi","Robusta",1,code,rb,"medium-light","roast_mass_loss",13.7,.024,"Table S1 genotype; C/R/H are C. canephora varieties")
  obs(f"acre-caf-{code}",mid,rb,"acre2024","acre2024_tables1_2","lab_uel_benassi","caffeine",acre_caf[gi][i],acre_caf_sd[gi][i],"mg/100 g",n=4,locator="Table 1")
  obs(f"acre-tri-{code}",mid,rb,"acre2024","acre2024_tables1_2","lab_uel_benassi","trigonelline",acre_tri[gi][i],acre_tri_sd[gi][i],"mg/100 g",n=4,locator="Table 2")

viencz_raw='''1,2.79,.01,.97,.04;2,2.34,.01,1.06,.01;3,2.69,.02,1.06,.01;4,2.35,.00,.97,.01;5,2.12,.03,.99,.00;6,2.15,.02,.89,.01;7,2.26,.06,1.11,.03;8,1.63,.03,.93,.01;9,2.18,.01,.84,.00;10,2.47,.02,.92,.00;11,2.32,.03,.97,.00;12,2.11,.04,.98,.02;13,2.03,.04,.94,.01;14,2.37,.00,1.05,.01;15,2.19,.01,.97,.01;16,2.02,.03,.85,.03;17,2.53,.01,.96,.00;18,2.65,.02,.96,.03;19,1.98,.10,1.02,.02;20,2.74,.02,.96,.01;21,2.61,.01,.92,.01;22,1.72,.01,.89,.02;23,2.68,.04,.98,.02;24,2.34,.04,.78,.03;25,2.48,.00,.93,.01;26,2.30,.02,1.02,.00;27,2.71,.02,1.00,.03;28,2.21,.01,1.01,.01;29,2.18,.04,.86,.01;30,2.65,.05,.93,.02;31,2.65,.04,.94,.02;32,1.80,.02,.84,.00;33,2.84,.08,1.05,.16;34,1.97,.01,1.02,.04;35,2.84,.07,.96,.03;36,2.64,.02,.94,.01;37,2.58,.01,.74,.01;38,1.94,.02,.78,.02;39,2.67,.14,.85,.04;40,2.69,.06,.89,.05;41,2.32,.06,.99,.02;42,2.26,.04,1.01,.04;43,2.44,.04,.86,.03;44,3.33,.02,1.00,.02;45,1.68,.02,.99,.02;46,3.05,.08,1.03,.05;47,2.73,.06,1.15,.02;48,2.33,.03,.86,.01;49,2.20,.02,1.03,.02;50,2.40,.00,.84,.00;51,2.44,.09,.80,.05;52,1.92,.07,.79,.05;53,2.61,.08,1.01,.04;54,2.34,.02,.88,.01;55,2.60,.04,.84,.00;56,2.35,.05,.78,.03;57,2.46,.00,.79,.00'''
viencz=[x.split(',') for x in viencz_raw.split(';')]
viencz += [[x[0],str(x[1]),str(x[2]),str(x[3]),str(x[4])] for x in [
 ("BRS1216",2.86,.02,.65,.01),("BRS2299",2.29,.05,.74,.01),("BRS2314",3.09,.05,.71,.00),("BRS2336",3.57,.01,.81,.02),("BRS2357",2.52,.00,.60,.01),("BRS3137",2.46,.05,.82,.04),("BRS3193",2.72,.05,.85,.00),("BRS3210",2.88,.04,.84,.00),("BRS3213",2.68,.04,.72,.00),("BRS3220",2.55,.01,.85,.02)]]
for code,c,cs,t,ts in viencz:
 code=str(code); label=code if code.startswith("BRS") else "R"+code; mid="viencz_"+label.lower(); rb=mid+"_medium"
 material(mid,"viencz2023","viencz2023_tables1_2","lab_uel_benassi","Robusta",1,label,rb,"medium","Agtron",60,.039,"2020 Embrapa Ouro Preto do Oeste; Agtron 65-55")
 obs(f"viencz-caf-{label}",mid,rb,"viencz2023","viencz2023_tables1_2","lab_uel_benassi","caffeine",c,cs,n=4,locator="Table 1" if label.startswith("R") else "Table 2")
 obs(f"viencz-tri-{label}",mid,rb,"viencz2023","viencz2023_tables1_2","lab_uel_benassi","trigonelline",t,ts,n=4,locator="Table 1" if label.startswith("R") else "Table 2")

# Existing non-primary evidence, represented without forbidden phase conversion.
material("pannusch_source_coffee","pannusch2024","schmieder_pannusch_lineage","lab_tum_briesen","Blend","","source coffee","pannusch_source_roast","","","","","model fitted")
for a,v in (("caffeine",10.80),("trigonelline",4.19)): obs(f"pannusch-{a}","pannusch_source_coffee","pannusch_source_roast","pannusch2024","schmieder_pannusch_lineage","lab_tum_briesen",a,v,"","mg/mL solid phase","solid-phase volume", "SOLID_PHASE_CONCENTRATION","MODEL_INFERRED_OR_FITTED",n=0,locator="Table 2")
material("schmieder_source_coffee","schmieder2023","schmieder_pannusch_lineage","lab_tum_briesen","Blend","","source coffee","schmieder_source_roast","","","","","same coffee across extraction programs")
for a in ("caffeine","trigonelline"): obs(f"schmieder-{a}","schmieder_source_coffee","schmieder_source_roast","schmieder2023","schmieder_pannusch_lineage","lab_tum_briesen",a,0,"","mg","asymptotic extracted mass", "ASYMPTOTIC_EXTRACTED_MASS","ASYMPTOTIC_EXTRACTION_ESTIMATE",n=0,locator="registered cup-mass lineage; representative atlas classification")

write("sources.csv",sources); write("materials.csv",materials); write("observations.csv",observations)
write("lineage_links.csv",[
 {"link_id":"l1","left_type":"publication","left_id":"viencz2023","right_type":"laboratory","right_id":"lab_uel_benassi","reason":"shared UEL Benassi analytical laboratory"},
 {"link_id":"l2","left_type":"publication","left_id":"acre2024","right_type":"laboratory","right_id":"lab_uel_benassi","reason":"shared UEL Benassi analytical laboratory; separate data lineage"},
 {"link_id":"l3","left_type":"publication","left_id":"pannusch2024","right_type":"publication","right_id":"schmieder2023","reason":"Pannusch fit reuses Schmieder experimental lineage"},])
print(len(sources),len(materials),len(observations))
