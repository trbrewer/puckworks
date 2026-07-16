# Paper 3 — per-claim evidence graph (spec)

This is the **hand-authored spec** for the Paper-3 evidence graph. It supersedes the
gate-name-only `generated/component_gate_matrix.csv`: that CSV lists, per component, only the
names of the gates wired to it. The evidence graph instead records, **per gate wiring**, the
specific claim, the observable compared, the source cards, the exact MANIFEST datasets with
their fit/eval roles, the independence of the evaluation, the honest per-gate evidence tier, a
caveat, and what the gate does **not** establish.

- **Source of truth (curate this):** `puckworks/paper3/EVIDENCE_LINKS.json`.
- **Engine + reconciler:** `puckworks/paper3/evidence_graph.py`.
- **Generated (never hand-edit):** `generated/evidence_graph_matrix.{csv,md}`,
  `generated/evidence_graph.json`, `generated/evidence_adjudication_queue.md`,
  `generated/evidence_conflicts.md`.

## Why a graph, not a matrix

A component can carry several gates, and a single gate can back several *distinct* claims (e.g.
`gate_kappa_t_degeneracy` asserts both a code-level model reduction **and** a same-rig flow
reconstruction — these are two links). Evidence strength is a property of the **claim a gate
checks**, not of the component as a whole. Rolling everything up to a component-level tier hides
exactly the distinctions Paper 3 needs to state honestly.

## Link schema

Each entry in `EVIDENCE_LINKS.json → links[]`:

| field | meaning |
|---|---|
| `link_id` | unique id; `<component>::<gate>` (with a `::suffix` when a gate splits) |
| `component` | exact registered component id (live registry) |
| `gate` | exact gate function name wired to that component |
| `card` | the component's own card stem, or `null` if none exists |
| `claim` | the specific scientific claim passing the gate demonstrates |
| `observable` | the physical quantity compared |
| `source_cards` | card stems supplying the data/physics |
| `dataset_ids` | exact MANIFEST dataset ids used (`[]` = uses none; `null` = not yet adjudicated) |
| `dataset_role` | per-dataset role: `fit` / `eval` / `both` / `reference` |
| `independence` | `independent` · `within_campaign_held_out` · `post_fit_reconstruction` · `code_verification` · `not_empirical` |
| `evidence_strength` | the **per-gate adjudicated** tier (registry `EVIDENCE_STRENGTHS` enum) |
| `component_evidence_strength` | the component's own declared tier — **context only, never a verdict** |
| `caveat` | the key limitation a reader must know |
| `claim_not_supported` | what a reader might wrongly infer that the gate does not establish |
| `conflict_note` | a documented tension this link records (feeds the conflicts report), else `null` |
| `adjudication_status` | `ADJUDICATED` or `NEEDS_ADJUDICATION` |

`dataset_ids: []` (gate loads no dataset) is a **different state** from `dataset_ids: null`
(not yet adjudicated). Drafts leave every curated field `null`.

## Integrity rules (enforced by `reconcile()`)

- **Bijection with the live registry:** every `(component, gate)` wiring has ≥1 link, and every
  link points at a real wiring, real dataset ids, and real card stems.
- **No inferred promotion:** the bootstrap emits only `NEEDS_ADJUDICATION` drafts with
  `evidence_strength = null`. A tier is set **only** by a human adjudication. The component's
  declared tier is carried separately as `component_evidence_strength` and is never inherited.
- **Vocabulary guards** (the two labelling errors this project bans):
  - a `code_verification`/conservation check may not be called empirical — its `independence`
    must be `code_verification` or `not_empirical`;
  - `source_curve_reproduction` may not be labelled `independent`;
  - a `post_fit_reconstruction` may not be tiered `controlled_independent`/`within_campaign_held_out`;
  - `controlled_independent` requires `independence = independent`.

## Draft vs strict CI modes

- **draft** (`--reconcile`, wired into the generated-artifacts lane now): structural validity +
  bijection + completeness/guards for the *adjudicated* links. `NEEDS_ADJUDICATION` links are
  allowed — the graph is prefilled conservatively and adjudicated incrementally.
- **strict** (`--reconcile --strict`): additionally requires **zero** `NEEDS_ADJUDICATION`.
  Fails today (33 drafts remain); flip the blocking lane to strict once the queue is empty.

## Adjudicating a draft

1. Pick a gate from `generated/evidence_adjudication_queue.md`.
2. Read the gate body in `puckworks/validation/gates.py`; follow its data loaders to the exact
   MANIFEST `dataset_id`s; read the component's card. **Do not infer from the component name.**
3. Fill `claim, observable, source_cards, dataset_ids (+ dataset_role), independence,
   evidence_strength, caveat, claim_not_supported` in `EVIDENCE_LINKS.json`; set
   `adjudication_status = "ADJUDICATED"`. Choose the **most conservative tier that is true**.
4. `python -m puckworks.paper3.evidence_graph --reconcile` then `--write`; commit the JSON and
   the regenerated artifacts together.

## Regenerate / check

```
python -m puckworks.paper3.evidence_graph --reconcile          # validate (draft mode)
python -m puckworks.paper3.evidence_graph --reconcile --strict  # require full adjudication
python -m puckworks.paper3.evidence_graph --bootstrap           # print draft skeletons
python -m puckworks.paper3.evidence_graph --write               # regenerate artifacts
python -m puckworks.paper3.evidence_graph --verify              # fail on stale artifacts
```

## Status of this draft (initial landing)

49 links (48 registry wirings + the `gate_kappa_t_degeneracy` split). **16 adjudicated, 33
awaiting adjudication.** The 16 were curated from the gate bodies and cards, choosing the most
conservative true tier. Notable findings surfaced by the first pass, recorded in
`generated/evidence_conflicts.md`:

- **`gate_infiltration_triangle`** is the registry's only `controlled_independent` component,
  but at the gate level its evidence is `sign_or_compatibility`: the permeability comes from a κ
  fitted to the *same* DE1 shot and the front is driven by that shot's own pressure trace, so
  the match is a wide-bracket compatibility check on in-sample data, not a parameter-free
  independent prediction. The graph records `sign_or_compatibility`; the registry component tier
  is left untouched (any promotion/demotion is a separate ROADMAP §7.1 change).
- The two **G10** viscosity gates encode a real inter-source tension: the reference envelope
  (~1.3–1.9× water) vs the Telis-Romero-2001 closure (~1.06× at bulk shot TDS), and a bounded
  ~+37% khomyakov-vs-TR2001 offset over the measured overlap.
- The **c_sat** constant (212.4 / 224 / 170 kg m⁻³) is surfaced, not merged, per ROADMAP §5.4.
