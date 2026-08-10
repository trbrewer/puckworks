# RP-D lateral cross-model programme — bounded activation

```
CROSS_MODEL_NUMERICAL_VERIFICATION
DETERMINISTIC_SYNTHETIC_GEOMETRY
NOT_EXPERIMENTAL_VALIDATION
NOT_A_REGISTRY_STATUS_PROMOTION
NOT_A_PUBLICATION_RESULT_YET
```

**This document defines a staged sequence. It executes none of it beyond Stage A, and Stage A is
the only stage authorized in this branch.** ROADMAP §9 keeps RP-D as a scheduled backlog
programme; this file records the one bounded slice that human authorization activated, and why.

## 0. Why this slice, and why now

`WP6-LC-IDENT` (2026-08-09, `docs/insights/screens/WP6-LC-IDENT/`) established **structural
identifiability**: in the isoresistive-mirror two-path design the map
`(c, Ξ) → (R, s)` is one-to-one and has an exact closed-form inverse, verified against
`model1_two_path` to ~1e-11. That result is entirely *internal* to the two-node network — the
inverse was tested against the same algebra that generated its inputs.

That leaves one sharp, cheap, decisive question, and it is the reason this slice was selected
rather than any other RP-D stage:

> **Is Ξ a coarse-grained physical quantity, or only a parameter of the two-node network?**

Nothing in the repository answers it. A spatially resolved solver that was implemented
independently of `model1_two_path` — `brewer2026.lb_reference`, a D3Q19 TRT Stokes kernel with no
knowledge of nodes, contrasts or Ξ — can generate the ground truth. If the boundary inverse
recovers an independently field-derived effective Ξ from that solver's fixture, Ξ has survived a
test it could have failed. If it does not, that is a bounded negative result about the reduction,
obtained before any apparatus is built.

The screen's own `DECISIVE_EXPERIMENT.md` specifies a **physical** two-lane fixture. This
programme is the **virtual** rehearsal of it. It cannot substitute for the experiment and does not
close the card's box 5; it reduces the risk of building the wrong apparatus.

## 1. What this programme is NOT

- Not an Insight Foundry screen. No `I-` number is minted, no candidate is added, no lens, no
  generator, no scoring, no change to `ID_REGISTRY.json`. It lives under `docs/analysis/`, not
  `docs/insights/screens/`.
- Not an activation of RP-D at large. Explicitly **out of scope in every stage below**: passive
  scalar transport, dissolution, multiple species, wetting or two-phase flow, swelling or
  deformation, fines transport or clogging, temperature coupling, extraction clocks, random
  pore-pack ensembles, XCT-conditioned morphology, basket-scale cup-output coupling, N-path
  lateral-coupling models, and Paper 4 manuscript work.
- Not a new registered component. `brewer2026.lb_reference` gains **additive diagnostic
  instrumentation only** (an optional macroscopic-field export); its default API, its numerics and
  every existing gate are unchanged. A genuinely new reusable solver would require a card, a
  registry entry and a gate first (CLAUDE.md rule 1) and is not attempted.
- Not an experiment. Every result surface carries the claim ceiling in §4.

## 2. Activated scope

Exactly three things are activated, and only inside Stage A:

| RP-D element | activated portion |
|---|---|
| **Stage 0** — scope, contracts, cards, V&V matrix, claim ceiling | in full, for this question only |
| **Stage 1** — general geometry & boundary infrastructure | **only** the minimum this fixture needs: valid inlet/outlet topology, boundary-flow measurement, and conservation/pressure instrumentation. Non-cubic domains already work in the reference kernel; a new pressure-boundary mode is added only if the topology adjudication demands it |
| **Stage 2** — verified 3D hydraulics | **one** deterministic hydraulic pilot: the two-lane mirror fixture |

Stages 3–6 of ROADMAP §9 RP-D remain unactivated.

## 3. Staged sequence (defined, not executed)

Only **Stage A** is authorized. Each later stage needs its own human authorization and its own
entry condition; documenting a stage does not start it.

### Stage A — RP-D-LC-001: deterministic virtual fixture and cross-model recovery *(AUTHORIZED)*

Bundle: `docs/analysis/rp_d_lc_001/`.

A deliberately simple, exactly mirror-symmetric voxel fixture — common plenum, two axial lanes of
differing segment order, a blockable lateral bridge — solved by the existing LB kernel. Truth is
constructed two independent ways (calibrated coupons; in-situ field coarse-graining) and neither
may call the WP6 inverse. The inverse sees only `Q0, ΔP0, q1, q2, ΔP`. Disposition per the frozen
rule in `rp_d_lc_001/PROTOCOL.md` §12.

**Entry condition (met):** WP6-LC-IDENT merged; a verified inverse exists to import.

### Stage B — RP-D-LC-002: deterministic porous-segment fixtures and controlled morphology

Replace the smooth slot segments with *deterministic* porous media (regular sphere or pillar
arrays at controlled solid fraction) while keeping the fixture topology and the anti-circularity
contract from Stage A. Asks whether the Stage-A conclusion survives when the axial elements are
Darcy media with a tortuous internal structure rather than analytic ducts, and whether Ξ still
coarse-grains when the "node" is a genuine porous cross-section.

**Entry condition:** Stage A returns `CROSS_MODEL_RECOVERY` or `MECHANISM_ONLY`, **and** the
Stage-A pressure-nonuniformity diagnostics show a two-node coarse-graining is defensible.
Deterministic morphology only — no seeded ensembles.

### Stage C — RP-D-LC-003: seeded synthetic-pack ensembles, transfer and failure boundaries

Seeded random packs (`brewer2026.pack_generator` class geometry), ensembles over realizations, and
a deliberate search for the boundaries where the reduced inverse stops working: contrast range, Ξ
range, lane-length-to-width ratio, distributed vs localized lateral exchange. The first stage in
which a *statistical* statement is possible, and the first that needs the ensemble machinery
Stage A explicitly forbids.

**Entry condition:** Stage B complete with its own disposition; a predeclared ensemble size and a
predeclared failure-boundary definition.

### Stage D — RP-D-LC-004: experiment optimisation and physical-apparatus handoff

Use the Stage A–C map of where the inverse is quantitatively useful to optimise the *physical*
fixture of `DECISIVE_EXPERIMENT.md`: choose lane geometry and bridge aperture that place Ξ in the
useful window with margin on the cross-product gap `X`, and quantify how much of the required ~1 %
reproducibility is spent on construction tolerance. Hands a design, not a result, to TB.

**Entry condition:** Stage C failure boundaries known; an instrument/noise model supplied from
outside the repository (none exists today — this is the same gap that keeps card box 5 OPEN).

## 4. Claim ceiling for every stage

- deterministic synthetic geometry; single-phase steady creeping flow;
- **cross-model numerical verification only** — never experimental validation;
- no real coffee morphology, no real-puck Ξ, no transverse coffee permeability estimate;
- no evidence that espresso occupies any Ξ regime;
- no apparatus precision established;
- no evidence-rung or registry-status promotion;
- no claim of a validated espresso digital twin;
- `docs/cards/lateral_coupling_feasibility.md` **box 5 remains OPEN** and **box 6 remains closed
  on its existing mathematical result**; **Paper 4 remains unauthorized**.

Always write "the effective Ξ of the virtual fixture", never "the Ξ of an espresso puck". A
successful simulation does not close the accessible-experiment box; it only reduces the risk and
sharpens the design of that future experiment.

## 5. Compute guardrail

Heavy LB execution stays in `puckworks/validation/slow/` or local/Colab runs, never in normal CI
(CLAUDE.md rule 3). CI-side work is limited to geometry construction, observable arithmetic,
schema validation and deterministic bundle regeneration from committed compact scalar records.
