# MODEL-PANNUSCH2024-FLOW-TEMP-FV-003 handoff

G2 / NUMERICAL_METHOD_CHANGE; RESEARCH_ONLY.
PHYSICAL_VALIDATION=NOT_ESTABLISHED.

The additive API is
`puckworks.models.pannusch2024.flow_temperature_history_fv.simulate_flow_temperature_history_fv`.
`FlowHistory` supplies strictly positive SI m^3/s through constant intervals or
linear knots. `TemperatureHistory` remains unchanged. Both histories independently
cover the explicit model interval. Returned fields are physical cell averages;
source geometry and coefficients are fixed. Mout is evolved with the same
midpoint-frozen T/Q operator as phase masses. Prescribed volume is independently
integrated analytically, including interior observations and delayed fractions.
Numerical frozen-step and prescribed-flow diagnostic fluxes remain separate.

The new joint-linear temporal target is **5e-4 on fixed source scales**, including
interior observations. This is one-tenth of the retained .005 spatial
fraction/Mout allowance and **does not amend or inherit 002's tighter 1e-6
temperature-only qualification**. Runtime calls retain accuracy NOT_ASSESSED;
COMPLETE means integration/support, not qualified accuracy. Unsupported values
are null with reasons; inadmissibility or unresolved mass differences suppress
public fraction concentrations. Neither flux diagnostic is an exact solution.

## Outcome

**VERIFIED_ON_DECLARED_CASES**: all 32 planned executions completed and every
frozen gate passed. No candidate/reference failures, missing coverage, correction
trajectories or incomplete numerical checks remain. Constant-Q comparisons are
bitwise equal on all compared numerical channels; the worst default/Radau
fixed-scale difference is 8.1970955e-5. Primary endpoints, requested/diagnostic
samples and quadrature nodes were checked; this is not an all-time floating-point
certificate. The full campaign consumed 924.253093 execution wall-seconds plus
53.833501 auxiliary seconds, **978.086594 of 1800 seconds**, with all four
correction slots unused. Retained test/reference/reporting defects were corrected
in this task and are classified separately in QA.json.

## Evidence and reproduction

[RESULTS.md](RESULTS.md) and [RESULTS.json](RESULTS.json) report every frozen gate,
failed/incomplete check, fixed-scale error and comparison. [CASES.json](CASES.json)
and [CONTRACT.md](CONTRACT.md) were frozen at
`7f97054` before numerical producer `92580e3`. [SOURCE_IDENTITIES.json](SOURCE_IDENTITIES.json)
binds actual producers and unchanged predecessor/source paths. [RESOURCES.json](RESOURCES.json)
records launches and charged numerical/auxiliary work; [QA.json](QA.json) is a
separate software receipt. Detailed arrays, logs and task authority are outside Git.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
python -m tools.pannusch_flow_temp_fv_verification execute \
  --evidence-dir "$EVIDENCE_DIR"

# Saved evidence only: no simulations, no additional trajectories.
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
python -m tools.pannusch_flow_temp_fv_verification report \
  --evidence-dir "$EVIDENCE_DIR" --output-dir "$REPORT_DIR"

python -m pytest -q tests/test_pannusch_flow_temperature_history_fv.py \
  tests/test_pannusch_flow_temp_fv_verification.py -m 'not protected_target_integrity'
python examples/pannusch_flow_temperature_history_fv.py
```

Execution reserves a receipt before each launch and resumes only unattempted
cases. The task budget lives in the Git common directory and binds the evidence
location; changing an output directory cannot reset it. An affected correction
uses `--case-id` with `--correction` and consumes the four-slot reserve. No
additional campaign is authorized. Report-only reductions also charge wall time.
Expensive qualification is outside ordinary CI. The example is N=8 and illustrative.

## Provenance and scope

Puckworks reviewed/actual base: `1d780b7fb57df4693e22e564010c891602df119d`.
EWP reviewed/remote base: `73ec476ffe6ac626705ca949e28b32935ddf2992`; read only.
Owner checkouts were preserved. Current metadata now records 001 PR314 merged at
`1e9f85a5e42d206baf05a0a95aa81847d506c9d5` and 002 PR315 merged at the Puckworks
base. Their numerical INCOMPLETE / declared-case VERIFIED dispositions and all
historical reports/receipts remain byte-identical. No legacy/default/registry,
source parameter, dependency-lock, workflow threshold or EWP change occurred.

[INTAKE.json](INTAKE.json) reuses the scoped 001 preflight and original MATLAB
text-inspection identities. This task inspected repository equation/parameter
code, the card, provenance and relevant catalog entries; it does not claim fresh
original-file access or native execution. Canonical IDs are
`pannusch2024/table2_params`, `pannusch2024/experimental_kinetics` and literal
`pannusch2024 (Mendeley repo)`. Equations, geometry and parameters supply authority;
experimental observations are not numerical campaign inputs. Reference builders
share these unchanged source quantities and closures, but independently assemble
concentration balances, history clocks/segmentation and volume arithmetic.

Pannusch et al., DOI 10.1016/j.jfoodeng.2023.111887; author code/data DOI
10.17632/y2tz67f6ry.1. Source-derived reports retain CC-BY-NC-3.0 separately from
first-party software licensing. No originals, protected observations, private
locators or full raw numerical outputs are committed. Programmed experimental
endpoints and beverage-mass derivatives remain ineligible inlet-flow mappings.
No empirical score, fit, profile benefit, taste, MATLAB equivalence, coupling,
production adoption, physical validation, laboratory operation or successor.

Final draft PR URL/exact head, hosted checks and the explicitly nonhuman
independent exact-head review are recorded on the task PR linked to issue #316.
Pending/unavailable CI or review is not PASS. The PR remains draft and unmerged
with auto-merge disabled. The owner may assess this bounded result; this task
does not start a successor.
