> **Historical planning snapshot — NOT an authoritative statement of current repository status.**
> The canonical status is generated at `docs/planning/STATE_OF_TRUTH.md` from `docs/status/current.json`.
> This file is retained for provenance only.

# PUCKWORKS — UPDATED NEXT-STEP PLAN

> Recorded verbatim 2026-07-16 (Tim strategic input). Review basis: main @ 19919c4.
> Parallel to `PRODUCT_FIRST_REPRIORITIZATION.md`; the two disagree on the PRIMARY
> lane (this doc → publication-integrity convergence; the other → product slice).
> Decision OPEN — see `STATE_OF_TRUTH.md`.

## EXECUTIVE DECISION

Optimize for **CONVERGE, PROVE, AND SHIP**. Highest-value portfolio:
0. Complete the deadline-bound B2 APS abstract submission.
1. Repair the publication-freeze and corpus-integrity boundary.
2. Lock and harden the pressure-atlas scientific analysis.
3. Produce a submission-ready Paper A release candidate.
4. Turn Paper 3 into a genuine evidence-linked, reproducible release.
5. Make quick/slow/live/release CI lanes operationally distinct.
6. Begin physical lateral-coupling work only as a bounded, card-first feasibility program.

Do NOT return to broad registry growth, generic data intake, or further G10
viscosity work as the principal track.

- Primary engineering lane: **PUBLICATION-INTEGRITY HARDENING** (real freeze
  lifecycle; immutable materialized snapshot; pressure-atlas estimand/inference
  upgrade; static-export readiness).
- Parallel publication lane: **PAPER A SUBMISSION RC** + **PAPER 3 EVIDENCE GRAPH & REAL RELEASE**.
- Next-science lane after release-critical work: **PHYSICAL LATERAL-COUPLING FEASIBILITY** (card/derivation first; implement only after go/no-go).

## WHY THIS HAS CHANGED

Foundations now present (registry typed; Paper 3 tables producer-generated;
corpus census + pressure-atlas commands exist; corpus bundle command exists;
live-contract workflow exists; G10 viscosity closure quantitatively checked;
Paper A reports baseline-relative transfer skill). The bottleneck is no longer
components/analyses — it is whether the repo can establish WITHOUT manual
interpretation: exactly which data were analyzed; which logical version of each
record was selected; whether that dataset was immutable; which estimand each
metric represents; how repeated users + irregular sampling affect uncertainty;
which dataset supports each gate; whether a paper bundle reproduces from clean;
and whether generated artifacts match the submitted manuscript.

## WP0 — DEADLINE + STATE-OF-TRUTH PASS (immediate, bounded)

**0.1 Complete the B2 APS DFD abstract submission** (calendar exception, NOT a
B2 reopening). Replace author/affiliation/presenter/funding placeholders;
confirm APS membership + presenter eligibility; recheck title/abstract vs portal
limits; regenerate every quantitative statement from a versioned producer; keep
rehearsal Visualizer-corpus findings OUT; preserve exact submitted
text/metadata/confirmation id; record artifact + content hash in the ledger.
Claim ceiling: "the same/similar integrated flow trace can be compatible with
distinct temporal mechanisms; controlled perturbations are needed to
discriminate them." Do NOT claim unique mechanism id, causal validation from
observational telemetry, latent-puck-state validation from the corpus, or broad
machine generality. Acceptance: submitted (or a recorded explicit decision not
to); exact text/metadata retained; every number has a producer path; no
rehearsal-corpus result in the abstract; broader B2 scope review-stable.

**0.2 Reconcile planning documents with repository reality.** One small
high-leverage "state of truth" change before selecting more work. Mark G10
closure complete; mark Paper A baseline-relative transfer skill complete; mark
landed corpus/registry/canary/Paper-3 generation accurately; split broad D2/D3
into done vs remaining; identify export-blocked work; archive duplicated tasks;
distinguish implemented / scientifically-validated / release-ready / submitted.
Prefer a compact canonical status file: item_id, state, artifact-or-test,
blocking dependency, next decision, owner type (code/scientific/maintainer/PI),
last verified commit. Keep the active queue ≤5 concrete outcomes. Acceptance: no
active item asks for Paper A's landed baseline comparison; G10 not shown as
active engineering track; corpus/Paper-3 scaffolding not listed unimplemented;
every active item links to code/test/manuscript/external-dependency; next sprint
chosen from one canonical queue.

## WP1 — MAKE "PUBLICATION FREEZE" A VERIFIED STATE (P0)

A publication freeze must be an immutable, independently verifiable artifact —
NOT a classification string callers assign to a moving store.

- **1.1 Correct logical-version selection.** Canonical latest rule: primary key
  max(updated_at); tie-break max deterministic append/source-version sequence.
  Do NOT use content-hash lexical ordering as last-written semantics. Persist/
  derive a deterministic sequence so latest(), latest(as_of), freeze, and audit
  pick the same winner. Equal-timestamp differing-content records remain visible
  as conflicts even though one deterministic winner is selected. Tests: same id
  diff timestamps; equal ts equal content; equal ts conflicting content; as_of
  before/after each version; reload-from-disk identical winner; shard-merge
  deterministic ordering.
- **1.2 Replace caller-assigned publication status.** CorpusView (mutable/read-only
  analytical view, may be exploratory); FreezeCandidate (readiness report over a
  source state); PublicationSnapshot (only returned by successful
  materialize-and-verify). Classification derived by the freeze builder, not a
  constructor arg. A publication bundle requires a verified PublicationSnapshot/
  receipt — not a string comparison.
- **1.3 Three-stage lifecycle.** `freeze rehearse` (read-only readiness/blocker
  report; never emits a publication snapshot); `freeze materialize` (reads a
  fixed source state; writes the canonical one-row-per-logical-record view +
  audit/provenance to a NEW destination; refuses overwrite); `freeze verify`
  (recomputes hashes/counts from an independent process; confirms source didn't
  mutate; confirms manifests + selection maps reconcile; issues a receipt used by
  bundles).
- **1.4 Materialize the frozen logical view.** Snapshot dir: snapshot_manifest,
  verification_receipt, canonical_records, selected_version_map, version_conflicts,
  exclusions, quarantine, qc, eligibility, measurement_dictionary,
  source_export_manifest, run_manifests/, file_hashes, README/DATA_CARD. Selected-
  version map: logical id, selected source version, file/shard, updated_at,
  append/version sequence, content hash, selection reason. Content-addressed
  snapshot id from canonical manifest + file hashes.
- **1.5 Verify immutability + source coherence.** Record source file list/sizes/
  hashes, version-key multiset, aggregate digest, counts before + after. Fail on
  change during the op. A publication snapshot ALSO fails when: source is a moving
  recent-activity feed rather than a coherent export; export cutoff absent;
  incompatible normalized schemas mixed without approved migration; required
  raw/Bronze lineage missing under policy; reconciliation mismatch; unknown schema
  versions; unresolved quarantine classes; unknown license/privacy/redistribution;
  unresolved analysis-required quantity semantics; unidentifiable importer/normalizer.
- **1.6 Expand the manifest** (snapshot_id/state, acquisition method, export cutoff,
  export creation ts, import start/end, source identity + file/aggregate hashes,
  logical/stored/duplicate/revision/conflict counts, schema counts, Bronze lineage
  counts, quarantine-by-reason, exclusion-by-profile, source/channel coverage,
  importer/normalizer/measurement-dictionary versions, privacy policy + key
  fingerprint, license/redistribution, source commit, analysis-spec hashes,
  materialized file hashes, snapshot aggregate hash).
- **1.7 Define + exercise the sanctioned-export contract NOW** (don't wait for the
  real export). Versioned export spec requesting: stable shot id; precise
  updated_at / opaque version id; export cutoff; visibility/deletion state;
  canonical + (permitted) raw telemetry; distinct machine vs integration/source
  fields; channel quantity kinds + units; commanded-vs-achieved identity; profile/
  control metadata; privacy-safe user linkage or documented absence; omitted-PII
  policy; format/partitioning/row counts/checksums; data-use/attribution/
  redistribution terms. Build a synthetic export (revisions; equal-ts conflicts;
  missing channels; source-family diffs; quarantine; incompatible schema; records
  around the cutoff) and run import→reconcile→rehearse→materialize→verify→bundle.

Acceptance: a classification string cannot create a publication snapshot; the
current exploratory/mixed corpus is REJECTED by the publication gate; freeze
produces a new immutable canonical dataset; verification detects source/
materialized mutation; equal-ts selection deterministic + documented; a synthetic
sanctioned export runs the complete pipeline; a verified RECEIPT (not a label) is
required by release analysis.

## WP2 — PRESSURE ATLAS V2 (P0)

Commit final estimands + analysis behaviour BEFORE inspecting a sanctioned full
export, then fit the implementation to irregular hierarchical telemetry.

- **2.1 Pre-analysis spec** `docs/analysis/PRESSURE_ATLAS_SPEC.md`: questions;
  population/unit; primary estimands; secondary diagnostics; active-interval def;
  eligibility profiles/thresholds; command-shape defs; sampling/interpolation
  assumptions; missing-gap policy; lag policy; source/user/profile strata; min
  cell sizes; uncertainty method; sensitivity analyses; multiplicity; permitted/
  prohibited claims. Hash the spec into every final output. Post-hoc threshold
  changes create a NEW explicitly-versioned exploratory spec.
- **2.2 Correct time-series semantics.** Commanded setpoint = zero-order hold
  unless documented otherwise; achieved = linear interp only within short valid
  contiguous intervals; never interpolate across a gap > predeclared threshold;
  error summaries integrate over TIME not sample count. Primary: time-weighted
  |err|, squared err, signed err; eligible active-time denominator; fraction of
  eligible active time within tolerance. Sample-weighted only as regression
  diagnostics.
- **2.3 Active brewing interval** hierarchy: documented machine/state signal →
  documented command phase → predeclared pressure fallback → exclude. Record the
  rule per shot. Exclude idle pre-roll, flush, tails, long missing intervals,
  serialization padding, invalid transitions.
- **2.4 Purpose-specific eligibility profiles**: pressure_descriptive,
  _steady_tracking, _transition_tracking, _lag_estimable, _source_stratifiable.
  Dimensions: monotone time; min active duration; min achieved/goal overlap; max
  missing fraction; max gap; timing jitter; channel-length relationship; finite/
  plausible pressure; command excitation; source-semantic confidence; required
  metadata. Each failure → stable exclusion token; emit inclusion/exclusion flow
  with exact denominators.
- **2.5 Classify commanded profiles** (constant plateau; single step; single
  ramp; multi-step; declining; complex) via min amplitude/dwell/merge/jitter
  tolerances + threshold sensitivity.
- **2.6 Primary + secondary metrics.** Primary: time-weighted MAE (bar), RMSE
  (bar), signed bias (bar), fraction of eligible time within absolute tolerance.
  Prefer physical units over range-normalized RMSE (undefined for constant-goal).
  Secondary: p90 |err|, steady bias, overshoot/undershoot, transition lag, rise/
  settling time, post-transition integrated |err|, clipping, valid coverage. Main
  result uses UNSHIFTED series; lag-corrected error only as secondary — never
  optimize away controller delay and present as perfect tracking.
- **2.7 Inferential hierarchy** (samples ⊂ shots ⊂ users): all-shot descriptive
  distributions; per-user summaries; user-cluster bootstrap CIs; deterministic
  one-shot-per-user sensitivity (seed from snapshot hash + spec hash + algorithm);
  optional one-shot-per-control-class-per-user. Replace "first encountered shot."
- **2.8 Concentration + subgroup support** per stratum: shots, users, max
  shots/user, concentration measure, missing-metadata fraction, incl/excl. Require
  declared min shot+user counts before subgroup estimates. Describe subgroups as
  observed tracking distributions, not machine-quality rankings.
- **2.9 Publication-grade bundle** per run: snapshot id + receipt hash; spec hash;
  commit; producer version; metric defs; thresholds; incl/excl table;
  concentration report; seeds; aggregate tables; figure source data; machine-
  readable results; output hashes; frozen-vs-exploratory status; evidence-ceiling
  statement. A partial/moving corpus → unmistakable "EXPLORATORY — NOT A
  PUBLICATION SNAPSHOT" mark.
- **2.10 Adversarial fixtures** (analytically calculable): perfect constant-goal
  tracking; known bias; known lag; known overshoot/settling; irregular sampling;
  dense sampling in one high-error interval; duplicate timestamps; missing
  interval; channel-length mismatch; jittering goal; short trace; multiple
  transitions; idle pre-roll+tail; prolific user; store-order permutation;
  deterministic bootstrap reproduction.

## WP3 — PAPER A SUBMISSION RELEASE CANDIDATE (P0/P1, parallel)

Move scope-frozen Paper A from complete draft to submission-grade archived RC;
don't reopen central scope unless release verification exposes a defect. 3.1 lock
central interpretation (transferred model has limited improvement over level-only
baseline under available external comparison; consistent across abstract/results/
discussion/captions/cover letter; include aggregate skill, pointwise win/loss,
calibration/transfer distinction, uncertainty/coverage limits, evidence ceiling).
3.2 one canonical manuscript source + target-venue submission dir (manuscript,
generated tables, vector figures, supplementary, bib, declarations, data/code
availability, cover letter, checklist). 3.3 human literature + authorship gates
(indexed search per handoff; reconcile bibliography; novelty wording; author
order/contributions; acknowledgements/funding; conflicts + data/code statements;
author approval — record search date/DBs/strings/decisions). 3.4 regenerate +
verify all claims from a clean checkout; fail when a manuscript number differs
from producer output. 3.5 real release artifact (deterministic source archive;
figure source data; env spec; software/data manifests; claim bundle; test report;
commit; checksum; citation metadata; verify clean install/regeneration, no
private data, stable hashes). 3.6 further analyses nonblocking unless a specific
reviewer objection with available data + predeclared interpretation.

## WP4 — PAPER 3 EVIDENCE GRAPH + REAL RELEASE (P1, parallel)

4.1 gate-/claim-specific evidence (EvidenceLink/GateSpec: gate_id, component_id,
claim/observable_id, callable/test target, source_card, dataset_manifest_ids,
evidence_strength, evaluation role, fit/eval independence, validity range,
expected metric/artifact, caveat, status). Typed non-dataset rationales: analytic
identity; dimensional check; numerical convergence; code verification; source-
curve reproduction; qualitative capacity; proposed experiment. A missing dataset
must never be indistinguishable from an unrecorded one. 4.2 genuine evidence
matrix (component_id, stage, execution_role, provenance_class, source_card,
claim_id, gate_id, dataset_id, evidence_strength, evaluation_role, validity_range,
status, caveat) as CSV/MD + graph JSON; resolve every dataset id against the live
manifest. 4.3 strict reconciliation fails on: dataset id absent from manifest;
missing source card/module; duplicate gate id; reality-facing gate lacking
evidence metadata; gate-less component lacking typed rationale; card describing
evidence absent from graph; component-summary vs gate-record conflict; stale
tables; stale manuscript counts. 4.4 replace assertions at validation boundaries
with explicit exceptions (survive `python -O`). 4.5 adjudicate ambiguous evidence
at claim/gate level (record what was fitted/evaluated, independence, reproduction
vs new validation, supportable/unsupportable claim — not by picking a stronger
enum). 4.6 make the bundle a real archive (clean checkout; regenerate; wheel+sdist;
fresh-env install; no-private-data worked example; smoke tests; deterministic
archive; manifest; SHA-256; verify). A path-printing command is `list-bundle`,
not `bundle`/`release`. 4.7 complete reproducibility resource contents; prohibit
private/non-redistributable Visualizer data. 4.8 prevent manuscript drift (stable
include markers/linter guarding component/dataset/role/provenance/evidence counts,
Table 1, Appendix A, schema description, evidence terminology). 4.9 one clean-room
public workflow run exactly as written in release CI.

## WP5 — CI LANES OPERATIONALLY DISTINCT (P1/P2)

5.1 markers (quick, slow, live, release, gpu, external_data); quick-pr = `-m "not
slow and not live and not gpu and not external_data"`; slow-science = `-m slow`;
live-contract = bounded live schema/normalization only; release = clean build/
install/example/archive create+verify; add an inventory test preventing unmarked
slow tests. 5.2 quick feedback stays offline/deterministic/private-data-free/no
large sweeps/multi-Python/schema+producer+numerics coverage. 5.3 slow runs retain
inspectable evidence (command/config/env/timing/tables/commit/input+output
hashes/report); don't rerun the same unclassified suite under a new name. 5.4
release CI builds + uploads the archive + checksum + manifest + clean-install +
producer verification. 5.5 strengthen the live canary safely (minimum bounded
requests; list/detail id consistency; field locations/types; in-memory
normalization; privacy-safe schema fingerprint; contract drift; never retain raw
payloads). 5.6 harden (least-privilege perms; timeouts; concurrency cancellation;
deterministic cache; action pinning; secret gating; one declared release env).

## WP6 — PHYSICAL LATERAL-COUPLING FEASIBILITY (next-science, bounded until go/no-go)

Determine whether a physical lateral-coupling model is well-defined, testable,
and distinguishable from the existing proxy to justify a Paper 4 program —
starting with SOURCE + MATH CLOSURE, not a code build. 6.1 source/model card first
(geometry; state variables; axial constitutive law; lateral pressure-gradient law;
conservation eqs; BCs; coupling topology; dimensional params; nondimensional
groups; relation to measurables; limiting cases; observables; validity;
unresolved assumptions) — clearly distinguish physical transverse Darcy coupling
vs numerical diffusion vs ad-hoc mixing vs the existing proxy regularizer. 6.2
minimum conservative model ladder (Model 0 uncoupled axial; Model 1 two-path/small-
network lateral conductance; Model 2 spatially-resolved transverse-pressure only if
Model 1 shows distinct useful behaviour) — each requires local + global mass
conservation, correct zero- and strong-coupling limits, dimensional consistency,
admissibility, solver convergence. 6.3 decision-relevant nondimensional regime
(transverse-redistribution vs axial-transport ratio → when negligible/homogenizing/
amplifying; which regimes experiments distinguish; is espresso inside a measurable
transition?). 6.4 stability analysis defined before coding (base state;
perturbation; Jacobian/tangent; finite-time amplification; boundary; numerical
verification; link to observable traces — not a diverging trajectory as sole
evidence). 6.5 synthetic discriminating tests (proxy ≈ physical in a limit; diverge
in a predicted intermediate regime; lateral flux reverses under reversed ΔP;
analytic conservation; known refinement expectation). 6.6 go/no-go review — proceed
only with a complete card + demonstrated conservation/limits + meaningful transition
+ distinguishable predictions + an accessible test + identifiable inference; stop/
redesign if the physical model collapses to the proxy over every accessible regime,
params unmeasurable, outputs indistinguishable, or numerics dominate the signal.

## WP7 — SANCTIONED CORPUS EXPORT RUNBOOK (trigger-based)

On a static maintainer export / coherent endpoint: 7.1 import into a NEW empty
store (never append to the exploratory rehearsal store); record checksums, cutoff,
config, privacy transform, schema mapping, importer/normalizer versions. 7.2
representative pilot (compare supplied vs imported counts; revisions/conflicts;
quarantine; channel coverage; source/integration semantics; quantity-kind
mappings; deterministic re-import). 7.3 import + reconcile full export (raw/Bronze
under policy; normalized versioned layer; exact version-key reconciliation; schema/
source/channel/privacy audits; license record; resolve quarantine before freezing).
7.4 freeze rehearsal (coherence; cutoff; revisions/conflicts; exclusions; user/
source concentration; semantics; privacy; licensing; analysis readiness — do NOT
change atlas thresholds after seeing headline results). 7.5 materialize + verify
(content-addressed snapshot; verify from a separate clean process; retain receipt).
7.6 run locked products (census; measurement/source dictionary; pressure atlas; all
declared sensitivities; figure source data; claim bundle). 7.7 integrate
conservatively (Paper 3 end-to-end resource; B2 only robust ecological context
surviving all sensitivities; Paper A not reopened absent review need).

## WP8 — EVIDENCE-DRIVEN INTAKE ONLY (opportunistic)

Score intake by evidence lift (+ independent/held-out gate; resolves a weak claim;
resolves quantity-kind/source-semantic ambiguity; supplies a lateral-coupling
param/target; reachable + clear provenance; usable licensing) minus (duplicates a
source-fit gate; code without a target claim; inaccessible raw; heavy transcription
for weak evidence; mere registry breadth). Priority: 1 independent-evidence gap;
2 sanctioned-export channel semantics; 3 lateral-coupling discrimination data;
4 reachable pending sources with a claim consumer; 5 generic breadth last. Do NOT
spend the next cycle on more G10 viscosity work unless a genuinely independent
espresso-condition dataset CONTRADICTS the current closure.

## RECOMMENDED MERGE SEQUENCE

PR0 state-of-truth reconciliation; PR1 version-selection correctness; PR2 real
freeze lifecycle; PR3 export contract + synthetic importer; PR4 pressure-atlas
spec + time engine; PR5 hierarchical inference + product bundle; PR6 Paper A RC;
PR7 gate-level evidence graph; PR8 Paper 3 RC; PR9 honest CI lanes; PR10 lateral-
coupling feasibility; PR11 final corpus import+freeze (trigger only); PR12 final
atlas + paper integration.

## STOP / GO GATES

A B2 abstract (GO when human metadata + portal reqs complete; don't wait for
corpus). B publication snapshot (GO only on successful materialize + independent
verify; a string is insufficient). C final pressure atlas (GO only with committed
spec + verified snapshot + active-interval + time-weighted metrics + tested
user-cluster inference). D source/machine comparisons (GO only with documented
source semantics + min user/shot support). E flow atlas (GO only with resolved
flow quantity kinds/units/provenance). F Paper A submission (canonical venue
source; reconciled literature search; every number regenerates; clean archive
verify; author approval). G Paper 3 submission (evidence graph reconciles;
generated tables; clean-room example; real archive; explicit licensing; clean-env
verification recorded). H full lateral-coupling/Paper 4 (only after feasibility
shows conservation + meaningful regime + distinguishable predictions + accessible
evidence).

## DO NOT DO NEXT

No G10 as primary track; no reimplementing Paper A's baseline comparison; don't
trust stale checkboxes over code/tests/manuscripts; no caller-assigned publication
status; no calling a manifest-only op an immutable freeze; no publishing
rehearsal-corpus pressure metrics; no treating irregular telemetry as independent
equally-weighted; no first-encountered-shot sensitivity; no optimizing away
controller lag in headline; no source/machine rankings with weak semantics; no
flow atlas before quantity kinds resolved; no calling a list of gate names an
evidence matrix; no one component-label standing for multiple claims; no Python
asserts as validation boundaries; no calling a file list a release bundle; no
quick/slow running the same suite; no registry breadth for count's sake; no
private Visualizer data in archives; no broadly reopening Paper A; no broadly
reopening B2; no large lateral-coupling model before operator/regime/prediction
defined.

## SINGLE-CHOICE RECOMMENDATION (this document)

Choose: **PUBLICATION-INTEGRITY AND RELEASE CONVERGENCE.** Main engineering work
= real freeze lifecycle + pressure-atlas estimand/inference upgrade. In parallel:
finish Paper A submission RC; build Paper 3's gate-level evidence graph + real
release archive. Treat the B2 APS abstract as the immediate bounded deadline
exception. Treat physical lateral coupling as the next major science opportunity,
card-first with a go/no-go phase.
