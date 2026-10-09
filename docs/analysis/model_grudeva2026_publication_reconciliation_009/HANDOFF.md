# 009 owner handoff

**CORROBORATED_PUBLICATION_DISCREPANCY; comparison complete.** Both qualified
baselines fail the same 17 selected publication targets in the same direction.
All 17 failures persist under both retained combined refinements. All four
inputs fail every publication family; there are no method-specific failures,
support differences, direction reversals or family-verdict changes.
Original-run provenance, and therefore the cause of the discrepancy, remains
unresolved. That does not make this completed comparison unfinished.

[RESULTS.md](RESULTS.md) gives maxima with both compared values, signed
residuals, exact target IDs and limits. [RESULTS.json](RESULTS.json) retains all
124 requested rows at stored precision: **72 included, 52 excluded, 0 unavailable**.
Each input has Figure 3 concentration 9/19 included, 10 excluded; all three
measured fronts included; Figure 4 concentration 5/8 included, three excluded;
and one arrival event included. Of the 18 included comparisons per input,
17 fail and the t=.4 front passes. Supported excluded values are diagnostic,
not passes. No numerical or extraction allowance was enlarged.

| Primary maximum absolute residual | P0 production | C0 comparator | Limit |
|---|---:|---:|---:|
| Figure 3 concentration, F3C-016, t=6.4, z=.9704579025110783 | .09706211176387364 | .09699961117395267 | .015 |
| Figure 3 front, F3F-003, t=4.8 | .013449181931561194 | .01345521083093193 | .008 |
| Figure 4 concentration, F4C-004, t=6.551378446115288 | .1413974742031971 | .14131064604731197 | .015 |
| Figure 4 arrival, F4A-001, z=1 | .12084982342895056 | .12088406935098295 | .025 |

Concentration residuals are positive: both methods predict higher selected
concentrations. Front-position residuals are negative: desaturation has reached
less depth. Both methods arrive later, at 6.5043084700454914 (P0) and
6.504342715967524 (C0), versus publication 6.383458646616541.

The earliest discrepancy supported by these selected coordinates is at **t=3.2**:
F3C-004/005/006 have shared positive concentration failures; F3F-002 has
residuals -.008050125762883997 (P0) and -.00805631094976117 (C0), just beyond
the .008 front limit. At t=.4 the measured front passes and all three requested
concentration values are excluded by the historical displacement mask. These
sparse targets do not establish an exact first divergence time.

The remaining shared witnesses are F3C-009/010/011 and F3C-014/015/016;
F3F-003; F4C-004 through F4C-008; and F4A-001. Common-support residual
identities close within the frozen scale-aware allowance (primary accounting
error is exactly zero). This is arithmetic consistency, not independent
numerical validation.

Refinements preserve all shared-failure witnesses and included/excluded target
sets; the numerical mask boundaries change with each input. Across common included coordinates,
the largest production/comparator concentration sensitivities are respectively
9.519822462930594e-6 (F3C-015) / 6.191121498511087e-5 (F3C-006) for Figure 3,
and 2.705578589057289e-6 / 7.619790888363509e-5 (both F4C-004) for Figure 4.
Arrival changes are +1.069423756661081e-6 (production) and
-2.3328293158542124e-5 (comparator). The complete per-input maxima and every
common-coordinate difference remain separate; no baseline is replaced by an
intersection or refinement. These small empirical changes do not supply a
rigorous continuum-error bound.

## Execution and software evidence

Selected base is actual #330 merge
`ab28bd1d20b4fec43d6023a15bc628ee9f0bebcc`, tree
`2aced72fda1c8413d572f803319b7899b9dcb3e5`, with the supplied ordered parents.
Main had not advanced. [INTEGRATION.json](INTEGRATION.json) binds all seven
successful exact-merge PUSH workflows and all 17 applicable jobs on attempt 1;
quick-pr 37957821862 is successful. No PR-head check substituted for integration,
and no successful workflow was rerun. No equivalent 009 branch, PR or execution
was present. Unrelated owner worktrees were preserved.

[EVIDENCE_BINDINGS.json](EVIDENCE_BINDINGS.json) records actual admissions,
including original arrays/observations, environment, sources, task/row/attempt,
plans, closed predecessor ledgers and the accepted certificate composition.
Every 009 admission exactly equals the corresponding 008 binding.
[ACCOUNTING.json](ACCOUNTING.json) closes **one archive assessment** in
**87.63170858900412 seconds**, with peak resident memory 7,896,387,584 bytes.
Exit 2 is the expected completed-disagreement result. There were **zero new
production simulations, comparator simulations, qualification/certification
campaigns or fits**. Existing bounded solver fixtures did execute in ordinary
software QA; no claim of zero solver calls across all QA is made.

[PRE_SCORING_REVIEW.json](PRE_SCORING_REVIEW.json) is the independent nonhuman
audit of contract `ab4d874bb4d93b17ced4610e72b77505db72b833fc2a6c0445f39805cf6c888b`.
Its two manufactured-data findings were corrected before scoring. The ordinary
baseline passed 6,371 tests (67 skipped, 63 deselected), using the unchanged
selector; all 178 affected tests pass, including 58 new manufactured tests.
Ruff, configured mypy and registry gates pass. [QA.json](QA.json) records
generated/integrity, scientific-baseline and packaging results separately.
A packaging-of-evidence script initially mistook the adjacent log for an
attempt directory; its directory filter was corrected and only report assembly
repeated. The scientific score, contract and assessment outputs were unchanged.

The draft PR carries the exact candidate head/tree, current-candidate hosted
run/job conclusions and final independent nonhuman review receipt. At this
committed report's construction those final delivery checks are pending;
the PR's exact-candidate receipt supplies their later disposition without
misrepresenting an earlier review as review of a later head. No human approval
is implied. EWP main remains `16eec1dda24ebf658965eddcf1a6fffa81903b32`, with
dependency-lock SHA256
`52b15ceef87d503a3e77c6e3c1cbed785185d2dde0b79647e5fbe309395d2f10`;
no EWP files were written.

## Source interpretation and cause

**DEMONSTRATED source/provenance facts:** the unchanged fixture identifies the
gray asymptotically reduced curve, not a finite-epsilon full-model curve.
[SOURCE_REUSE.json](SOURCE_REUSE.json) verifies the original fixture PDF and
both embedded image identities, and compares both retained 002 extraction
artifacts with every immutable target coordinate, value and extraction bound.
No new extraction was performed. The original PDF container SHA256 is
`5b9e41e85591dce8a32b923663ee3ccf9e00c0ac34dc17659864ff7417326a29`;
002 inspected a different PDF container,
`592304014b7be482b5fe2814d730f7d128f9ec2e77d6f7d25f8e0292c5fce5e5`.
Both retain the same qualified Figure 3/4 image identities. The alternate
container and supplement inspection are reused from the hash-bound 002 audit;
they were not reacquired or re-extracted here. No distinguishing contradiction
justifies changing the fixture, source or historical observation records.

The [001 contract](../model_grudeva2026_reduced_001/CONTRACT.md),
[002 source audit](../model_grudeva2026_reference_002/RESULTS.md) and unchanged
[card](../../cards/grudeva2026_2.md) map Eqs.21/29 to phase capacities,
Eq.67 to liquid transport, Eqs.68–70 to fixed-depth grain diffusion, Eq.74 to
the desaturation-front jump law, and Eq.75 to the outlet/event conventions.
Eqs.76/77 set phi_f=.64, phi_b=.16, phi_l=phi_T=.20, varphi_lb=0, q=1 and
D_sb=1; gamma=1, beta=3.2, delta=.8, a=4.2. Both initial concentrations are
Table 2's 1.388. Wetting is min(t,1), horizon 8. Time is
t_dim/(phi_T*L/q_app), depth z_dim/L, liquid concentration c_l/c_sat.
No cafe-case diffusivity, inventory fit, clock or coordinate shift was used.

**CONSISTENT_WITH_BUT_NOT_ESTABLISHED:** agreement of the two qualified
discretizations can be consistent with a difference shared by their source
interpretation or by the original figure-producing settings/observation
operation. It does not identify which explanation applies. The documented
Table 1 identity 310/224=1.383928571... differs from the selected Table 2
1.388, and printed Eq.71 has an absolute/elapsed-time inconsistency. The
implemented autonomous Duhamel kernel uses t-u, with activation at
t_desat(z)=s_d^{-1}(z), distinct from wetting time z. Those choices are
explicit and retained; their existence is not evidence that they caused
the plotted discrepancy. No alternative setting or source interpretation
was fitted or executed.

**UNRESOLVED:** which exact configuration, source revision, saved arrays and
plotting/observation operation produced the gray Figure 3/4 curves? A
versioned figure-producing run manifest with initial concentrations,
diffusivity, time/activation conventions, saved t/z/concentration/front
arrays and the plotting script would distinguish a configuration difference,
an implementation/interpretation difference and a plotting/readout difference.
The adapted permission-attributed 004 reference lineage is neither that
original execution nor a wholly independent source interpretation. Two
agreeing implementations do not establish author error. Existing source
evidence does not resolve that original-run question; this is not a claim
that those artifacts do not exist or that external evidence is exhausted.

Historical 001/002 publication assessments remain unchanged. Their baseline
captures and legacy Result profile interpolation differ from 009's original
006 capture qualified by 007, retained certified 007 combined capture, and
qualified 004 final comparator captures. The new production concentration
comparison consumes the qualified raw-state diagnostic profile directly.
These are multiple provenance differences; changed scores cannot all be
attributed to the observer without a matched causal experiment. The original
P1 failed replay gate and DIAGNOSTIC_ONLY origin remain recorded alongside
the accepted certificate; no qualification or certification was rerun.

## Component use and limits

The standalone component can support research calculations on the declared
fixed-flow reduced equations with the configuration-specific numerical and
observation qualifications retained here. Publication agreement must be
reported from these actual comparisons. Empirical refinement differences
are not rigorous continuum-error bounds. This work earns no physical
validation, arbitrary-shot applicability, author-error conclusion, Guided
Pull or EWP integration, production adoption, release or default change.
Figure 5 remains **FIG5_REFERENCE_INCOMPLETE**; two reduced implementations
cannot reconstruct its full/reduced spatial MSE or epsilon convergence.

## Reproduction and delivery boundaries

The frozen [CONTRACT.json](CONTRACT.json) binds exact original P0/C0/P1/C1
identities through the unchanged 008 authorities. The 009 wrapper verifies
actual #330 selected-base integration and reuses only the unchanged admission
helpers. It never invokes 008's task wrapper or completed comparison.
Resolve the existing owner evidence parent through the retained task
configuration and predecessor root bindings; full arrays, private paths,
source PDFs and raw logs remain external. Use the frozen Python/NumPy/SciPy
runtime and a new non-overwriting attempt directory:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python -m puckworks.analysis.grudeva2026_publication_reconciliation_009 \
  --evidence "$GRUDEVA_EVIDENCE_PARENT" \
  --output "$GRUDEVA_NEW_009_ATTEMPT" \
  --integration docs/analysis/model_grudeva2026_publication_reconciliation_009/INTEGRATION.json \
  --review docs/analysis/model_grudeva2026_publication_reconciliation_009/PRE_SCORING_REVIEW.json
python tools/grudeva2026_publication_reconciliation_009_report.py \
  "$GRUDEVA_NEW_009_ATTEMPT/results.json" "$GRUDEVA_NEW_009_REPORT"
```

Exit 0 means complete agreement for all inputs; **2 means a completed adverse
scientific assessment**, not an implementation failure or reason to retry;
3 means incomplete admission/support, preserving any qualified failures;
1 means an implementation, contract or operational failure. Reproduction
instructions are not an automatic rerun authorization. No application timeout,
numerical budget, memory ceiling or invocation quota is added; actual OS/hosting
limits, process/memory/disk monitoring and durable locked accounting remain.

This is G1 / NO_GOVERNING_PHYSICS_CHANGE and a public, previously exposed
numerical-reference comparison, not a blind or independent experimental
validation. Keep the single PR draft and unmerged, auto-merge disabled and
issue #67 open. EWP and its dependency lock remain read-only. No successor
is started or authorized. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
