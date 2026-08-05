# I-040 — Waszkiewicz mixed-evidence audit

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

## What was run

An audit of every consumer of `waszkiewicz2025/traces_time_dependent`, attributing each to the
half of its mixed `validation_strength` cell that its assertion actually rests on.

**Question** (generated, verbatim from the candidate):

> For the 1 datasets whose validation_strength names both independent + post_fit +
> same_campaign, which of those strengths does each consuming gate actually rely on?

**The cell** (MANIFEST row 2, copied byte-identical, never paraphrased anywhere in this bundle):

```
independent within-rig (equilibrium) / post-fit (9-bar Q(t) reproduction)
```

**The caveat cell** (also verbatim — it carries the node convention and the circularity
disclosure that several consumers inherit):

```
soft circularity: m_d(t) from TDS x Q on same rig; 11-13 bar dip below monotone model; basket
vs line pressure both present (node id per RC-3/S5.9) | S5.9 nodes: basket_pressure__bar =
P_basket (basket gauge), pressure__bar = line/pump-side.
```

## How to re-run

```
python -m puckworks.analysis.screen_i040_evidence_halves
```

Writes `result.json` and `figures/primary.png`. Takes ~20 s, almost all of it the dynamic
trace.

Focused test: `pytest tests/test_screen_i040.py -v`

## Method — four layers, deliberately separable

A reviewer should be able to reject one layer without discarding the rest.

1. **Static enumeration.** An AST pass finds every call site of the loader
   `puckworks.data.waszkiewicz_traces`; a simple-name call-graph closure finds every `gate_*`
   that *could* reach one. It **over-approximates on purpose** — a shared function name links
   unrelated functions — because for a completeness check the safe error is a false positive,
   never a miss. Result: **21 call sites, 12 gates flagged**.
2. **Dynamic trace.** Every flagged gate is executed with the loader wrapped and the call count
   recorded. Result: **7 real gate consumers, 5 name-collision false positives**
   (`gate_coupled_kappa_t`, `gate_fasano_freeboundary`, `gate_lee_feedback_negative_result`,
   `gate_p3_schmieder_peak_discrimination`, `gate_unified_kappa_t` — all reach
   `waszkiewicz2025.poroelastic.published_calibration()`, which reads a **different** manifest
   row, `waszkiewicz2025/static_calibration`).
3. **Adversarial docstring scan.** Each real consumer's docstring is scanned for ROADMAP §0
   strength vocabulary. Any consumer resting on the post-fit half whose text contains
   "independent" is surfaced as a **candidate promotion** and must be cleared by reading.
4. **Human attribution.** Per consumer: columns read, pressure-node convention, the half its
   assertion depends on, the strength it states, and the reasoning — recorded per row so a
   reviewer can disagree with one row rather than the whole table.

Layer 2 is reconciled against layer 4: if the trace finds a consumer the table does not cover,
the screen returns `NEEDS_NEW_DATA` rather than a verdict. It is complete.

### Model execution

**One**, and it is the carve-out the candidate's method statement allows ("perform no model
execution unless strictly necessary to resolve a source-column path"): layer 2 executes the 12
statically flagged gates purely to observe whether they open the file. No result is fitted,
scored or read; the gate return values are discarded. Without it, five non-consumers would have
been attributed and one real consumer would have been missed.

## Strength ordering

ROADMAP §0, strongest first — a **promotion** is stating a strength strictly stronger than the
half the assertion rests on:

```
independent  >  post-fit reconstruction  >  verification  >  qualitative
```

## What the screen found

**7 gate consumers, 2 public claims, 18 producers/analyses/renderers — 27 in total, 0
promotions.** Detail in `decision.md`; numbers in `result.json`.

Three things worth carrying forward regardless of the verdict:

1. **A third category the cell does not anticipate.** `gate_ntube_kappa_t_union` reads
   `time__s` **only** — the dataset supplies a clock, and no measured column is scored against
   it. Neither manifest half is load-bearing. Found by the dynamic trace, not by reading.
2. **Two gates state no strength at all** (`gate_p2_kappa_ladder`,
   `gate_kappa_t_composition_diagnostic`). Their labels are carried downstream by PV-02 and
   PV-05. Not a promotion — but the split is preserved *downstream*, not at the gate.
3. **The claim layer already enforces the split at the strongest point.** PV-02's evidence
   selection names only `gate_waszkiewicz_dynamic_9bar` and records
   `"EXCLUDED: gate_waszkiewicz_static_refit, which concerns the steady-state pressure-flow
   curve and the recovered P_c/Q_c -- a different observable."` The independent-half gate is
   explicitly refused as evidence for the post-fit claim.

## Figure

`figures/primary.png` — asserting consumers grouped by the half they lean on, with the columns
they read, the strength they state, and the comparison.

**Note on the viz layer.** This figure is deliberately **not** registered in
`puckworks/viz/registry.py` / `docs/figures/viz/GALLERY.md`. That registry governs visuals that
depict a *mechanism* and binds each to a producer with a fidelity ceiling (ROADMAP §8). This
figure depicts **provenance bookkeeping** — which consumer leans on which manifest half — and
asserts nothing about physics, so it has no mechanism fidelity to ceiling. Registering it would
also mean extending a governed registry for a screen artifact, which the IF-5 decision forbids
before Wave 1 reports. It uses the house print palette (`puckworks.figures` tokens); the
categorical subset `#0072b2 / #e69f00 / #cc79a7` passes lightness-band, chroma, CVD-separation
and normal-vision checks on the light surface, and every mark carries a visible text label.

## Corpus warnings

**None of the 32 build warnings is load-bearing for this screen**, and none was repaired.
`docs/cards/waszkiewicz2025.md` resolves, carries no `TEMPLATE_DEVIATION`, and the manifest
row's `source_card` resolves. All 32 are deferred — see
[`../../IF5_HUMAN_TRIAGE_DECISION.md`](../../IF5_HUMAN_TRIAGE_DECISION.md) §7.

## Scope — what this screen did NOT do

- It did **not** re-adjudicate whether the manifest's own half-A label ("independent
  within-rig") is the right label for a refit that reproduces the source's own published static
  fit from the source's own equilibrium data. That is a question about the *cell*, not about
  which half a consumer leans on, and answering it is outside I-040's decision rule. Recorded
  in `decision.md` as a bounded observation with no verdict attached.
- It did **not** change, promote or restate any evidence label, badge, validation rung or model
  verdict. Nothing in the registry, the manifest, the cards or the claim records was edited.
- It did **not** run any candidate outside Wave 1, and did no novelty research.
