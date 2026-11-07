# Reproduce PW-WASZ-TURNOVER-TIME-001

Base main: `4c5ebab5df79929813949df7113c21290dde40cc`.
The settings and input identities were committed before outcomes in
`a434a7386f1c02735d85beeb0fffe47179daa3b3`. No model fitting or refitting occurs.
Only this task's files are added. EWP, originals, production defaults and
historical result bundles remain unchanged; no dependency on PRs #421/#422
being merged. Their results motivate the question, not the observation operator.

Use Python 3.12.3, NumPy 2.0.2, SciPy 1.13.1 and Matplotlib 3.11.2 for the
recorded run. Install the checkout with `pip install -e '.[dev,viz]'` in a
research environment, pinning those library versions for byte reproduction.
The tests also run under the current development environment (NumPy 2.5.4).

```bash
# Set these to existing, read-only source locations; do not download a new cohort.
EWP=/path/to/espresso-whole-pull
RAW=/path/to/zenodo-18046315/upstream
NATIVE=/path/to/retained/FORM_A/campaign

# Optional explicit prerequisite; the full command also does this first and stops
# before time-series observations if any historical reference check fails.
OPENBLAS_NUM_THREADS=1 python -m puckworks.analysis.wasz_turnover_time_001 \
  --ewp "$EWP" --raw "$RAW" --native "$NATIVE" --reference-only

# Use a new output directory to compare with the committed bundle.
OPENBLAS_NUM_THREADS=1 python -m puckworks.analysis.wasz_turnover_time_001 \
  --ewp "$EWP" --raw "$RAW" --native "$NATIVE" --output /tmp/wasz-turnover-replay

python -m pytest -q tests/test_wasz_turnover_time_001.py
ruff check puckworks/ tests/
python -c 'from puckworks.registry import run_all_gates; run_all_gates()'
```

`RAW` contains `measurements_time_dependent/*.txt`; `NATIVE/source_inputs.json`
is authenticated against the retained FORM_A manifest. The read-only EWP checkout
was `479783685360fdd31636890cf8e588a8fdd692d8`. All required original, normalized,
historical-reference and inherited-code hashes are in
[INPUT_MANIFEST.json](INPUT_MANIFEST.json). The runtime authenticates every one
before computing outcomes. New code and plan hashes, brew order and the shared
draw-bank hash are in [RUN_RECEIPT.json](RUN_RECEIPT.json). The draw bank is
generated once with `default_rng(20261106)` in sorted condition order, using
Stage A brew order. Its SHA-256 is over concatenated little-endian int64 indices.

The native clock/terminal/flow/onset functions are inherited unchanged from B0.
No padded course array or onset+2-s fitting mask is used. `paired_window` integrates
piecewise-linear native flow and line pressure over identical, fully supported
2-s intervals. The exact Stage A reference is separate: endpoint flow and final
normalized pressure, historical bootstrap seed 20261029. All condition means,
pressures and historical condition intervals agree within 1e-10; the slope is
−0.06550641262782862 g/s/bar and maximum is nominal 6 bar. The observed slope
interval reproduces Stage A's four-decimal report, [−0.0880, −0.0403].

CSV units appear in column names. Empty numeric cells mean undefined, not zero.
Every attempted brew window is retained with its availability reason. Condition
means use the same available brews for pressure and flow. All actual windows have
full support. `TIME_SLOPES.csv` includes pointwise nearest-rank 95% intervals,
paired stable-100-minus-current and current-minus-previous differences, and
bootstrap maximum selection frequencies (ties contribute to every tied condition;
frequencies need not sum to one). For onset times, stable 100 s is a cross-clock
reference; there is no onset-100-s observation. `CONDITION_MEANS_BY_TIME.csv`
contains analogous paired flow changes. Resamples retain complete brew identity
across every time and both clocks; missing sampled values are never redrawn.

The final descriptive replay used **1.3294 CPU seconds = 0.0003693 core-hours**
(1.3299 s wall time, one BLAS thread), including authentication, reference
reproduction, 1,000 cached resamples, CSVs and the figure. No optimizer ran.
The first full run plus this replay total **0.0007627 core-hours**; the replay
moved the figure legends outside the data panels and all five CSVs remained
byte-identical. No observation or statistical rule changed.
Focused tests and required CI are separate verification cost; their status is
reported in the PR. Receipt timing fields naturally vary on replay; the numeric
CSVs, draw-bank hash and SVG are deterministic in the recorded environment.

Attribution: Waszkiewicz, Myck, Białas, Puciata-Mroczyńska, Dzikowski, Szymczak
and Lisicki (2025), [Zenodo 18046315](https://doi.org/10.5281/zenodo.18046315),
CC-BY-4.0 data. Existing independent Puckworks reduction only; GPL source programs
are not imported. No new harvest, fit, physical claim or successor task.
