#!/usr/bin/env python3
"""Build the reviewed 39-family local-corpus authority deterministically."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "puckworks/data/AVAILABLE_DATA_REGISTER.json"
OUTPUT = ROOT / "puckworks/data/LOCAL_CORPUS_FAMILY_INDEX.json"

FAMILIES = (
    "angeloni2023", "bruno2026", "cameron2020", "egidi2024", "ellero2019",
    "fasano2000_partI", "foster2025_2", "g10_liquor_rheology",
    "g1_glassbead_analog", "g3_pump_characteristic", "gagne2021", "gloess2013",
    "grudeva2025", "hargarten2020", "khamitova2020", "liang2021", "maille2024",
    "mckeonaloe2022", "mo2023", "mo2023_2", "moroney2015", "moroney2016",
    "moroney2019", "pannusch2024", "perticarini2024", "pocketscience2024",
    "ribes2020", "ribes2021", "romancorrochano2015", "romancorrochano2017",
    "schmieder2023", "schulman2011", "smrke2024", "sobolik2002",
    "telisromero2001", "vacaguerra2023a", "visualizer", "wadsworth2026",
    "waszkiewicz2025",
)
REGISTER_ALIASES = {
    "fasano2000_partI": "fasano2000_parti",
    "telisromero2001": "g10_liquor_rheology",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    register = json.loads(REGISTER.read_text(encoding="utf-8"))
    by_id = {item["family_id"].lower(): item for item in register["families"]}
    records = []
    material_ids = {item.lower() for item in FAMILIES}
    for family_id in FAMILIES:
        source = by_id[REGISTER_ALIASES.get(family_id, family_id)]
        aliases = {family_id.lower(): family_id}
        source_aliases = [] if family_id == "telisromero2001" else source["source_cards"]
        for alias in [family_id.upper(), *source_aliases]:
            if alias.lower() in material_ids and alias.lower() != family_id.lower():
                continue
            aliases.setdefault(alias.lower(), alias)
        dataset_ids = source["manifest_dataset_ids"]
        source_registration = f"AVAILABLE_DATA_REGISTER:{source['family_id']}"
        strongest_uses = source["eligible_uses"] or source["historical_task_uses"][:1]
        limits = [*source["blocked_uses"], *source["notes"]]
        rights = source["rights"]
        raw_access = source["raw_access_status"]
        if family_id == "telisromero2001":
            dataset_ids = [item for item in dataset_ids if "telisromero2001" in item]
            source_registration = "SOURCE_CARD:docs/cards/telisromero2001.md;PROVENANCE:puckworks/data/telisromero2001/PROVENANCE.md;G10_LINK:AVAILABLE_DATA_REGISTER:G10_LIQUOR_RHEOLOGY"
            strongest_uses = ["RHEOLOGY_OR_VISCOSITY_SOURCE_AUTHORITY_FOR_BOUNDED_FLUID_PROPERTY_SENSITIVITY"]
            limits = ["coffee-specific production viscosity validation", "direct EWP rheology validation", "one industrial soluble-coffee extract batch; source domain must be retained"]
            rights = ["paywalled Wiley article; compact normalized factual transcriptions only; no article PDF or raw rheograms redistributed"]
            raw_access = "RIGHTS_BOUNDED_COMPACT_TRANSCRIPTION_NO_RAW_ARTICLE"
        records.append({
            "family_id": family_id,
            "aliases": sorted(aliases.values(), key=str.lower),
            "manifest_dataset_ids": dataset_ids,
            "source_registration": source_registration,
            "rights_access_status": rights,
            "raw_access_status": raw_access,
            "model_chain_stages": source["stages"],
            "strongest_current_uses": strongest_uses,
            "limits": limits,
            "last_qualified_task": source["last_qualified_task"],
            "review_trigger": "after the next substantive task or a material rights/source change",
        })
    return {
        "schema_version": 1,
        "review_authority": "ESPRESSO_CORPUS_LEVERAGE_002_R1_INDEPENDENT_REVIEW_PASS_WITH_MATERIAL_QUALIFICATIONS_WASZKIEWICZ_REMAINS_PRIORITY",
        "reviewed_family_census": "INDEPENDENT_LOCAL_FAMILY_CENSUS.csv",
        "available_data_register_sha256": digest(REGISTER),
        "material_family_count": len(records),
        "mapped_or_registered_family_count": len(records),
        "unregistered_material_family_count": 0,
        "families": records,
    }


if __name__ == "__main__":
    OUTPUT.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
