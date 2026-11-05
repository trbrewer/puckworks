# Reproduce the bounded no-fit audit

Actual PW base: `4c5ebab5df79929813949df7113c21290dde40cc`.
Pre-analysis PLAN commit: `389506deca7fc7087a5430b6c7619ef7882fe1c1`.
LC evidence is read with `git show` at
`0e1944de72819f0a058b99b6c0b2879e2d4ffde6`; PR #417 was unmerged at intake.
EWP evidence is read without checkout changes at
`67bead2a25bd7e61c16c4fe2c104d885d8d26dd9`. The local EWP worktree is at
`479783685360fdd31636890cf8e588a8fdd692d8` and remains unchanged.

## Inputs and rights

Underlying source files were inspected and rehashed, not merely catalogued.
Waszkiewicz, Myck, Białas, Puciata-Mroczyńska, Dzikowski, Szymczak and Lisicki
(2025), *Under pressure: poroelastic regulation of flow in espresso brewing*,
[Zenodo 18046315 v1.0.1](https://doi.org/10.5281/zenodo.18046315), CC-BY-4.0 data.
The accompanying source code is GPLv3; none is copied or imported here.
The existing campaign and prior target exposure are unchanged.

Authentication follows the pinned SCI-MD-010 INPUT_ARTIFACT_REGISTER for the two
processed data files and the pinned FORM_A manifest for source_inputs.json,
each of its 56 original-file hashes and the unchanged B0 observer source.
The public loader uses `include_aliases=False`; `12-8-6_alt` remains the excluded
duplicate of `12-8-6`. No physical brew is dropped. Endpoint targets are read
from the existing equilibrium-window loader; flow is not independently derived.
Supporting onset/clean-flow observations call the existing B0 helpers and replay
the saved FORM_A trace/mask exactly. Only observed columns of historical model
tables are consumed; no model is evaluated or scored.

| Input | SHA-256 |
|---|---|
| PLAN.md | `d01e2806a6ded016b0a2caaad2d602ac3018d0ce7b1aacd72d09ab278dc7d231` |
| traces_per_brew.csv | `55fcc6290113932d863b0b6aa6571ad169e5e32f78920659c2cefe2184abef08` |
| equilibrium_windows.csv | `c33bd01729cfe63db6d319d9c64afcac818050fdf8c888ab4d47dc233d5e2213` |
| FORM_A source_inputs.json | `a4f186f1affd6a8267b79bced5152c4b8d111cede2e894d84e1166f7eac149d9` |
| pressure_peak_stage_b0.py | `aa57d56b514a5e7eb9288a8bf37e070709bb4e9c9082111e1f050f39e429f458` |

[INPUT_HASHES.json](INPUT_HASHES.json) records every consumed original, pinned
table and loader/producer identity. Original files, full logs and PNG previews
stay outside Git. The retained endpoint pressures are the final 100-s grid
values, not a different raw interpolation or the final raw acquisition.

## Commands

From this PW checkout, in the existing development/figure environment with
NumPy, SciPy and Matplotlib, set these paths to the available read-only inputs
and a new external evidence directory. The git object databases must contain
the pinned commits above; this task does not require merging #417.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1
export PYTHONPATH="$PWD"
export WASZ_AUDIT_EWP=/path/to/espresso-whole-pull
export WASZ_AUDIT_RAW=/path/to/authenticated/espresso-v1.0.1
export WASZ_AUDIT_SOURCE=/path/to/FORM_A/campaign/source_inputs.json
export WASZ_AUDIT_WORK=/path/to/external/audit-evidence
mkdir -p "$WASZ_AUDIT_WORK"
/usr/bin/time -f 'user_seconds=%U\nsystem_seconds=%S\nelapsed_seconds=%e\nexit_status=%x' \
  -o "$WASZ_AUDIT_WORK/analysis.time" \
  python -m puckworks.analysis.wasz_3p5_endpoint_consistency_001 \
  --ewp "$WASZ_AUDIT_EWP" --raw "$WASZ_AUDIT_RAW" \
  --source-inputs "$WASZ_AUDIT_SOURCE" \
  > "$WASZ_AUDIT_WORK/analysis.log" 2>&1
python -m pytest -q tests/test_wasz_3p5_endpoint_consistency_001.py
python -c 'from puckworks.registry import run_all_gates; run_all_gates()'
ruff check puckworks/ tests/
git diff --check
```

The four CSVs and SVG are deterministic; run CPU metadata varies. The native
Matplotlib preview of the same figure was inspected. `VIZ_SPEC.json` records
its descriptive evidence scope. Supporting CSV condition rows are equal-brew
means of the per-brew scalar columns, including within-brew SDs; they are not
pooled sample summaries. Interval lists exist only on brew rows. Reporting
pressure uses the saved 0.1-s trace mask; final-clean-30-s trends use original
native samples and the unchanged helper, never that reporting mask. See PLAN
for each time origin/window and the inherited terminal and detector rules.

## Execution and CPU

Two successful producer runs used **5.44 CPU seconds**: the first generated all
requested statistics; the second additionally serialized the time intervals
underlying the same predeclared pressure-excursion durations. No window,
threshold, target or statistical operation changed. Figure preview/export work
used **2.50 CPU seconds**, including a failed optional CairoSVG import (0.01 s),
an ImageMagick preview (1.09 s), and the accepted native Matplotlib preview
(1.40 s). Total timed audit/figure CPU: **7.94 s = 0.002206 core-hours**,
user plus system, including child processes. This is processing CPU, excluding
interactive file inspection, repository tests and hosted CI; it is not wall time.
Every producer attempt succeeded; no fitting, optimizer, simulation or model
score was run. Preview logs/timers and both producer logs/timers are retained
outside Git. The final optional PNG-export argument changes no CSV or SVG values.

Focused checks cover unsorted/unfiltered raw records (including missing fields,
duplicate/backward timestamps and non-bridged gaps), synthetic endpoint pressure
pairing with unsupported-time rejection, band-duration arithmetic, adjacent
steps, and all 56 stored endpoint identities. The exact unchanged base's prior
offline suite (8,065 passed) is reused; registry gates passed in this worktree.
Final required CI links and head identity are recorded on the draft PR, avoiding
a documentation-only commit that would supersede the checked head.
