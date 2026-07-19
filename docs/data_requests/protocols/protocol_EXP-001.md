# Protocol pack — EXP-001: Synchronized whole-shot telemetry and cup chemistry

**Scientific decision.** Does the guided-pull/Cameron chain reproduce the measured pressure/flow/mass time histories and final TDS/EY on one machine + coffee?

**Models / gates affected.** `cameron2020.extraction_bdf` → `gate_cameron_conservation`.

**Apparatus.** espresso machine with basket-pressure and beverage-mass logging; refractometer for TDS. Record the full apparatus in `../templates/apparatus.yml`.

**Preparation.** Follow the site's standard puck preparation; record dose, grinder, basket, and coffee
lot in `../templates/shot_metadata.csv`. Do not change the grinder dial mid-block without recording it.

**Calibration.** Calibrate every instrument before (and where possible after) the block; log in
`../templates/calibration.csv` with method, offset, and scale. Sampling rates: preserve the fastest
valid native rate; a minimum useful rate is derived from a pilot (`PILOT_REQUIRED`), not prescribed.

**Experimental factors & controls.** single machine + coffee lot per block; distinguish prescribed vs measured pressure, scale-derived vs measured flow, target vs achieved beverage mass.

**Sequence.** Record one `shot_id` per shot; time series in `../templates/shot_timeseries.csv` use
monotonic `elapsed_s`. Preserve raw rows (`raw_or_processed = raw`); any resampling/derivation is a
separate processed file.

**Raw files.** As listed in the campaign's `raw_file_schema`. Deposit bulk raw data externally
(Zenodo/OSF) with a DOI; submit metadata + dictionary + checksums here.

**Quality control.** Monotonic time; non-negative mass; achieved-vs-target beverage mass within the
recorded tolerance; (for EXP-001 chemistry) summed fraction mass matches cup mass within tolerance and
species recovery is bounded. A missing value is recorded as `missing`/`below_detection`/`not_measured`,
never zero.

**Stopping criteria.** Stop a shot on an instrument fault or an out-of-range input; record it as an
exclusion with a reason (`../templates/exclusions.csv`) — never discard silently.

**Exclusion policy.** Every excluded replicate is retained with a recorded reason.

**Analysis plan.** Preregister the primary observable and analysis (`PILOT_REQUIRED` until the pilot
sets the design). Declare a holdout before any fitting. The acceptance calculation is
`DESIGN_CALCULATION_REQUIRED`.

**Evidence ceiling.** See the campaign's `evidence_ceiling`. A single machine/coffee/rig result is not
a universal claim; a bracket is not a point prediction.

**Safety.** Hot water and pressurized equipment — follow the site's safety procedures.

**Rights.** Contributor-owned raw data under a licence the contributor can grant (CC BY 4.0 / CC0
preferred); Puckworks code is MIT. No private or unlicensed third-party data.

**Submission package.** `campaign_metadata.yml`, `apparatus.yml`, `calibration.csv`, the raw + processed
CSVs, `exclusions.csv`, `file_manifest.csv` (with SHA-256), the external DOI, and the licence. Open an
experimental-data proposal issue first.
