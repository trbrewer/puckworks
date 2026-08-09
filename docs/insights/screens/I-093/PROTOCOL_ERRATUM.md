# I-093 — protocol erratum

**Dated 2026-08-08.** Raised after cheap-screen execution, on inspecting the registry text
verbatim. Recorded here **because [`PROTOCOL.md`](PROTOCOL.md) is preserved byte-for-byte**: it is
the frozen record, [`result.json`](result.json) binds its SHA-256, and editing it would both break
that binding and make the error look anticipated.

## The protocol language that was wrong

`PROTOCOL.md` §6b states:

> The pack card's declared box guidance is **≥ 5 grain diameters**; L = 100 is the smallest swept
> size that reaches it.

and §6a refers to the grain-radius floor as coming from "the pack card". `decision.md` and
`README.md` inherited the same characterisation.

## What the repository actually says

The declared range of `brewer2026.pack_generator`, verbatim from the registry:

```
grain radius >= 10 voxels; columns >= 5 grain diameters for sigma
```

Two corrections follow:

1. **The five-grain-diameter condition is scoped to `sigma`** — the columnar heterogeneity field —
   **not to permeability.** It is a box-size condition for resolving σ, and this screen repurposed
   it as a permeability-representativeness guidance, which it is not.
2. **There is no pack card.** No `docs/cards/` file describes `brewer2026.pack_generator`; the
   declared range lives only in the registry entry. Every reference in this bundle to "the pack
   card" is therefore wrong on its face.

**The repository has never claimed that five grain diameters is sufficient for permeability.**

## Consequences

**No repository correction is warranted, and none is made.** This screen contradicts no existing
repository statement. In particular:

- **no pack-card correction** (there is no pack card);
- **no registry correction** (`grain radius >= 10 voxels; columns >= 5 grain diameters for sigma`
  is accurate as written and correctly scoped);
- no card, manifest, gate or evidence surface is touched.

**Unaffected by this erratum:**

- the numerical metric and its frozen threshold;
- the executed run matrix and every measured value;
- the frozen decision rule and the historical **SURVIVE** decision, which was applied as written;
- the SHA-256 binding of `PROTOCOL.md` in `result.json`.

**Execution does not need to restart.** The error is one of *characterisation*, not of scenario,
parameter, threshold or measurement. The box sizes swept, the criterion applied and the numbers
obtained are all exactly what the protocol specified.

## The corrected reading

The cheap screen is a **first repository-bound measurement for the tested generator/solver pair**:
permeability had not stabilised by L/d = 5.0 under the frozen criterion, for
`brewer2026.pack_generator` + `brewer2026.lb_reference` at R = 310.8 µm and φ ≈ 0.49.

It is **not** a finding against repository guidance, because no such guidance existed for this
observable. Reaching 5.0 grain diameters is not reaching a declared permeability threshold, so the
SURVIVE-versus-INCONCLUSIVE boundary drawn in the cheap screen rests on a figure with **no
repository-declared anchor for permeability**. That does not change the decision — the frozen rule
was applied as written — but it does change what the decision means, and this bundle now says so
throughout.

## Consistency

[`decision.md`](decision.md) and [`README.md`](README.md) carry the same correction and have had
the "pack card guidance" characterisation removed from their body text (it survives only where
quoted as the error). [`NOVELTY_REVIEW.md`](NOVELTY_REVIEW.md) records the same scoping fact.
