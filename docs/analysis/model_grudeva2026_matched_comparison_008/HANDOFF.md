# 008 owner handoff

**MATCHED_BASELINE_AGREEMENT_ON_DECLARED_CASE** for primary P0/C0 and all
three fixed secondary pairs. The four-pair scientific task is complete. Every
one of the eleven families and seven individual histories passes; no required
observation is unavailable and no qualified disagreement is detected.

[RESULTS.md](RESULTS.md) reports every family and history with both values,
signed difference, location, counts and limit. [RESULTS.json](RESULTS.json)
retains full stored precision, separate completeness/verdicts and the intersection
diagnostic. [DIAGNOSTICS.json](DIAGNOSTICS.json) localizes maxima, records physical
front distances and actual cup-plus-phase consistency. All four pair masks are
identical, verified by their full Boolean-array hashes; intersection diagnostics
therefore coincide with the headline support on this case.

## What the saved data establish

The primary maximum liquid-profile difference is +0.00021510927068019159 at
t=6.505, z=.995, shortly after both fronts have exited. Production/comparator
values are 0.28343165898570638 / 0.28321654971502619; the unchanged limit is .001.
The outlet maximum is +0.00018501067289122819 at t=6.53. The grain-profile maximum
is -0.000097430779996909855 at post-exit z=1, t=6.525; the seven-history maximum
is -0.00009817867267991609 at interior z=.5, t=3.25. Both are below .0005.
Production arrives 0.000034245922032383191 earlier in dimensionless time.
The largest activation displacement is -0.000050598047798278145 at z=.11.

The primary cup maximum is -0.000020793791875028944 at t=6.505, below .0001.
Liquid, fines and boulder inventory maxima are approximately 5.028e-6, 1.609e-5
and 8.649e-7, each below .0001 in the inherited `phi_T*L*A*c_sat` units.
The difference between actual cup-plus-all-phase totals is at most 1.687e-8
for the primary pair. This is a consistency diagnostic using actual amounts,
not a newly introduced gate or a complement inventory.

Comparator-only refinement reduces the liquid-profile maximum to 3.489349e-5
and outlet maximum to 2.456422e-5. Refining both gives 2.971592e-5 and
2.971450e-5 respectively, with cup maximum 7.324545e-6. Production-only
refinement has smaller mixed effects: the outlet maximum increases from
1.850107e-4 to 1.901610e-4 and the history maximum from 9.817867e-5 to
1.035319e-4, while the liquid/grain-profile maxima decrease. All remain below
the original limits. These are measured refinement sensitivities on identical
accepted masks, not certified continuum-error bounds or evidence that one
implementation is exact truth.

## Evidence, execution and software

The actual working base is `37f62d80ce972141b515b48c893244780e6dd097`, tree
`fcaaf3b83f999db45486b436601ccd018de0b4cf`. [INTEGRATION.json](INTEGRATION.json)
binds all seven successful exact-merge PUSH runs, attempts and applicable jobs.
#329 was already merged; it was not remerged and no workflow was rerun.
EWP main `16eec1dda24ebf658965eddcf1a6fffa81903b32` and lock SHA256
`52b15ceef87d503a3e77c6e3c1cbed785185d2dde0b79647e5fbe309395d2f10`
were read-only and unchanged. Unrelated owner worktrees were preserved.

[CONTRACT.json](CONTRACT.json), [SUPPORT.json](SUPPORT.json) and
[EVIDENCE_BINDINGS.json](EVIDENCE_BINDINGS.json) bind original P0, retained P1,
qualified C0/C1, source/environment identities and all admission outcomes.
Actual saved numerical records and production named arrays were inspected.
The Grudeva card is retained byte-for-byte because the qualified 004 source
bindings include it; the living roadmap and sprint point to these new results.
No owner-local evidence needed by this comparison was unavailable. Source
qualification receipts were reused, including the accepted 007 certificate;
original replay failures and diagnostic-origin labels remain untouched.
The comparator retains its permission-attributed modified reference lineage
and existing source-reuse notices. No source PDF or private correspondence is
redistributed, and the published-reference curves were not rescored or fitted.

[ACCOUNTING.json](ACCOUNTING.json) closes every new archive attempt:
one source-role freeze failure, one successful admission preflight and one
successful four-pair comparison. Total admission/comparison wall time is
175.82116250597756 seconds; the comparison attempt costs 88.03380397098954
seconds including full input admission. Peak comparison resident memory is
7,841,468,416 bytes. Predecessor costs remain separate. The initial report
serialization failure and affected renderer-only correction are also retained;
the scientific score was not repeated. New production simulations = **0**;
new comparator simulations = **0**. Actual OS restrictions were preserved;
no application deadline, memory ceiling, numerical budget or retry quota was
introduced.

[PRE_SCORING_REVIEW.json](PRE_SCORING_REVIEW.json) is the independent nonhuman
audit of contract `4f657f041145cf42916a9f37c4788d290d0b8bac47783c233c6c76be29d81e7c`.
The ordinary quick suite passed 6388 tests (33 skipped, 72 deselected), using
the unchanged repository selector. All 162 affected tests pass, including
71 manufactured 008 tests. Ruff, configured mypy, registry and generated/
integrity checks pass; [QA.json](QA.json) records scope and identities.
The exact final candidate head/tree, current-head CI run/job conclusions and
independent nonhuman actual-evidence review are reported in the draft PR with
external `final-ci.json` and `final-review.json` receipt hashes. Their status at
report construction is pending; the PR's exact-head receipts supply the final
disposition without pretending that earlier-head checks review a later commit.
No human approval is implied.

## Reproduction

Use the existing owner evidence parent and the retained Python/NumPy/SciPy
runtime from CONTRACT.json. Full input archives remain external. Resolve them
through the existing owner configuration; missing access means unavailable
evidence, never permission to replace the declared captures. In the checkout:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python -m puckworks.analysis.grudeva2026_matched_comparison_008 \
  --evidence "$GRUDEVA_EVIDENCE_PARENT" \
  --output "$GRUDEVA_NEW_ATTEMPT" \
  --integration "$GRUDEVA_008_INTEGRATION_RECEIPT" \
  --review "$GRUDEVA_008_PRE_SCORING_RECEIPT"
PYTHONPATH=. python tools/grudeva2026_matched_comparison_008_report.py \
  "$GRUDEVA_NEW_ATTEMPT" "$GRUDEVA_REPORT_OUTPUT"
```

The output directory must be new. `--admission-only` verifies inputs without
cross-method scoring. Exit 0 means complete agreement; 2 means complete with
disagreement; 3 means incomplete evidence/support; 1 means implementation,
contract or operational failure. This reproduction information is not an
instruction to rerun the completed task automatically.

Leave the one PR draft and unmerged, auto-merge disabled, and issue #67 open.
No successor is started or authorized. Production defaults, historical
scientific code/evidence, EWP and its dependency lock remain unchanged.

The two baselines agree within the existing limits on all eleven declared
observable families, including all seven grain histories. Refining either
method or both preserves that finding; comparator refinement generally reduces
the differences, while production refinement has smaller mixed effects. No
required comparison support remains unresolved. The excluded jump/young-age
regions are outside the inherited smooth-comparison claim, and physical
validation, continuum accuracy, publication reproduction and applicability to
arbitrary espresso shots remain unestablished. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
