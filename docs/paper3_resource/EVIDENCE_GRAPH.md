# Paper 3 — per-claim evidence graph (spec, schema v2)

Hand-authored spec for the Paper-3 evidence graph. It supersedes the gate-name-only
`generated/component_gate_matrix.csv` and records, **per gate wiring**, a typed claim with its
provenance, scope, and the honest fit/evaluation relationship — enough for **fail-closed, scoped
Paper-3 release validation** without forcing every unrelated or future gate to be empirically
resolved.

- **Source of truth (curate this):** `puckworks/paper3/EVIDENCE_LINKS.json` (schema v2).
- **Engine + reconciler:** `puckworks/paper3/evidence_graph.py`.
- **Generated (never hand-edit):** `generated/evidence_graph_matrix.{csv,md}`,
  `generated/evidence_graph.json`, `generated/evidence_graph_summary.json`,
  `generated/paper3_priority_evidence_matrix.md`, `generated/evidence_adjudication_queue.md`,
  `generated/evidence_conflicts.md`.

## Link schema (v2)

Core: `link_id`, `claim_id`, `component`, `gate`, `card`, `claim`, `observable`, `caveat`,
`claim_not_supported`, `conflict_note`, `adjudication_status`.

Scope + provenance (v2 additions):

| field | values | meaning |
|---|---|---|
| `claim_owner` | `paper3` · `paper_b2` · `paper_a` · `paper4_future` · `project_only` | which paper/effort asserts the claim |
| `paper3_use` | `primary_claim` · `method_demonstration` · `resource_context` · `cited_science` · `not_in_scope` | how Paper 3 uses it |
| `reality_facing` | bool | does the claim assert something about physical reality (vs a code/math property) |
| `support_status` | `admissible` · `context_only` · `unsupported` · `blocked_missing` · `proposed_not_run` · `needs_adjudication` | the honest state of support |
| `evidence_strength` | registry `EVIDENCE_STRENGTHS` | the **per-gate adjudicated** tier |
| `component_evidence_strength` | registry value | the component's declared tier — **context only, must equal the live registry** |
| `relationship` | `independent_external` · `within_campaign_held_out` · `same_campaign_not_held_out` · `post_fit_same_data` · `code_verification` · `not_empirical` | the honest fit/evaluation relationship (authoritative for the guards) |
| `sources[]` | list | typed provenance (below) |

Each `sources[]` entry: `source_card` (a card stem **or** a MANIFEST-declared provenance string),
`dataset_manifest_ids` (exact MANIFEST ids), `dataset_status`
(`resolved_manifest` · `not_applicable_code` · `not_applicable_source_equation` ·
`not_applicable_synthetic` · `proposed_experiment` · `blocked_missing` · `needs_adjudication`),
`evidence_role` (`fit` · `eval` · `reference` · `context`), `independence`, `note`.

An **empty dataset list never silently stands for all of those states** — the `dataset_status`
names which one, and a `resolved_manifest` source must actually carry ids.

## Integrity rules (enforced by `reconcile()`)

- **Bijection** with the live registry wirings.
- **No inferred promotion:** the bootstrap emits only `NEEDS_ADJUDICATION` drafts with null
  verdicts. A tier/relationship/scope is set only by a human `ADJUDICATED` flip with every field
  filled and **no placeholder values**.
- **Stored component tier must equal the live registry** value (no stale context).
- **Provenance from the MANIFEST, never from a name prefix** — `sources[].source_card` is the
  dataset's declared MANIFEST provenance.
- **Mechanical guards** (reconciliation fails when):
  - fit and eval dataset ids overlap but `relationship` is `independent_external` or
    `within_campaign_held_out`;
  - `evidence_strength=controlled_independent` with no independent evaluation source;
  - `evidence_strength=within_campaign_held_out` with no held-out evaluation source/relationship;
  - `evidence_strength=code_verification` used empirically (relationship not code/not-empirical);
  - `source_curve_reproduction` labelled `independent_external`;
  - a `post_fit_same_data` relationship carrying a top tier;
  - a stored component tier differing from the live registry;
  - an `ADJUDICATED` link containing a placeholder;
  - an in-scope asserted Paper-3 claim with no admissible evidence.

## Strict modes

- **draft** (`--reconcile`): structural validity + bijection + adjudicated-completeness + the
  mechanical guards. Drafts allowed. This is the ordinary-PR check.
- **`--strict --scope paper3`** (release gate): additionally fail-closed on the **asserted**
  Paper-3 claims (`claim_owner=paper3`, `paper3_use ∈ {primary_claim, method_demonstration}`) —
  each must be adjudicated, `admissible`, carry a caveat + `claim_not_supported`, and have
  resolved provenance. It does **not** fail for honestly out-of-scope / future / project-only /
  resource-context gates. Runs in `paper3-evidence.yml` (not yet a *required* branch check —
  make it required once PR C lands and it is green on main).
- **`--strict --scope all`**: additionally require the WHOLE graph adjudicated. Manual
  (`workflow_dispatch`) only; stays non-blocking until the full queue is reviewed.

## Packaging / release decision — **Option A (source-tree tooling)**

The reconciler reads `docs/cards/` (card stems) and writes generated artifacts under
`docs/paper3_resource/generated/`; neither path ships in the wheel. The evidence graph is
therefore **source-tree release tooling**, by decision:

- evidence reconciliation (`--reconcile [--strict --scope paper3]`) runs **before packaging**,
  from a source checkout, and the generated evidence outputs are bundled with the release;
- the command is **not** an installed-wheel feature and must not be invoked from an installed
  package without the repository present. `EVIDENCE_LINKS.json` lives inside the package
  (`puckworks/paper3/`) but the card/generated paths it needs do not — this is documented here as
  an intentional source-tree-only dependency, not an accidental missing-file bug.

## CI integration

- **Ordinary PR CI** (`generated-artifacts.yml`, required `verify-generated`): live-gate coverage
  (quick lanes), schema/reference reconciliation (`--reconcile`), draft-state consistency, and
  generated-artifact freshness (`--verify`).
- **Paper-3 build/release** (`paper3-evidence.yml`): `--strict --scope paper3`.
- **Manual/scheduled** (`paper3-evidence.yml`, `workflow_dispatch`): `--strict --scope all`.

Global strict (`--scope all`) is deliberately **not** a required branch check.

## Adjudicating a draft

1. Pick a gate from `generated/evidence_adjudication_queue.md`.
2. Read the gate body in `puckworks/validation/gates.py`; follow its loaders to the exact
   MANIFEST `dataset_id`s; read the card. Attribute each dataset to its **MANIFEST source_card**.
3. Fill the v2 fields in `EVIDENCE_LINKS.json`; choose the **most conservative tier and
   relationship that are true**; set `adjudication_status = "ADJUDICATED"`.
4. `--reconcile` (and, for a Paper-3 claim, `--reconcile --strict --scope paper3`), then
   `--write`; commit the JSON and regenerated artifacts together.

## Status (v2 landing)

49 links (48 wirings + the `gate_kappa_t_degeneracy` split). **16 adjudicated, 33 awaiting.**
`--strict --scope paper3` is **green** (every asserted Paper-3 claim is admissible). Semantic
corrections applied in this version:

- **`gate_infiltration_triangle`** — the same DE1 fixture supplies calibration and evaluation, so
  the relationship is `same_campaign_not_held_out` (not `within_campaign_held_out`); the gate tier
  is `sign_or_compatibility`, while the registry component tier (`controlled_independent`) is
  carried untouched as context and the discrepancy is surfaced in the conflicts report. A
  component→gate roll-up policy is a separate decision; until it is adopted, **gate-level evidence
  is authoritative** for public/release claims.
- **`gate_kappa_t_composition_diagnostic`** — reclassified from `code_verification` to
  `exploratory_synthesis` with `post_fit_same_data` (a residual-based diagnostic, not pure code).
- **`gate_waszkiewicz_static_refit`** — tier and relationship aligned to
  `post_fit_reconstruction` / `post_fit_same_data`.

The two **G10** viscosity gates and the **c_sat** 212.4/224/170 constant remain surfaced in
`evidence_conflicts.md`.
