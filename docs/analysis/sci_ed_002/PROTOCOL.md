# Protocol

## Estimands and sampling

`T_total[a,u]` is total assayable roasted content under SOP v1.0.0, reported as analyte mass per dry roasted-coffee mass using same-batch moisture. `I_ref[a,u|SOP_version]` is the separately measured, method-conditioned reference-extractable inventory. Neither is metaphysical total, production-accessible inventory, equilibrium inventory, or `c_s0`. `Q_production_solid_initial[a,u]` is `NOT_ESTABLISHED`.

Each group contains Arabica and Robusta at light, medium, and dark roast. Odd groups pair S1 at light/medium; even groups pair S1 at medium/dark. Every group has its own source study, package, lineage, materials, roast batches, custody chain, laboratory assignment, and organization. VG01–VG05 are open qualification; VG06 is sealed. Each open group preregisters one reserve material per species. Reserve activation is limited to documented qualification failure before analyte-result review and never counts until activated.

## Receipt, splitting, and replication

Custody begins at sealed receipt. Store dry, dark, and temperature-monitored; record every transfer. Complete analysis within the stability window qualified before commissioning. Homogenize each roast batch centrally with a cleaned burr mill, mix the entire ground batch, and randomize adjacent aliquots by a seeded blind-code list. Separate lanes cover moisture, total content, reference extraction, roast metrics, archive, and optional espresso. Retain 100 g or 20% of the homogenate, whichever is greater. Record split order, minimum lane mass, packaging seal, grind state, storage, contamination blank, and custody.

Moisture uses three independent adjacent aliquots. Total content uses three independent preparations across two non-consecutive batches. Reference extraction uses three independent preparations across two non-consecutive days. Both analytes are paired in each preparation; if method qualification forces adjacent aliquots, flag lost preparation covariance. Injections are nested technical repeats and never independent evidence. No pre-averaging is permitted.

## Holdout sequence

VG06 uses repository separation plus encryption controlled by an independent custodian. Operations may see identity and logistics metadata but model developers may not see analyte results, extraction outcomes, or aggregates. Audit all access. Emergency owner-approved access triggers review and presumptive invalidation. First qualify VG01–VG05; then replay unchanged SCI-MD-007 F0–F7 on real open data only. Predictor work and one-time VG06 unsealing each require later authority.

## Governance

No laboratory contact, quote, purchase, sample work, shot, model fitting, correction factor, production adapter, or runtime change is authorized. Any future `c_s0` mapping requires a separately authorized direct test of mass basis, phase basis, accessible pool, solid volume/mass, geometry, units, preparation state, and model interpretation.
