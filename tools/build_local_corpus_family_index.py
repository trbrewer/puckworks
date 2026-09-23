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

# Reviewed source-to-EWP chain roles. These are routing labels, not claims that
# every family independently validates the corresponding stage.
MODEL_CHAIN_STAGES = {
    "angeloni2023": ["chemistry", "extraction"], "bruno2026": ["source_material", "chemistry"],
    "cameron2020": ["extraction", "chemistry"], "egidi2024": ["extraction", "chemistry"],
    "ellero2019": ["extraction", "transport"], "fasano2000_partI": ["extraction", "transport"],
    "foster2025_2": ["wetting", "hydraulics"], "g10_liquor_rheology": ["rheology", "thermal"],
    "g1_glassbead_analog": ["bed_structure", "hydraulics"], "g3_pump_characteristic": ["machine_boundary", "hydraulics"],
    "gagne2021": ["hydraulics", "bed_structure"], "gloess2013": ["sensory", "chemistry"],
    "grudeva2025": ["extraction", "transport"], "hargarten2020": ["source_material", "chemistry"],
    "khamitova2020": ["source_material", "chemistry"], "liang2021": ["extraction", "transport"],
    "maille2024": ["bed_structure", "hydraulics"], "mckeonaloe2022": ["source_material", "sensory"],
    "mo2023": ["bed_structure", "hydraulics"], "mo2023_2": ["bed_structure", "hydraulics", "extraction"],
    "moroney2015": ["extraction", "transport"], "moroney2016": ["extraction", "transport"],
    "moroney2019": ["extraction", "transport"], "pannusch2024": ["extraction", "chemistry"],
    "perticarini2024": ["source_material", "sensory"], "pocketscience2024": ["machine_boundary", "hydraulics"],
    "ribes2020": ["source_material", "chemistry"], "ribes2021": ["source_material", "chemistry"],
    "romancorrochano2015": ["extraction", "chemistry"], "romancorrochano2017": ["extraction", "transport"],
    "schmieder2023": ["extraction", "chemistry"], "schulman2011": ["extraction", "chemistry"],
    "smrke2024": ["source_material", "extraction"], "sobolik2002": ["rheology", "thermal"],
    "telisromero2001": ["rheology", "thermal"], "vacaguerra2023a": ["bed_structure", "hydraulics"],
    "visualizer": ["machine_boundary", "hydraulics"], "wadsworth2026": ["source_material", "bed_structure", "hydraulics"],
    "waszkiewicz2025": ["machine_boundary", "hydraulics", "extraction"],
}


# G0 discovery notes: curated separately from observed snapshot counts.
DISCOVERY_NOTES = {'angeloni2023': ('Fraction and endpoint chemistry; protected comparison lineage. Existing source cards and '
                  'manifest carry analyte, basis and fraction details.',
                  'Source-conditioned extraction comparison only under its existing exposure contract. '
                  'Hash-only this census; no target values or headers opened. Next step is a '
                  'contract-authorized reader, not automatic reuse.'),
 'bruno2026': ('Roasted-composition long table: 40 compound/source rows; wide table: 10 compound rows for '
               'four origins. mean, sd, unit, basis and n_measurements are explicit columns.',
               'Upstream roasted-inventory context and uncertainty priors; long/wide are alternate '
               'representations, not independent batches. No matched brew, pressure or fraction delivery.'),
 'cameron2020': ('Figure 2 PSD: 618 diameter bins, particle_diameter_um and four volume-percent grind '
                 'columns. fig5_grind_deviation has three points.',
                 'The PSD file is a provisional subset without its own MANIFEST row; fig5_grind_deviation does not register it. Verify its source/rights locator before adding a stable subset ID. Grind-specific PSD and coarse/fine behavior reconstruction. Bins are not shots; dial '
                 'cannot be mapped to a different grinder. Local holdings do not imply the entire '
                 'experimental supplement.'),
 'egidi2024': ('table2_egidi2024_tds_ey: 12 condition rows, T [degC], p [bar], tau [s], Granulometry, TDS '
               '[%], TDS sigma, EY [%].',
               'Endpoint condition contrasts; no measured pressure history, fraction chemistry or individual '
               'shot join. Replicate identities UNKNOWN in held table.'),
 'ellero2019': ('Figures 2–4 contain nondimensional t_over_tnu, Reynolds number, applied forcing and '
                'concentration curves across theta, Db and Dr; reference-8 experimental Reynolds points are '
                'separate.',
                'Numerical/source reconstruction and mechanism sensitivity. Most curves are model output; '
                'the experimental digitization is not a new experiment or an espresso chemistry validation '
                'target.'),
 'fasano2000_partI': ('fig8_1: pressure_bar/time_s/discharge_ml_s; fig8_4: direct/inverse segment traces; '
                      'figures 8.6–8.7 carry asymptotic and threshold curves.',
                      'Pressure-response shape and qualitative fines-mechanism context. Separate digitized '
                      'observations from theoretical curves; published apparatus and original clocks are '
                      'needed for transfer.'),
 'foster2025_2': ('fig6_front_position and fig8_headspace each have nine time points in seconds/mm with '
                  'error columns. fig12_14 separates fitted and data front/bed/headspace; fig15 has '
                  'normalized Q and headspace pressure.',
                  'Wetting/bed-change observation operators and source reconstruction. Nine points are not '
                  'nine independent shots; normalized modeled machine response is not a measured '
                  'inlet-pressure schedule.'),
 'g10_liquor_rheology': ('Telis-Romero Table 1: 24 eta_Pas cells indexed by Xw_pct/T_K; Table 2: 27 K_Pasn/n '
                         'cells. Khomyakov: 60 kinematic-viscosity cells indexed by solids fraction and '
                         'temperature; regression/density conflicts are flagged.',
                         'Industrial extract property sensitivity. Water mass percent differs from solids '
                         'fraction; kinematic viscosity needs an authorized density conversion. Quarantined '
                         'regression cannot be silently used. No fresh-espresso rheometry.'),
 'g1_glassbead_analog': ('glassbead_retention_kr: ten quantity/medium/parameter/value/unit/source rows.',
                         'Retention and relative-permeability shape priors only. Glass beads are an analogy; '
                         'no measured coffee wetting curve or absolute coffee permeability.'),
 'g3_pump_characteristic': ('pump_characteristic_ulka: ten pump-model/voltage/quantity/value/unit/source '
                            'rows.',
                            'Machine operating-envelope anchors and sensitivity bounds. Manufacturer '
                            'endpoints and community curve shapes have different authority; no shot-specific '
                            'pump identification.'),
 'gagne2021': ('Eleven .shot machine logs plus eleven resistance-decline summary rows and 14 grinder-arm '
               'summary quantities. Time-series text decoded; Tcl-style shot format needs the existing '
               'dedicated reader.',
               'Machine response and descriptive decline; summary and logs share shots. Grinder arm is '
               'apparatus-specific, pressure is machine telemetry, and inferred resistance is not a '
               'permeability measurement.'),
 'gloess2013': ('de_espresso_endpoint: 17 quantity/value/uncertainty/unit/basis/source-location rows.',
                'Endpoint chemistry and method context. Mixed quantities are not 17 shots; no fraction or '
                'time-series join. Consult source card for direct versus derived values.'),
 'grudeva2025': ('exp13_per_vial_stats: 16 vial rows with solubles_mean_g, solubles_sd_g, n_shots; parameter '
                 'table distinguishes thesis and paper values.',
                 'Source reconstruction and fraction observation support. Means are not new replicate '
                 'records; permission documented in the existing permission card does not create an SPDX '
                 'license or resolve the grain/bed-volume basis bridge.'),
 'hargarten2020': ('Eight roast/temperature/time/swelling-progress rows plus 14 scalar anchors with units '
                   'and uncertainty.',
                   'Wetting/swelling timescale priors and sensitivity. These are source transcriptions; no '
                   'synchronized espresso pressure, flow and wet-bed geometry.'),
 'khamitova2020': ('Tables 5.2–5.5 each have nine pressure/temperature rows and four tamp-force groups, '
                   'analytes in mg/40 mL and mg/mL with RSD. Table 5.6 holds ground-coffee context.',
                   'Endpoint analyte response to conditions. Concentration bases must remain explicit; no '
                   'fraction clock or physical-shot identifiers. Do not join to another campaign by matching '
                   'pressure/temperature.'),
 'liang2021': ('Figures 3–5 carry brew-ratio, TDS, extraction percentage and cupping/retained-liquid '
               'quantities, with nominal versus digitized ratio distinguished.',
               'Immersion extraction ceiling and retained-liquid observation kernels. Not a flowing-puck '
               'hydraulic experiment; digitization error and dependent derived yield remain.'),
 'maille2024': ('Batch extraction curves for caffeine, 3-CQA, citric, malic and quinic acids; time and '
                'normalized C/Cinf. Tables carry sample IDs, sieve/roast, air/liquid PSD, specific surface '
                'and porosity.',
                'Early-release kernels and within-source material comparisons. Join by declared Sample '
                'ID/material only; air and liquid PSD methods differ. Stirred batch has no bed-pressure '
                'history or matched espresso output.'),
 'mckeonaloe2022': ('basket_open_area_geometry: four basket/face rows with open-area percent, hole diameter '
                    'and uncertainty; two basket specimens.',
                    'Basket outlet geometry context and observation-operator development. Faces of a basket '
                    'are not independent specimens; no measured hydraulic pressure loss or coffee '
                    'extraction.'),
 'mo2023': ('PSD table has four capsule types. Four sample tables have six microCT-derived geometries each, '
            'porosity/tortuosity and simulated kD/kF/kF1; some entries are missing or zero.',
            'Geometry-conditioned transport priors and unit auditing. Permeabilities are SPH-derived on '
            'measured geometry, not 24 independent wet espresso measurements; inertial-unit caveat remains.'),
 'mo2023_2': ('fig3a_qdecay contains powder/swelling setting/time/flow curves; figs6_9 has cup mass, '
              'yield/strength and errors; fig6_Ksweep contains model sensitivity curves.',
              'Separate experiment digitizations from simulated swelling and partition sweeps. Source '
              'reconstruction and sensitivity only; fitted inventory cannot become an independently measured '
              'initial condition.'),
 'moroney2015': ('Tables 1–2 mix measured, nominal and fitted parameters; README_manifest identifies '
                 'per-figure evidence. Figures include PSD, batch/bed extraction, pressure and concentration '
                 'profiles.',
                 'Primary lineage for later Moroney models; use source reconstruction and transport-kernel '
                 'checks. Simulations, fitted parameters and source experiments are distinct subsets and '
                 'reused across later papers.'),
 'moroney2016': ('Table 1 parameters include measured, nominal, fitted and derived roles; Figure 6 has 15 '
                 'nondimensional exit-concentration points.',
                 'Asymptotic/source reconstruction, using Moroney 2015 experimental lineage. No independent '
                 'new campaign; nondimensional time requires its declared source scale.'),
 'moroney2019': ('table2: six fine/coarse and single/two-grain parameter rows, including reported and '
                 'corrected mass-transfer coefficients and diffusivity.',
                 'Parameter/unit reconstruction and mechanism priors. These are fitted model '
                 'parameterizations, not six experiments or independent diffusivity measurements.'),
 'pannusch2024': ('Full archive and extracted repository inspected: fit and prediction HPLC/RI/DoE '
                  'workbooks, 70 legacy XLS telemetry files, dry PSD workbook, MATLAB arrays/code and '
                  'generated figures. Prediction DoE includes DoE, pmax, ExpSheet, HPLCWeightsAlcaloids, '
                  'HPLCWeightsLactones, SampleWeights sheets; RI workbook separates TdS, dilution_factor and '
                  'raw_data.',
                  'Use the qualified fit/prediction/reference reconstruction: 45 fit shots +24 prediction '
                  'shots, six fractions each, and one 12-fraction reference preparation (three spill '
                  'exclusions). Programmed flow/temperature are inputs; mass fractions and analytes are '
                  'targets. Opaque MATLAB tables require the existing qualified adapter. No new M0, '
                  'same-lot, clock or pressure-boundary equivalence.'),
 'perticarini2024': ('bed_height_time: eight coffee/granulometry/height/time rows; ey_tds_cibao: 18 '
                     'condition rows with T, p, tau, TDS uncertainty and EY; six granulometry parameter '
                     'rows.',
                     'Geometry and endpoint condition context. Approximate grain-family parameters and '
                     'prescribed conditions are not matched instantaneous hydraulic measurements.'),
 'pocketscience2024': ('Three source-style CSV exports include LRR dose/water/beverage quantities and '
                       'multirow basket sheets. Derived edge-EY means have 12 condition rows; LRR summary '
                       'has two grinder rows.',
                       'Retained-liquid and radial extraction context. Multirow exports need a header '
                       'adapter; source measurements and condition means must not be counted twice. '
                       'Community methods lack a qualified puck-pressure boundary.'),
 'ribes2020': ('radial_ey: nine condition/tamper/filter/zone rows with inner/outer radii, zone EY and shot '
               'EY.',
               'Radial observation operators and mechanism discrimination context. Zone observations share '
               'shots; no resolved radial flow or transient transport, and no cross-study matched-shot '
               'join.'),
 'ribes2021': ('radial_ey: 12 basket/contact-screen/zone rows, radii and local/whole-shot EY.',
               'Basket/screen radial extraction context, separate from Ribes 2020 conditions. Spatial '
               'endpoints do not identify a unique flow mechanism or provide radial time-series truth.'),
 'romancorrochano2015': ('table2: 12 grind/bulk-density/permeability/SD rows with Tukey grouping.',
                         'Separate source permeability priors and uncertainty context. Bulk density is not '
                         'wet operating porosity; methods and apparatus must be reconciled before EWP use.'),
 'romancorrochano2017': ('Comment-prefixed CSV tables/figures carry diffusivity, hindrance, partition '
                         'coefficients, tamped permeability, extraction inventory and model prediction '
                         'error. Printed thesis pages are retained in comment provenance.',
                         'Source reconstruction and mass-basis/unit adapters. Fitted transport parameters '
                         'and digitized model error are not direct independent observables; strip comments '
                         'before parsing, preserving source notes.'),
 'schmieder2023': ('S1 Fraction Mass & Concentration sheet: 292 sheet rows including headers; normalized '
                   'raw_fractions: 288 rows with exp/rep/fraction, fraction/accumulated mass g and three '
                   'analytes mg/g. S2 fits and S3 cup totals are different subsets; copies occur in two '
                   'directories and an archive.',
                   'Fraction delivery and within-campaign replicate analysis via exp/rep/fraction. Fit '
                   'parameters are derived, cup totals overlap fractions, and Pannusch shares the '
                   'fit-campaign lineage. No independent cross-corpus doubling or production-inventory '
                   'bridge.'),
 'schulman2011': ('The quoted comment/header layout defeated the initial strict CSV reader; the final '
                  'comment-filtered structural receipt recovered 14 rows with six consistent columns: '
                  'basket, D_base_mm, d_hole_um, sigma_hole_um, A_h_mm2, grid.',
                  'Basket geometry context is available in the public source card. Structural recovery '
                  'is not a new scientific qualification: face-side hole area has tapered-hole bias, '
                  'hole count is derived and plate thickness assumed. Check source conventions for '
                  'any adapter. No pressure-loss experiment held.'),
 'smrke2024': ('Figures 2–7 and supplementary Fig S1 are present as digitized CSVs and images. Fig S1: '
               '18,001 time/flow/series/run-index rows; PSD curves: 4,342 sampled curve rows. Fitted '
               'PLSR/sensory curves are separate from experimental marker digitizations.',
               'Fines/PSD/flow-shape and observation-operator context. Dense pixel-derived points are not '
               'independent shots. The card statement that the supplement was not held at intake is '
               'historical; this census confirms its digitization is held, without recovering native machine '
               'logs.'),
 'sobolik2002': ('Tables 1–2 coefficients, figures 1–3 and 6 digitizations, apparatus dimensions and '
                 'equation-evaluated grids are distinct subsets. omega is solids mass fraction, T in degC, '
                 'viscosity Pa s; shear-rate/shear-stress columns exist in Fig 1.',
                 'Property priors and law sensitivity. Computed grids are model output; Weisser refit and '
                 'concentrated solution measurements are distinct lineages. Source-domain and 90 C '
                 'extrapolation limits from rheology work persist.'),
 'telisromero2001': ('Two Markdown table transcriptions: 24 Newtonian viscosity cells and 27 K/n pairs. G10 '
                     'CSVs are alternative normalized representations; Xw is water mass percent, viscosity '
                     'table displays 10^3-scaled Pa s.',
                     'Measured-source fluid-property anchors and bounded sensitivity; not new shots or fresh '
                     'espresso. Keep industrial-soluble-extract transfer, dilute continuation and '
                     'source-table rounding explicit. No article PDF or rheograms held here.'),
 'vacaguerra2023a': ('Figure 12: 50 measured/calculated dry-porosity rows; Table C1: nine conditions with '
                     'distribution, dosage, epsilon_0, pressure/flow/height and errors. Tables 1–3 hold PSD '
                     'and fitted coefficients.',
                     'Dry-porosity source operators and separate priors. EWP qualified two porosity supports '
                     'across this and Wadsworth; Figure 12 is operator-only, permeability stress-only. Dry '
                     'does not equal wet porosity.'),
 'visualizer': ('Raw/bronze and normalized compressed JSONL shards, index and provenance are held. '
                'Structural inspection checks schemas without exporting values. Prior qualified canonical '
                'current-state count is 23,169; shard lines include versions and are not additional shots.',
                'Operating histories and empirical baselines, subject to recent-public-window selection and '
                'unknown sensor location. User-entered TDS/EY is not qualified fraction chemistry. Prior '
                'boundary/onset and machine-prior decisions are exhausted as documented in EWP; new '
                'questions need a distinct decision or new semantics. Research access does not grant raw '
                'redistribution.'),
 'wadsworth2026': ('Table 1: 22 coffee/dial rows, PSD radius moments in SI, total/connected porosity, '
                   'connectivity, surface area and permeability/error; 21 nonmissing permeability values.',
                   'Separate structure/permeability priors and source operators; keep total and connected '
                   'porosity distinct. Grinder-specific dial and untamped/compacted states do not transfer '
                   'automatically to EWP.'),
 'waszkiewicz2025': ('traces_per_brew: 57,000 samples, 57 source labels; known duplicate leaves 56 distinct '
                     'brews in 11 conditions. Columns distinguish pressure__bar (line), '
                     'basket_pressure__bar, mass__g and derived mass_flow_rate__g_per_s. TDS: twelve 5-s '
                     'fractions; calibration and brewer curves separate.',
                     'Controlled source-internal hydraulic reconstruction and fair baselines. Duplicate '
                     'labels do not add experiments; source aggregation retained them historically. Pressure '
                     'forcing cannot also validate pressure; derived flow and mass share information. '
                     'Existing resistance/poroelastic negative decisions stand.')}

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
            "external_corpus_id": source.get("external_corpus_id"),
            "discovery": {"observed_structure": DISCOVERY_NOTES[family_id][0],
                          "practical_use_and_limits": DISCOVERY_NOTES[family_id][1],
                          "snapshot": "puckworks/data/LOCAL_CORPUS_SNAPSHOT.json",
                          "guide": "docs/data/ESPRESSO_DATA_GUIDE.md"},
            "aliases": sorted(aliases.values(), key=str.lower),
            "manifest_dataset_ids": dataset_ids,
            "source_registration": source_registration,
            "rights_access_status": rights,
            "raw_access_status": raw_access,
            "model_chain_stages": MODEL_CHAIN_STAGES[family_id],
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
