# WP6-LC-IDENT — can Ξ be inferred from boundary measurements alone?

```
HUMAN_SELECTED_POST_SNAPSHOT
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

**Decision: SURVIVE.** Full record in [`decision.md`](decision.md); the question was frozen in
[`PROTOCOL.md`](PROTOCOL.md) before the module existed.

## What was run

The exact steady two-path Darcy network (`puckworks/models/lateral_coupling.py`, `model1_two_path`)
in the isoresistive-mirror geometry the discrimination harness already uses — `(3, 1, 1, 3)` as the
primary case. The screen asks whether the two **boundary** observables

```
R = Q/Q0   (total flow, lateral bridge open ÷ blocked)
s = q1/Q   (separate outlet-flow share)
```

determine the exact pressure-equalization number `Ξ = G_lat·(1/A₁ + 1/A₂)` — that is, whether the
lateral-coupling mechanism is *identifiable* without ever measuring `k_lat` or the inter-path
spacing `w`.

Six arms: a hand derivation of the forward map and inverse, falsified against the network on a
predeclared 10 × 22 `(c, Ξ)` grid; the minimum-observable test; the **existing** physical-vs-proxy
adversary (called, not reimplemented); six controls; and a 16-sign-corner mirror-imperfection
adversary at 1 %/2 %/5 %.

## Why this was selected

`docs/cards/lateral_coupling_feasibility.md` §4 carries two OPEN go/no-go boxes. Box 6 —
*"the inference is not structurally non-identifiable"* — had never been tested: the repository
contained forward maps only and no inverse anywhere. It is decidable with algebra plus the model
already in the tree, needs no new data, no new machinery and no compute campaign, and it directly
challenges the card's box-5 parenthetical *"needs `k_lat` and `w`"*.

**This is not a generated candidate.** It was selected by a human from a live card after the
candidate snapshot. The Foundry has no identity mechanism for that, so it uses a stable slug. **No
`I-` number was minted; `docs/insights/ID_REGISTRY.json` and `docs/insights/candidates/` are
byte-unchanged; the 90 candidates were not scored, ranked or inspected; no lens, generator or
scoring system was added.** `docs/insights/generated/**` was **regenerated** — never hand-edited —
because the card correction this screen earned is an input the corpus map hashes. The only field
that moves in the candidate and tension payloads is `source_commit`: all 90 candidates, all 171 tension rows, every ID, every
`SEED` status and every (empty) score are identical. Scoped precisely: in the complete candidate
and tension payloads only `source_commit`/`commit` provenance moved; in `snapshot_manifest.json`
the snapshot commit, the corrected card's input hash and the derived output hashes moved, with all
other normalised manifest structure and content equal; and in `corpus_map.json` the corrected card's own entity attrs (`card_sha256`, `section_names`, `section_hashes`) moved — the map recording the card it is supposed to record, with no other entity, relation, warning or count touched. A test asserts exactly that, by
sentinel-substituted whole-object comparison rather than a field-by-field spot check.

## Result in plain language

**Yes — and when `c` is not independently known, total flow alone is not enough.**

The qualifier is load-bearing. The full hierarchy, each rung demonstrated on the exact model:

| what is known | observables | identifies |
|---|---|---|
| the mirror contrast `c`, independently and **nonzero** | `R` | **Ξ** — `R` alone *is* sufficient |
| only that the fixture is built as an exact mirror | `R`, `s` | **`c` and Ξ** — the primary result |
| all four axial conductances, calibrated and **nondegenerate** | pressure-normalised total flow | **`G_lat`** |
| nothing beyond boundary flows (general geometry) | `q₁, q₂` blocked and open | **nothing** |

Coupling always raises total flow in this mirror, but `R` depends on the axial contrast only
through `c²`. So when `c` is unknown, a single measured `R` is reproduced exactly by a *continuum*
of different `(c, Ξ)` states — **including both signs of `c`**. Adding the separate outlet share
collapses that continuum to one point, and it does so exactly, because the model obeys the identity

```
s − 1/2 = −(R − 1) / (2 R c)
```

along any fixed-`R` family. The inverse

```
ĉ = (R−1)/[R(1−2s)]      t̂ = [1 − R(1−ĉ²)]/ĉ²      Ξ̂ = 1/t̂ − 1
```

recovers `c` to 3.0e−12 and `Ξ` to 8.2e−11 relative across all 220 nondegenerate grid points, and
survives path-swap, ×10 scaling and conservation controls. The two degenerate cases — no coupling
(`Ξ = 0`) and identical paths (`c = 0`) — both land on `(R, s) = (1, ½)` and are reported as
carrying **no information**, not as a number.

**Three caveats that bound it, all measured here:**

1. **The mirror assumption is load-bearing.** A 1 % construction asymmetry can bias `Ξ̂` by a factor
   of ~5. With the four axial conductances independently calibrated, `G_lat` instead follows
   *exactly* from `Q` alone — for any **nondegenerate** calibrated geometry having a nonzero
   uncoupled mid-node pressure gap (`g1_top·g2_bot ≠ g2_top·g1_bot`), with no symmetry assumed.
   **Not "any geometry":** when that cross product vanishes the two uncoupled mid-node pressures
   coincide, nothing drives the bridge, and `Q` is exactly independent of `G_lat`. The routine
   reports that case rather than returning a number, and the failure is continuous (`1/X²`), so a
   real fixture needs a *margin* on the pressure gap, not merely a nonzero one.
2. **Boundary flows alone do not identify Ξ for an arbitrary fixture.** A family of different
   geometries spanning a factor of 8 in Ξ reproduces all four boundary flows exactly. The mirror
   *construction* closes the system — a design assumption about the apparatus, not a measurement
   of `k_lat` or `w`.
3. **The precision required is demanding.** Under the existing 1 %/2 %/5 % scenario convention, on
   the **frozen 22-point grid** exactly three points recover Ξ within a factor of two at a 1 %
   floor — **Ξ = 0.464, 1.0, 2.154** — and none at 2 % or 5 %. A separate post-hoc solve locates
   the continuous crossings at **Ξ ≈ 0.241 → 3.946** (1 %) and confirms **no passing interval** at
   2 % or 5 %. The three grid points' min and max are *not* the window and are not quoted as such.
   Worse than the band suggests, in fact: at most grid points some scenario corners return **no
   physical inverse at all**, so the plotted envelope is optimistic wherever it is marked ✕ —
   counted, not dropped quietly.

## Exact reproduction

```
python -m puckworks.analysis.screen_wp6_lateral_identifiability --write
python -m puckworks.analysis.screen_wp6_lateral_identifiability --verify
python -m pytest tests/test_screen_wp6_lateral_identifiability.py -q

# the upstream harness this screen calls, unchanged by it:
python -m puckworks.analysis.lateral_coupling_discrimination --verify
python -m pytest tests/test_lateral_coupling.py tests/test_lateral_discrimination.py -q
```

Sub-second and deterministic. `result.json` is SHA-256-bound to `PROTOCOL.md` and to every
load-bearing source, and carries its own `content_sha256`; `--verify` fails on any drift.

## Bundle

```
PROTOCOL.md             the question, frozen and committed before the module existed
README.md               this file
result.json             every number, machine-readable, producer- and protocol-bound
decision.md             SURVIVE, and why
DECISIVE_EXPERIMENT.md  the smallest experiment implied — a specification, not an authorization
figures/primary.png     one figure, three panels
```

## Current limitations

- **Synthetic and mathematical.** This is identifiability in an exact steady two-path Darcy
  network. It is **not** empirical validation of anything, and it upgrades **no** evidence rung.
- **Two paths, one mirror, steady state.** No N-path network, no PDE, no extraction clock, no time
  dependence, no real data, no fitted parameter.
- **No real-puck Ξ and no `k_lat` estimate.** Nothing here says espresso occupies the transition
  regime, or any regime.
- **`k_lat` and `w` are still required to decompose or physically interpret `G_lat`** — the screen
  overturns only the claim that they are needed to *infer* an effective Ξ.
- **No apparatus exists** and none is shown able to reach the calculated precision. The 1 %/2 %/5 %
  figures are hypothetical resolution scenarios reusing the existing floor convention — not
  instrument accuracies and not experimental uncertainty.
- **Paper 4 remains NOT authorized**, and card box 5 (an accessible experiment that can estimate Ξ)
  remains **OPEN**.
