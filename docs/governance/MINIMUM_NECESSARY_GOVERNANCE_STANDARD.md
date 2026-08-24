# Minimum Necessary Governance Standard for Scientific Model Development

**Policy ID:** SCI-GOV-001  
**Status:** Owner-approved for adoption; controlling once merged  
**Effective date:** 2026-08-24  
**Applies to:** `trbrewer/puckworks`, `trbrewer/espresso-whole-pull`, and cross-repository scientific-model-development work

## 1. Purpose

This standard keeps governance proportional to the scientific and engineering risk being controlled.

Governance exists to protect:

1. production solver and governing-physics correctness;
2. the truthfulness of scientific claims;
3. training/holdout separation and freedom from post-holdout retuning;
4. source rights, provenance, units, and reproducibility;
5. reliable protected merges.

Governance is not an independent project objective. A control that does not materially protect one of the five items above is advisory or ordinary engineering practice, not a mandatory scientific gate.

The default is the least burdensome process that still protects the claim being made.

## 2. Core rules

1. **Risk, not ceremony, determines the controls.**
2. **Scientific validity, software correctness, QA health, and CI infrastructure status are separate dispositions.**
3. **A failure is classified by what actually failed, not by the name of the workflow that reported it.**
4. **Historical evidence is preserved, but preservation does not require a new stage, branch, issue, or review ladder.**
5. **Corrections remain in the same lane unless the scientific decision surface or production behavior changes materially.**
6. **Unchanged evidence may be reused by exact commit, tree, file, artifact, and executable hashes.**
7. **Only affected evidence is rerun after a bounded nonsemantic correction.**
8. **One scientific stage normally uses one issue and one pull request per repository.**
9. **A stricter control must identify the risk it protects, its scope, and when it expires.**
10. **Stage-specific controls expire at stage close unless this or another enduring owner policy says otherwise.**

## 3. Governance classes

Every new task must declare one class before work begins.

### G0 — Ordinary engineering, documentation, tests, QA, and CI

Use G0 when the change does not alter:

- production solver behavior;
- governing equations;
- scientific parameters or thresholds;
- accepted source data;
- the training/holdout decision surface;
- a frozen prediction bundle.

Required controls:

- normal branch and pull request;
- relevant tests and static checks;
- required CI;
- ordinary review where repository protection requires it.

Not required by default:

- a new scientific stage or attempt identifier;
- a new scientific issue;
- a frozen mathematical contract;
- an independent scientific review;
- replay of unaffected numerical experiments;
- a correction or adjudication ladder.

Examples include documentation fixes, test-marker corrections, QA harness changes, CI timeout corrections, manifest regeneration, and warning cleanup.

### G1 — Data contracts, parameterization, calibration, and pre-holdout freeze

Use G1 when scientific inputs, parameters, fitting rules, observation operators, numerical application settings, or holdout cases are being selected without changing production governing physics.

Required controls:

- explicit training/holdout separation;
- frozen source identities, units, parameter scope, objective, thresholds, and numerical gates;
- target-blind parameterization;
- deterministic artifacts;
- one exact pre-scoring freeze;
- one independent pre-scoring audit;
- no post-score retuning.

Automated isolated integrity tests may read protected data if they are silent and cannot influence parameterization, selection, or human judgment.

A silent integrity read is QA activity, not scientific target access.

### G2 — Production solver, governing physics, or numerical-method change

Use G2 when production equations, state variables, coupling, boundary meaning, or materially relevant numerical behavior changes.

Required controls:

- frozen mathematical and compatibility contract;
- focused analytical or manufactured verification;
- conservation, boundedness, determinism, mesh, timestep, and parallel checks where applicable;
- unchanged-baseline comparison;
- one exact-head independent review;
- protected merge.

This is the highest routine development-control level. Additional review rounds require an identified unresolved scientific or production-safety risk.

### G3 — Protected holdout prediction and scoring

Use G3 when the frozen model is finally evaluated against protected target values.

Required controls:

1. verify the exact model, parameter, case, executable, and threshold hashes;
2. generate all predictions without target access;
3. freeze and hash the immutable prediction bundle;
4. invoke the protected scorer once;
5. report all predeclared metrics;
6. prohibit retuning under the holdout claim.

A later revised model may use the former holdout only by explicitly reclassifying it as training or comparison data.

## 4. Material holdout breach is defined by information flow

A material holdout breach occurs when protected target content reaches any of the following before the immutable prediction freeze:

- parameter fitting;
- model or species selection;
- hydraulic mapping;
- observation-operator selection;
- mesh or timestep selection;
- acceptance-threshold selection;
- human scientific judgment;
- an agent’s scientific decision context;
- post-result retuning.

The following are not, by themselves, material scientific contamination:

- an isolated, silent integrity test reading protected bytes;
- schema, hash, row-count, unit, or transcription checks that expose no values;
- public or pre-existing exposure already declared in the data contract;
- a test or CI process returning only pass/fail without target-derived details;
- a protected file open that cannot affect the scientific decision surface.

Unauthorized or mistimed automated reads may still be recorded as QA or process deviations. They invalidate scientific work only if target information could have influenced a scientific decision.

## 5. Failure taxonomy

Every stop must use one primary category.

### Scientific failure

Examples:

- a physical hypothesis fails;
- a predictive gate fails;
- a required trend is wrong;
- parameterization lacks predictive content;
- identifiability fails;
- numerical application uncertainty exceeds the frozen limit.

Effect: the scientific claim or next scientific stage is blocked.

### Production software or numerical defect

Examples:

- conservation failure;
- changed hydraulic behavior;
- nonnegative-state failure;
- incorrect equation implementation;
- serial/MPI inconsistency;
- invalid boundary behavior.

Effect: production merge is blocked until corrected and reverified.

### Data, rights, or provenance failure

Examples:

- incompatible units or mass bases;
- unverified source identity;
- unresolved rights;
- training/holdout separation cannot be established.

Effect: the affected scientific use is blocked.

### QA or infrastructure failure

Examples:

- test-harness defect;
- unmarked test;
- manifest drift;
- CI timeout;
- cancelled workflow;
- runner-capacity failure;
- artifact-upload failure;
- nondeterministic framework output unrelated to science.

Effect: preserve the failed run, correct the infrastructure in the same lane, rerun affected checks, and continue. It is not a scientific failure.

### Process deviation without material information flow

Examples:

- a valid test ran before the preferred lifecycle point;
- a review was attempted before all optional checks completed;
- a silent protected-data integrity read occurred outside the preferred QA phase.

Effect: record the deviation and assess materiality. Continue in the same lane when the scientific decision surface was unchanged.

## 6. Correction and escalation rules

1. A G0 defect is corrected on the same branch and pull request.
2. A G1 or G2 correction stays in the same scientific stage unless it changes:
   - governing physics;
   - the frozen parameterization method;
   - the holdout decision surface;
   - accepted target-informed choices;
   - the primary scientific result.
3. A documentation, test, QA, or CI correction does not create a new scientific attempt.
4. A failed run remains in logs or evidence; it does not require a separate committed evidence hierarchy unless it changes a scientific conclusion.
5. An exact candidate is invalidated only by a semantic change relevant to the reviewed evidence.
6. A reviewer may issue a bounded addendum for a CI-only or documentation-only delta when scientific hashes are unchanged.
7. After **two consecutive non-scientific stops**, no further correction round may be created automatically. The owner must consolidate the lane, remove unnecessary controls, and authorize one bounded completion.
8. No process may create governance to govern newly created governance unless a demonstrated risk remains uncontrolled.

## 7. Evidence reuse and rerun scope

Evidence may be reused when the relevant identities are unchanged, including:

- source commit and tree;
- scientific subtree tree;
- data bundle hash;
- solver source hash;
- executable hash;
- case/configuration hash;
- prediction or verification artifact hash.

After a bounded change:

- rerun tests that can be affected by the changed paths;
- rerun required repository CI;
- do not replay expensive numerical work whose inputs, executable, and relevant code hashes are unchanged;
- do not repeat an independent scientific review of unchanged scientific evidence;
- review only the delta plus the unchanged-hash proof.

A full replay is required only when the changed path can alter the scientific result, production behavior, or protected decision surface.

## 8. CI and workflow policy

Required branch-protection checks must ultimately complete successfully before merge. This requirement does not make every timeout or cancellation a scientific failure.

### Classification

- assertion/test failure: `SOFTWARE_OR_QA_FAILURE`;
- fixed-timeout expiration: `CI_INFRASTRUCTURE_INCOMPLETE`;
- concurrency cancellation or superseded run: `CI_RUN_SUPERSEDED`;
- runner outage or artifact-service failure: `CI_EXTERNAL_INFRASTRUCTURE_FAILURE`.

### Response

1. Rerun a cancelled or timed-out job once on the exact same head.
2. Do not create a semantic commit solely to trigger CI.
3. If the same job repeatedly reaches its budget, correct the job scope or structure in the same pull request or a normal G0 infrastructure pull request.
4. Prefer narrowing instrumentation, splitting independent jobs, caching, or selecting the tests that supply the required signal.
5. Do not repeatedly raise timeouts without addressing the cause.
6. A CI-only correction does not invalidate scientific evidence whose hashes remain unchanged.
7. Independent review may remain scientifically valid while merge waits for final CI completion.
8. Dashboard labels such as “failed,” “cancelled,” or “unstable” must be translated into the taxonomy above before a scientific disposition is assigned.

## 9. Independent review policy

One independent exact-head review is normally required for:

- G2 production solver or physics changes;
- the final G1 pre-holdout freeze;
- the immutable G3 prediction/scoring result when required by the programme.

Independent scientific review is not normally required for G0 changes.

When an exact candidate changes only in G0 paths:

- prove the scientific subtree and artifacts are unchanged;
- review the G0 delta;
- rerun affected checks and required CI;
- issue one review addendum;
- do not rerun the full scientific review.

## 10. Authorization format

Future authorizations should normally contain only:

1. objective;
2. governance class;
3. allowed and forbidden scientific scope;
4. decision surface being frozen;
5. required gates;
6. material stop conditions;
7. evidence eligible for reuse;
8. result classes;
9. next action.

Historical commits, hashes, and results should be referenced through existing artifacts rather than restated in full unless they are needed to prevent ambiguity.

An authorization should not restate normal repository commands, protection rules, or this policy unless an exception is being made.

## 11. Governance circuit breakers

Pause and simplify governance before continuing when any of the following occurs:

- two consecutive stops are QA, CI, or lifecycle-only;
- governance work exceeds the scientific implementation effort;
- a new stage is proposed without a changed scientific question;
- a failure class cannot be tied to a changed claim or uncontrolled risk;
- an unchanged scientific artifact is being repeatedly re-reviewed;
- a CI timeout is being reported as a model failure;
- agents are building test infrastructure primarily to validate other test infrastructure.

The owner’s consolidation decision should remove controls, not add another layer, unless a specific material risk remains.

## 12. Application to SCI-MD-004

For SCI-MD-004:

- Stage C solver implementation was **G2** and appropriately required full numerical verification and independent review. The verified indexed solver is complete.
- Stage E0 parameterization and case freeze is **G1**.
- Protected-target integrity-test infrastructure is **G0**.
- The eventual Angeloni prediction and scoring operation is **G3**.

Therefore:

- target-integrity QA defects remain in the same Stage E0 lane;
- silent automated integrity reads are not scientific contamination;
- cancelled or timed-out CI is infrastructure incomplete, not a parameterization failure;
- unchanged scientific bundles and subtrees remain reusable by hash;
- no further Stage E0 correction ladder is permitted for documentation, test, QA, review-administration, or CI-only defects;
- Stage E0 stops scientifically only for a real data-contract, mapping, predictive-content, identifiability, numerical-application, conditional-hydraulic, holdout-information-flow, or production-change failure.

## 13. Exceptions and precedence

This policy is the default owner standard for future work.

A future authorization may impose stricter controls only when it states:

- the specific additional risk;
- why this policy does not control it;
- the extra control being imposed;
- the artifact or claim it protects;
- the event at which the extra control expires.

In the absence of that explicit exception, this standard prevails over inherited stage-specific ceremony.

This policy does not waive legal obligations, source-license restrictions, branch protection, or truthful reporting.
