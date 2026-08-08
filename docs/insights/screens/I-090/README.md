# I-090 — can `first_drip_time` discriminate between the models that predict it?

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

**Decision: `RETIRE`** — not a rival pair. **Replicates would not have rescued it.**

## What was run

```
python -m puckworks.analysis.screen_i090_first_drip
```

Writes [`result.json`](result.json) and [`figures/primary.png`](figures/primary.png). The run is
deterministic: no RNG, no wall-clock, no network. Running it twice from clean inputs produces a
byte-identical `result.json` (asserted by `tests/test_screen_i090.py`).

```
python -m pytest tests/test_screen_i090.py -q
```

## Bundle

| file | what it is |
|---|---|
| [`PROTOCOL.md`](PROTOCOL.md) | frozen **before** the screen module existed, in its own commit |
| [`decision.md`](decision.md) | the decision record, blueprint Appendix C shape |
| [`result.json`](result.json) | machine-readable, hash-bound to the protocol and every input |
| [`figures/primary.png`](figures/primary.png) | the primary figure |

## The short version

The candidate expected `NEEDS_NEW_DATA` plus a costed replicate request. It gets `RETIRE`,
because the comparison turns out to be ill-posed **upstream** of the uncertainty question.

`foster2025.infiltration` and `foster2025.machine_mode` are **not rivals**. They are sequential
stages of one pipeline — `machine_mode` (stage `machine`) *generates* the pressure history that
`infiltration` (stage `infiltration`) *consumes* — and they bind to the **same card**, whose
Interface mapping says *"anything listed above is attributed to both."* The tension row's "2
registered models name `first_drip_time`" is one Outputs clause counted twice.

They also share one front law, `φ_T s ds/dt = (k/μ) ΔP`. Fed `machine_mode`'s own implied bed-top
pressure, `infiltration`'s public closed form reproduces `machine_mode`'s front to **RMSE
7.0 × 10⁻⁸ mm** on a 9.975 mm bed — and the residual **falls under grid refinement**, which is
what identifies it as quadrature error rather than a physical difference. So the two can differ
only through the pressure history supplied: a boundary condition, not a mechanism.

Separately, three different events are called "first drip" (front arrival; saturation in a
modelled `P(t)` shifted by a **fitted** `t_shift = 0.796 s`; first sample above 0.5 g on the DE1
scale), with no validated mapping between them — and the card declares the measured one is *"NOT
a model output"*.

The evidence audit confirms the candidate's second alternative exactly: **one** physically
independent extraction, 100 samples *of it*, no replicate spread, no declared within-model band,
grind **assumed** and κ **fitted to this same shot**. It just is not the binding obstacle.

## What this does **not** say

It does not say the shared front law is *correct* — two implementations agreeing is a statement
about the code and the source. It does not say `first_drip_time` is worthless as a discriminator:
this bounds **one pair**. It changes no evidence label or rung. The full ceiling is in
[`decision.md`](decision.md).

## Recorded, not applied

The evidence audit found `puckworks/data/MANIFEST.csv` row `de1_fixtureA` declaring
`validation_strength = independent (parameter-free triangle)`, which contradicts ROADMAP §7.1's
own 2026-07-16 entry calling the same first-drip bracket *"a wide-bracket compatibility check on
in-sample data, not a parameter-free independent result."* It is **named and left
byte-unchanged**: the Foundry is not an authority over an evidence label (CLAUDE.md), and I-045
set that precedent. Details and recommended wording in [`decision.md`](decision.md); a test
asserts the target files are unmodified by this branch.

## Two things worth carrying to the next screen

- **A generated "both models predict X" edge is a claim about cards, not about models.** Before
  treating two components as rivals, check what binds them. Here one card serves both by its own
  explicit statement, so the discriminator row was an artifact of card structure. The tension
  atlas already documents this failure mode for the opposite case — a card *without* an interface
  section hides a model — and this is the mirror image.
- **Demonstrate the identity; don't argue it.** "They share a lineage so of course they agree"
  would have been a plausible hand-wave, and it would have been unfalsifiable. Feeding one
  component's own implied forcing into the other's public entry point, and then requiring the
  residual to fall under grid refinement, turns it into a checkable claim — and the refinement
  requirement is what separates *same law* from *close enough at this tolerance*.
