# PW-LOWP-DATA-SCOPE-001 — evidence inventory

**35 series/observable rows; inventory only.** [INVENTORY.csv](INVENTORY.csv) separates campaigns, fitting, prior exposure, sensor locations and state. Following [JOINT_CLOCK #412](https://github.com/trbrewer/puckworks/pull/412), no inspected external set yet supplies a fully qualified fresh-bed **q(P,M)** comparison across 0.5–4 bar.

| Rank / specific comparison | Question, priority and smallest gap |
|---|---|
| **1. COR15_PQ: Corrochano Fig.10** | Does pressure-response shape persist in an extracted, consolidated bed? Nine **tank** settings, 0.5–4.5 bar, make this the strongest controlled within-bed sweep. Recover numerical curves/raw averages and qualify corrected bed pressure versus upstream-meter flow; tank settings are not measured bed extrema. |
| **2. GAG21_*: eleven Gagné blooming shots** | Does pressure conditional on flow/T and history support a recovery explanation? Native logs and scale channels make this more actionable than publication-only transients. Declare phase/state and sensor operators; coffee-specific calibration and machine-to-bed transfer remain. Previously fitted/inspected, not blind. |
| **3. SCH23_SUMMARY / P24_FIT** | How does machine pressure respond to controlled flow at fixed grind/T? Three flow levels and retained originals offer an inverse constraint. Join machine/scale clocks and retain **maximum pressure**, not instantaneous pressure. Original S3 rows 59–62 are summaries; their mislabelled descendants in `cup_masses.csv` need qualification before use. No source correction here. |

**Direct records for a prospective test:** Gagné's machine-observable histories under their stated contract. **Mapping/join needed:** Corrochano, Schmieder/Pannusch, Moroney geometry anchors, moka and Visualizer records. **Context:** Moroney Fig.12, Petracco, Smrke, Perticarini, Foster CT, and computational permeability/flow. **Known but inaccessible:** Corrochano raw acquisition and Smrke author-held mass traces.

Inspection on **2026-11-03**, main `dce84b2`: configured collection/private manifest mounted; selected originals, qualified results and primary publications inspected. Rows distinguish data, reconstruction and catalog-only evidence; no exhaustive raw-corpus claim. Missing evidence means unavailable, not absent. Shared campaign IDs prevent duplicate counting; separate campaigns can still be fit-exposed. Waszkiewicz coefficients are not universal. Rights remain source-specific; raw files stay external. No fits, digitization, evaluation, scoring, acquisition or successor work.
