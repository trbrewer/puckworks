import csv, importlib.util, json, pathlib

ROOT=pathlib.Path(__file__).resolve().parents[1]
def test_register_complete_and_deterministic():
    spec=importlib.util.spec_from_file_location("builder",ROOT/"tools/build_available_data_register.py"); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    a=m.build(); b=m.build(); assert a==b
    manifest={r["dataset_id"] for r in csv.DictReader((ROOT/"puckworks/data/MANIFEST.csv").open())}
    represented={x for f in a["families"] for x in f["manifest_dataset_ids"]}; assert manifest==represented
    assert "/home/" not in json.dumps(a)
def test_pannusch_ceiling():
    d=json.loads((ROOT/"puckworks/data/AVAILABLE_DATA_REGISTER.json").read_text()); p=next(f for f in d["families"] if f["family_id"]=="PANNUSCH2024")
    assert p["external_source_manifest_hash"]=="15b9f765d49abe45d6788d7c7891b0695fca185d9c614d122e393993ec06a83c"
    assert p["target_exposure"]=="TARGET_EXPOSED" and p["source_internal_or_external"]=="SOURCE_INTERNAL"
    assert {"absolute closure","hydraulic validation under prescribed flow","temperature-ramp EWP comparison under current physics"} <= set(p["blocked_uses"])
