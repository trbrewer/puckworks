# Independent pre-score review: SCI-MD-5CQA-DELIVERY-001

APPROVED for one predeclared frozen PRED score only, with no retuning.
Reviewer: fresh independent Codex agent `independent_5cqa_review`; not a human,
not the implementer, and not involved in model fitting or selection.
G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.

Reviewed producer `cadb7aeaa00630ad311970610ec5763ad4ffc9a3`, tree
`f570fab32f9105cc77e9cc3eb89b5a952448e9f6`; freeze SHA-256
`da6023c0e0077f5f89d2a7ed877b1a3ff26c8c4bc6935b9263ecdf798184b7a1`.
No blocking finding or requested scientific correction remains.

The independent review checked the original owner contract and continuation,
current repository governance, all three isolated modules and their tests,
fixed protocol, source and dependency manifests, development artifacts,
saved models, coordinate-only predictions, and narrow G0 repair.
All 57 code/protocol and 710 artifact bindings passed. The code that fitted
the models is unchanged between fit commit
`2adea62cafd6486b8768b7b3ae2268411c942bba` and the reviewed producer.
The protocol commit predates fitting. All 49 retained original-run files
remain byte-identical to the continuation's preservation manifest.

The eight original source files and ten source registers match their accepted
identities. The review independently checked all 180 original FIT 5CQA slots
against MATLAB column 3. PRED source files were hashed only; no PRED chemical
values were read, deserialized or joined by this reviewer. The preparation's
retained silent reconciliation of 276 original slots and species-specific HPLC
formulas was inspected and its code audited. It uses column Y/area I, separate
FIT and PRED calibration formulas, and original unrounded values. Public-table
rounding is only a reconciliation tolerance. The original-vial geometry and
four-ULP fraction-3 anchor rule are unchanged dependencies.

The implementation contains exactly E0 and D0. E0 uses one bounded global
amplitude/decay pair and stable exact interval integrals; D0 uses the inherited
five-knot, 15-coefficient logistic architecture and fixed penalty. No inherited
coefficients or chemical query features enter the new models. Fold preprocessing,
support and initialization are FIT-only. Independent arithmetic checked all
15 whole-design exclusions, hierarchical weights, deterministic starts,
77 saved models, and all 231 retained-start objectives using a separate
256-point knot-split operator. Maximum objective discrepancy was
8.881784197001252e-16. Winning starts and the selected D0 lambda 0.0001
match the fixed selection rule.

Saved-model inference reproduced all 192 prediction records exactly, including
190 numerically qualified records and both copies of the single unsupported
flow window. Per arm, primary is 48/48, temperature 24/24 and flow 23/24;
FIT is 177/180 across all 45 original shots and 15 designs. The final domain is
0.06971540000000001 kg. Feature extrapolation remains diagnostic. Runtime
inference needs no training, optimizer call, source workbook or predecessor
private run. SciPy initializes some optimization utilities transitively through
its integration namespace; the runtime imports no optimization API and does not
invoke one.

Independent 90-digit analytic references checked 128 synthetic E0/D0
integrals, including narrow intervals and extreme allowed coefficients with
extrapolated features. Reported allowances covered every reference discrepancy.
One extreme synthetic interval remained explicitly numerically unqualified;
the fixed quadrature was not relaxed. One hundred independently calculated
synthetic metric panels and 15 threshold-edge decisions passed. Code inspection
and focused tests confirm original denominators, absolute shot bias before
condition averaging, numerical allowances in both adequacy inequalities and
all four increment criteria, unresolved overlaps, and the inability of
secondary results to rescue a primary failure.

Focused scientific tests: 32 passed, four optimizer-bearing tests deliberately
deselected to keep this review free of fitting. These tests include ten invalid
approval variants, strict species/units, immutable serialization, numerical
qualification, exclusions, support, duplicate scoring and durable failed-score
consumption. The reviewer performed zero optimizer calls, fits, PRED outcome
reads, real outcome joins, scientific score calls, or native EWP runs.

The G0 repair is correctly limited to the WP6 historical range. Original PR
#233 and its final result identify base
`f77d0e328496dc1e85bf00fdb06ccdc52d8b2108` and completion
`13c398e038c94ae8f95c8106e327e47d3d5f5345`, whose result blob is
`c3c751247307382e98295eab2ce8fd05e979c6bb`. Both objects exist, ancestry holds,
and all three protected paths are unchanged over that range. The actual later
#296 registry diff appends IDs and preserves earlier assignments. Git failures
fail closed. The repaired node executes and passes. The independent WP6/I-045/
I-076 run passed 119 tests with one pre-existing, separate generated-corpus
skip. Retained repair-only full baseline evidence passes 4,940 tests with
65 existing skips and 60 deselections. Repair commit
`99a9eef4dbe63063033842fe0837aa109dbaeaf8`, tree
`d936196454f88edee9fa538fb13282e48b0e1d72`, changes only the authorized test
module and concise explanation. This is not a PASS claim for unchanged main.

Cumulative real fitting accounting is 231 starts (E0 48, D0 183),
25,092 actual residual calls including 23,137 numerical-Jacobian calls,
at most 161 calls per start, and 38.97401571273804 fitting-stage seconds.
All starts completed; no failed or boundary starts were hidden. The original
blocked run used zero starts and scores; its 1418.985946 elapsed seconds remain
separate. One worker, one BLAS thread and the 12-GiB process cap are retained.
Total task evidence at review is 181,450,939 bytes, below 5 GiB.

This receipt authorizes only the original single frozen score. The score guard
and exclusive durable receipt precede the sole outcome join; failed or completed
attempts cannot be silently overwritten or rescored. Verification replays saved
inference without outcomes, and reporting consumes retained scores. The study
remains SOURCE_INTERNAL / TARGET_EXPOSED / RETROSPECTIVE. No adequacy conclusion
exists at this pre-score review. Physical validation and analytical uncertainty
remain NOT_ESTABLISHED. Source-derived models retain CC-BY-NC-3.0 attribution.

Final full task regression and hosted CI are separate acceptance evidence;
this review does not label pending or uninspected CI as PASS. No production
adoption, registry/default promotion, EWP change, merge, further family,
post-score retuning, second score or successor is approved.
