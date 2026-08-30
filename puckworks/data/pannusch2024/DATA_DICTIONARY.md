# Pannusch reconstructed-data dictionary

These CC-BY-NC-3.0 source-derived records are third-party data. Empty fields mean
`UNKNOWN`; they are not zeros. `shot_id` identifies a physical brew,
`physical_replicate_id` its within-condition replicate, and `fraction_id` the source
collection interval. Analytical rows never create additional physical shots.

Campaigns are `FIT_2021_12` (source fitting) and `PREDICTION_2022_03`
(source-designated prediction). Coffee product, lot, roast batch, and campaign are
separate fields; `UNKNOWN` and `UNRESOLVED_*` must not be joined as identities.

Concentrations are mg/g measured liquid for named HPLC compounds and percent for RI
TDS. Fraction liquid is measured mass in g. Derived mass is concentration × fraction
mass (and ×10 for percent TDS to mg/g). Times are seconds. Program values are machine
instructions, not measured puck-face temperature or inlet flow.

Validity is `VALID` or `INVALID`; exclusions distinguish `INVALID_SPILL` from
`INVALID_ANALYSIS`, `SOURCE_EXCLUDED`, `MISSING`, `NONDETECT`, `VALID_ZERO`, and
`UNKNOWN`. Invalid values are retained by identity but left blank and never averaged.

Evidence labels distinguish directly reported, directly derived, fitted, and
programmed values. The March targets are `SOURCE_DESIGNATED_PREDICTION`,
`TARGET_EXPOSED`, and `SOURCE_INTERNAL`. Experiment 46 is direct recovered mass and an
`N1_OPERATIONAL_REFERENCE_ESTIMATE`; it is not total content, production M0, or fitted
`c_s0`. Fractions use measured collected-liquid mass and source collection times.

