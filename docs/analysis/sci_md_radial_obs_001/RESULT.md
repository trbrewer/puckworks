# SCI-MD-RADIAL-OBS-001 source result

**The workbook identifies operational recoverable-solute contrasts, not radial
solid depletion without additional physical assumptions.** Source reconstruction
is REPRODUCED; the model-to-assay map is CONDITIONAL. PHYSICAL_VALIDATION remains
NOT_ESTABLISHED.

All **1,672 formula cells** replay within the prospectively frozen 1e-8 absolute
(named display unit) plus 1e-10 relative tolerance; maximum absolute display error
is below 5e-9. There are no unsupported formulas or cache discrepancies. All
2,629 numeric source-export cells agree with their decimal rounding intervals.
The workbook has 60 experimental shots, three explicit source rejections,
57 retained shots in 12 conditions, plus 10 distinct retention/flush measurements.
Repeated readings and the two LRR average cells are not additional shots.

The sheets use different mass bases. Sworks adds a source recovery-retention
correction and divides recovered solubles by inferred original section masses.
VST does neither: it subtracts recovered solubles per weighed dried residue.
The shared shot anchor cancels from each sheet's edge-center difference but
remains in fractional edge loss. Only Sworks algebra enforces initial-mass-weighted
section EY equal to whole-shot EY. Later plotting additionally anchors/scales;
its exact Monte Carlo algorithm is unavailable and is not reproduced.

Sworks Y54 uses unfiltered TDS despite its filtered label; excluded AL9 refers
to the following shot. Both anomalies are preserved in the executable graph.
The source q labels mean outer-to-total by their denominators; the original
calibration weighings are not present, so the code does not claim measured cutter
radii. Metal screen versus paper on top and a nominal flat 6-bar machine programme
replace stale bare-puck/unknown-profile interpretations only for future use.

Nine entries in the rounded historical registry table fall outside their stated
decimal rounding intervals. [RESULT.json](RESULT.json) names each affected
condition/quantity; exact discrepancies and new aggregates remain in the private
replay. The available evidence cannot assign each difference uniquely to card
transcription/rounding versus an unprovided later transformation. No tolerance
was widened, formula fitted or historical value silently corrected.

A concrete executable counterexample preserves all recovery measurements, dry
residues, initial masses/inventories, global inventories and cup anchor while
changing radial solid depletion. The missing information is the partition
between remaining solid and retained dissolved solute, plus recovery/drainage,
handling and initial regional-inventory assumptions. This generic example does
not claim a source-shot-specific ambiguity fit. The weaker composite remains
usable for a future explicitly source-conditioned observation comparison.

See [MEASUREMENT_MAP.md](MEASUREMENT_MAP.md) for derivations and dispositions,
[README.md](README.md) for reproduction, and [AUDIT.json](AUDIT.json) for the
independent pre-analysis audit. The subsequent EWP floating-point guard correction
changed no source formula, source data, tolerance or successful source replay.
Scientific/source status is separate from repository software and hosted CI
reported in the PR. The private original workbook, exports and aggregates remain
external because the actual expanded redistribution grant was not found.

NEW_NATIVE_INTEGRATIONS=0; NEW_NATIVE_BUILDS=0;
PRODUCTION_DEFAULTS_AND_LOCK=UNCHANGED. No merge, successor or native campaign.

Software QA: the full local quick selection ran 4,568 tests: 4,523 passed,
32 skipped and 13 failed on stale generated current-count/fingerprint artifacts
or the initially missing editable package installation. All 13 affected tests
subsequently passed after the required generators and environment setup; the
focused source/metadata suite (19), Foundry suite (65), current-count suites
(116 across the corrected run), and three remaining generator checks passed.
Lint and registry gates passed (65 PASS, one acknowledged historical exception).
These repairs change no assay formula, source value, tolerance or scientific
result. Hosted final-head CI is reported on the PR; earlier failed/superseded
checks are retained in its history. Current inventory counts and fingerprints
were refreshed; historical correction outcomes and numerical results were not.
