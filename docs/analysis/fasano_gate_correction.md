# Fasano source-figure gate and claim correction — R-05/T06

## Bounded plan

Reproduce the old arithmetic from accepted CSVs; inspect the cited source through
the established locator if available; replace the invalid pressure/flow predicate
with finite-table descriptive checks; reconcile direct current claims and
generated consumers; test the actual callable and deliver one unmerged draft PR
with auto-merge disabled. No successor or merge is authorized.

**G0 / NO_GOVERNING_PHYSICS_CHANGE.** This corrects a demonstrated QA predicate
and unsupported descriptions. It changes no production equations, algorithms,
closures, parameters, interpolation, solver settings, accepted observations,
frozen prediction bundle or training/holdout decision surface. Withdrawing the
QA assertion establishes no replacement scientific acceptance requirement.
PHYSICAL_VALIDATION=NOT_ESTABLISHED.

## Identities and source access

- Actual PW base/current main at intake:
  `29bda250a3ffd3f60b2f0b45c7abdbbc26361089` (PR #345 merged).
  Isolated branch `fix/fasano-source-figure-gate`; main had not advanced from preparation.
  Current code, history and open/closed Fasano PR search found no equivalent correction.
- EWP main inspected through read-only Git objects:
  `7c025527da7e07982428d4c78a3e79bfa29a76ac`. No EWP writes or execution.
  `dependencies/puckworks.lock.json` remains at PW
  `fc61c4670ec7bf801e40bb391aab16048b8da26b`, tree
  `1d553e44ee2f7480a5df521560801b478618cc84`.
- Dataset IDs remain `fasano2000_partI/fig8_6_model_q_inf` and
  `fasano2000_partI/fig8_7_thresholds`. SHA-256 of their unchanged CSVs:
  `cabef7918b139832317da106a6d4f316b3a43b53b8b67313fbc621d72a6f980b`
  and `09da1d58601028cc09e6706db922f91cc71bffeae609181c5181ab3c45d6abb9`,
  respectively. All four Fasano CSVs are byte-identical to base.
- Authoritative code inspected: the three Fasano gates in
  `puckworks/validation/gates.py`, registry wiring, and
  `puckworks/models/fasano2000_partI/fines_migration.py`.
  The latter changes only its module docstring; executable AST is unchanged.
  Python 3.12 `ast.dump` after removing that docstring has SHA-256
  `dc1f063816f14355598dd144086229f4ddb5cd8cd9dc927837cadc5cf355d849`
  at base and candidate.

Source locator: Fasano, Talamucci & Petracco, *The Espresso Coffee Problem*,
chapter 8, *Complex Flows in Industrial Processes* (2000), pp. 241–280.
**Original passage not independently rechecked.** The existing authorized
configuration and its private inventory resolve the Fasano family to four CSVs
and retained provenance, with no chapter/scan. The finite publisher check
confirmed the chapter identity and DOI
[10.1007/978-1-4612-1348-2_8](https://link.springer.com/chapter/10.1007/978-1-4612-1348-2_8);
only metadata/abstract and subscription access were available. The historical
“no DOI” manifest locator is retained as recorded provenance, not a new claim
that no DOI exists.

Actually inspected: retained source card (governing equations, scaling,
Proposition 8.1/Corollary 8.2 summary, Lemma 8.3 qualifications, implementation
proposal), provenance, and the Fig. 8.6/8.7 CSV bytes; Fig. 8.4 is covered by its
existing selected trace check. Original proposition/corollary passages, their
definitions, figure captions/axes/normalizations and Lemma 8.3 passage were
**not** independently inspected. No authoritative quotation, source-exhaustion
claim or new acquisition follows.

## Reproduced defect and replacement contract

Independent pre-edit CSV reduction and the old callable reproduced PASS:

| series | samples | peak p₀ | peak q | steepest β segment q | midpoint q | old gap | nominal q gap | final q |
|---|---:|---:|---:|---|---:|---:|---:|---:|
| beta1 | 16 | 0.310 | 0.235 | 0.32–0.33 | 0.325 | 0.015 | 0.090 | 0.173 |
| beta2 | 16 | 0.210 | 0.153 | 0.22–0.23 | 0.225 | 0.015 | 0.072 | 0.121 |

The old `abs(peak_p0 - knee_q) < 0.05` compared pressure and flow. Both being
nondimensional does not make them interchangeable. Replacing pressure with
peak discharge gives the nominal CSV-coordinate arithmetic 0.090/0.072 only:
these are not qualified cross-figure discrepancies, a rejected scientific
relationship or grounds for selecting a new tolerance. “Knee” meant the
sampling-dependent midpoint of the most negative adjacent secant, not an exact
physical transition or analytically identified knee.

The retained beta2 tail is `(0.45,0.114), (0.50,0.116), (0.55,0.119),
(0.60,0.121)`. The new gate explicitly accommodates this rebound. PASS requires
for each response a sampled maximum strictly inside the represented pressure
range, lower discharge before that maximum, and a final discharge more than
**0.005** below it. This unchanged inherited descriptive screen is not an
uncertainty estimate, theorem requirement, model-accuracy tolerance or
physical-admission threshold. No global post-peak decline, strict unimodality or
continuous-curve maximum is asserted. beta2's lower peak pressure is a retained
observation without a causal attribution to threshold ordering.

Separately, Fig. 8.7 has nonincreasing β samples on every adjacent interval and
a net drop. Its steepest-segment bounds, midpoint and secant slope are reported
without comparison to peak pressure or discharge. The result reports `peak_p0`
and `peak_q` separately, removes `tracks`, and declares
`cross_figure_relation="unassessed"`. `cor82` survives only as historical naming.

## Three evidence roles and scientific consequence

1. **Figures:** Fig. 8.6 is retained source-model output; Fig. 8.7 contains
   threshold inputs. The source-figure gate reduces these finite tables without
   running the fines-migration solver. Fig. 8.4 is a separate experimental-trace
   reduction; its reversal-signature PASS does not simulate chamber reversal.
2. **Source mathematics:** the retained card gives a necessary finite-time
   condition involving evolving **b − β(q)**. It records q₀=K₀p₀/L scaling
   dependent on pressure and distinguishes q̃∞ from p̃₀ in Proposition 8.1.
   Compatible figure/theorem normalizations have not been established here.
   No equality of peak pressure, peak discharge and threshold-segment flow
   follows, and static coordinates do not demonstrate cessation of release.
3. **Implemented model:** the separate free-boundary gate executes the existing
   Fasano-structured solver with project-chosen closures. Its existing <1% mass,
   boundary, temporal-sign and sampled pressure-response checks demonstrate
   bounded numerical behavior. They do not attain the card's historical
   machine-precision proposal, reproduce the unpublished source parameterization,
   qualify all parameters or establish the finite-horizon approximation as an
   exact asymptotic limit.

Temporal flow behavior at fixed pressure is different from variation of
asymptotic response across pressures. P2's temporal-sign argument does not use
the withdrawn peak–knee predicate: `harness.kappa_t_ladder` and
`gate_p2_kappa_ladder` do not call this figure gate; the separate
`harness.kappa_branches` fines branch calls the existing solver. Its retained
source basis is Lemma 8.3 under
**R=R(m+b) and (8.42)**, with separate tested solver behavior. The overly broad
“independent of closures” passage in `docs/ANALYSIS_P2.md` is narrowed accordingly.
It is not an exclusion of arbitrary closures or all fines-migration mechanisms.
The other P2 comparisons and frozen history are preserved.

R-04 relies separately on SCI-MD-010/011/012, sign/domain feasibility and matched
pressure observables; no inspected current R-04 conclusion depends on this
figure predicate. This correction supplies no missing constitutive inputs,
establishes no applicability to the rising-flow trace, demonstrates no new
successful pressure mechanism and validates no whole-pull prediction. Only the
Fasano gate/claim portion of R-05/T06 is complete; remaining R-05/T06 and R-04
work remain separately scoped.

## Current evidence and read-only EWP disposition

Gate/result, loader explanations, registry notes, model module docstring,
provenance, manifest, source-card guidance, intake comments and Paper 3
claim/observable/caveat/unsupported-claim text are corrected.
`CONSERVATIVE_SUMMARIES` separates figure reduction from solver verification.
The stable evidence IDs, `context_only`, `reality_facing=false`,
`sign_or_compatibility` and component `qualitative_capacity` are retained;
the source-figure relationship uses existing `not_empirical` vocabulary.
Execution/provenance classifications and evidence tiers are unchanged.
The existing vector producer labels a context-only record with an unsupported
claim as `negative`; here that is a ceiling/rebuttal label, **not** a failed
peak–knee scientific test. The relationship itself remains unassessed.

Regeneration uses registry artifacts (including current Paper 3 draft blocks),
evidence graph, available-data register, dependent local-family index, data guide
and Insight Foundry producers. Only Fig. 2's evidence-vector CSV is exported from
`evidence_graph.evidence_vectors()` using the existing CSV schema; no unrelated
figure rendering or scientific producer is launched. Generated diffs and
append-only Insight IDs are reviewed. Frozen reports, gate censuses, prior
results/receipts and the old ROADMAP intake entry remain unchanged; this note
supersedes their affirmative peak–knee interpretation.
The registry export, component matrix, appendix catalog, priority evidence
matrix and manuscript generated blocks remain byte-identical after regeneration:
their projected fields did not change. Insight ID registry entries are unchanged.

EWP paths inspected at its main identity above:

- `docs/analysis/data_leverage/SOURCE_FAMILY_COVERAGE.csv`: current Fasano
  `MODEL_VERIFICATION_ONLY` family summary should distinguish descriptive figures
  from the separate bounded solver check in a future authorized EWP update.
- `docs/analysis/sci_md_010/EVIDENCE_UTILITY_REGISTER.csv`: retained
  `SOURCE_MODEL_REPRODUCTION` family classification is too coarse for the
  Fig. 8.6/8.7 gate; preserve this frozen register and cite this correction in a
  future current interpretation, rather than rewriting history.
- `docs/analysis/sci_md_002c/CLOSURE_IDENTIFIABILITY_ASSESSMENT.md` already
  distinguishes structured demonstration, project-chosen closures and missing
  real-puck mapping; preserve it.
- `docs/strategy/WHOLE_PULL_MODELING_AND_SIMULATION_STRATEGY.md` calls Fasano a
  conceptual transport/deposition/release branch; no stronger claim requires
  correction. Existing data-fusion source screens remain historical context.

No EWP production lock update is proposed.

## Verification

Focused callable tests cover retained diagnostics, rebound, increasing/decreasing/
constant negative controls, inherited margin, full-interval threshold check,
peak-pressure ordering, accidental proximity and evidence/output consistency.
Multiplying both pressure axes by two leaves the corrected verdict unchanged
while flipping the old proximity predicate; this is an axis-representation
test, not a physical scenario.

Local Python 3.12 checks on the candidate content: **89 passed**, comprising the
new focused module, only the two selected existing Fasano intake/free-boundary
tests, register/data-guide/family-index tests and Insight Foundry tests. All three
actual Fasano gate callables pass; the solver gate reports its unchanged
mass/boundary/temporal/pressure booleans and peak p₀=0.6, while the reversal gate
reports 17.3/3.4/14.4 mL/s segment peaks. No parameter campaign was run.

All seven requested Paper 3 verification/reconciliation commands pass:
`registry_artifacts --verify`, `build verify`, `availability --verify`,
`corpus --verify`, `evidence_graph --verify`, and strict `paper3`/`all` scopes.
`insights verify`, committed register/index/guide producer equality, Ruff and
mypy (19 files) pass. `git diff --check` passes with `cr-at-eol` for the existing
CSV line endings; source data were not rewritten.

One initial local `pytest` console-script invocation failed during collection
because the repository's `tools` namespace was absent from its import path.
Using `python -m pytest` from the worktree resolved it; this was a local QA
invocation failure, not a scientific finding. No selectors or exemptions changed.
The ordinary quick suite uses the repository's normal
`not slow and not live and not gpu and not external_data` selection, including
normal automated integrity QA; no protected-target values were manually inspected.
Result: **6,822 passed, 70 skipped, 63 deselected** in 1,302.86 seconds,
with one existing development-salt warning from a Visualizer fixture.
This was the precommit implementation content committed as
`60d806643c755b6433cc53d3609ddf44410faf8e`; the 89-test focused selection also
passes at that exact commit. The subsequent commit only records this attribution
and refreshes Insight Foundry commit stamps/digests from that source revision.
It changes no tested executable, source observation or evidence claim.

Final local/hosted revision attribution is recorded with the draft PR. Active GitHub
ruleset `Protect main` (19053322), read at intake, requires `quick (3.10)`,
`quick (3.12)`, `verify-generated`, `paper3-scope-strict`, `all-scope-strict`;
ordinary G0 review applies, with no new scientific review stage.
