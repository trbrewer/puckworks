# Proposed protocol — discriminating the κ(t) mechanism behind the rising-flow residual

**Status: PROPOSED EXPERIMENT DESIGN. No data in this repository satisfies it.**
This document specifies the decisive measurements that would separate the bed
mechanisms competing to explain the Waszkiewicz 9-bar *rising*-flow residual, which the
in-repo analysis (`ANALYSIS_P2.md` §2.2, PAPER_B §4) can only partially adjudicate. The
model predictions below are computable from the registered components *now*; the
measurements are not — this is the experiment the paper points to, written so an
experimental collaborator (or a future rig build) can execute it.

Every discriminating observable here is one already **named on a model card** (ROADMAP
§ "Discriminating observables named on the cards"); nothing is invented. No numeric
acceptance thresholds are asserted for the (nonexistent) data — only the *sign/shape*
predictions each mechanism makes, which is where the mechanisms genuinely separate.

## What is already settled (do not re-litigate)

- **Time variation is required** (PAPER_B §4): every constant / static-κ(P) null fails
  on the rising residual by ~5×; a mechanism that changes the bed's resistance over the
  shot is needed.
- **The matrix-resistance mechanisms are refuted by *sign*** (rung 5b + analytic): both
  particle swelling (`mo2023_2`) and fines migration (`fasano2000_partI`) can only
  *raise* resistance at fixed pressure, so both predict *falling* flow — the wrong sign
  for a rising residual (swelling: r ≈ −0.95 with the trace; fines: Lemma 8.3 monotone
  non-increasing at constant p₀). Dissolution-driven porosity *opening* (Φ(t)) is the
  only tested branch with the correct sign.

So the **live question** this protocol targets is narrower and sharper: *is the rising
residual sourced by dissolution opening porosity, or could a history-dependent matrix
effect still contribute once the applied pressure is allowed to change* (Fasano Part III:
at fixed p₀ the matrix branches cannot raise flux, but under a **rising** p₀ or a
**reversed** flow they make distinct, testable predictions). A sign test at fixed 9 bar
cannot see that; these protocols can.

## Mechanism → prediction matrix

| Mechanism (component) | Fixed-p sign | Flow-reversal replay | Pressure step-up | Rebrew (spent puck) | Depth porosity gradient |
|---|---|---|---|---|---|
| **Dissolution Φ(t)** (`waszkiewicz2025` / `cameron2020`) | rising (correct) | **no decay to replay** — porosity change is irreversible mass loss, direction-independent | flux tracks the static κ(P) jump; **no extra restart** (matrix already opened by dissolution, not pressure) | **flat at endpoint** — solute already removed, no fresh opening | ~uniform opening (bulk dissolution) |
| **Fines migration** (`fasano2000_partI`) | falling (refuted at fixed p) | **asymmetric**: reversing flow re-mobilises the outlet-deposited compact layer → decay does **not** replay symmetrically (Fasano Fig. 8.4) | flux may rise only if p₀ rises (Part III), but the compact layer persists | responds to pressure cycling; partial re-open then re-clog | **bottom-high** (fines deposited at the outlet; mo2023 Figs. 6/14/16 sectioning) |
| **Compaction / swelling** (`fasano2000_partII`, `mo2023_2`) | falling (refuted at fixed p) | **symmetric** — porosity change is a local grain rearrangement, direction-independent, so reversal replays the decay | Part III: with ∂K/∂ε ≥ 0, removal may **restart** under rising pressure — a distinct restart signature | elastic recovery on unload (partII h·ξ₂ term) | depends on strain field; not necessarily bottom-high |

The three protocol columns are exactly the card-named observables: **flow-reversal replay
(Fasano Fig. 8.4)**, **pressure-step (Fasano Part II/III endpoint result)**, **on/off
rebrewing without dissolution (Waszkiewicz Fig. 10 delamination)**, plus the **post-extraction
depth porosity gradient (mo2023)**.

## Protocol 1 — Flow-reversal replay (migration vs compaction; Fasano Fig. 8.4)

*Apparatus.* A bed fixture that can reverse the superficial flow direction after a
forward extraction phase, holding Δp magnitude fixed.
*Procedure.* (a) Run a normal forward shot to a chosen endpoint, recording q(t). (b)
Reverse the flow and record the reverse-direction q(t) under the same |Δp|.
*Discriminator.* **Fines migration is direction-asymmetric** — the compact layer sits at
the forward outlet, so reversing flow re-mobilises it and the reverse decay does *not*
mirror the forward decay. **Compaction/swelling is direction-symmetric** (a local
porosity field), so the reverse decay replays the forward one. This is the classical
Fasano Fig. 8.4 signature.
*Model side (available now).* `fasano2000_partI.simulate` produces the forward q(t) and
the free-boundary compact-layer position s(t); the asymmetry is a structural property of
the deposited layer, not our chosen closures.

## Protocol 2 — Pressure step-up mid-shot (Fasano Part II/III restart signature)

*Procedure.* Hold a constant applied pressure through the rising phase, then **step p₀
up** and hold; record q(t) across the step.
*Discriminator.* Fasano Part III endpoint result: with permeability K = K(b, m) only
(pure transport/clogging), the flux can rise again **only** because p₀ rose — it tracks
the static κ(P) jump and no more. With **∂K/∂ε ≥ 0** (a genuine porosity–permeability
coupling, i.e. the compaction/swelling matrix), **removal may restart** under the rising
pressure — an *extra* flux gain beyond the static jump. Dissolution Φ(t) predicts the
static-jump response with no restart (its porosity opening is set by dissolved mass, not
by the pressure step).
*Model side.* `waszkiewicz2025.q_static` gives the pure static-jump baseline; the
Φ(t) and RC-3b branches give the dissolution response; a lifted Part II κ(t) closure
would give the restart branch **iff** its constitutive constants are supplied (see
"Blocked inputs").

## Protocol 3 — Rebrew a spent puck without fresh solute (Waszkiewicz Fig. 10)

*Procedure.* After a full extraction, re-run flow on the **same, now largely spent**
puck (no fresh dissolution available); record q(t) and compare to the first shot's
endpoint.
*Discriminator.* **Dissolution Φ(t) predicts a flat rebrew** — the porosity was opened by
mass that is now gone, so there is no further opening and flow stays at the first-shot
endpoint. A **matrix mechanism** (poroelastic / delamination, Waszkiewicz Fig. 10)
responds to the renewed pressure cycle regardless of solute, so the rebrew flow is *not*
simply the frozen endpoint. This isolates "porosity opened by dissolution" from "porosity
governed by the stress state."
*Model side.* Re-running `cameron2020.simulate_shot` on a depleted initial inventory
yields the near-flat dissolution rebrew prediction; the poroelastic curve yields the
pressure-cycled alternative.

## Protocol 4 — Post-extraction depth-resolved porosity (mo2023 sectioning)

*Procedure.* Sacrificially freeze/section the spent puck and measure porosity vs depth
(or image the fines distribution).
*Discriminator.* **Fines migration predicts a bottom-high (outlet-side) porosity/solids
gradient** — the deposited compact layer (mo2023 Figs. 6/14/16). **Bulk dissolution**
predicts a comparatively uniform opening; **swelling** predicts a strain-set profile that
need not be bottom-heavy. This is a static end-state observable, complementary to the
three dynamic protocols.

## Decision logic

1. If **Protocol 3 (rebrew) is flat** and **Protocol 4 shows no outlet gradient** →
   dissolution-opening is the dominant source (consistent with the fixed-p sign result).
2. If **Protocol 1 shows reversal asymmetry** or **Protocol 4 shows a bottom-high
   gradient** → a fines-migration contribution is present that the fixed-p flow trace
   could not see.
3. If **Protocol 2 shows a restart beyond the static jump** → a genuine ∂K/∂ε matrix
   coupling contributes, and the Part II κ(t) closure earns a (constrained) fit.
   Absent that restart, the Part II closure stays an untested skeleton.

A clean dissolution verdict is outcomes (1) with null results on (2). Any positive matrix
signal upgrades one of the currently-refuted branches from "wrong sign at fixed p" to "a
history/stress contribution visible only under changing p or reversed flow" — which the
paper should then report, not suppress.

## Blocked inputs (why this is a proposal, not a result)

- **No reversal / pressure-step / rebrew / sectioning data** exists in-repo (single-rig,
  forward, constant-9-bar traces only). These require a second rig or a collaborator run.
- **The Fasano Part II porosity-evolution law has no published constitutive constants**
  (`docs/cards/fasano2000_partII.md`: δᵢ, g, h, ξ₁, ξ₂, ε_*, ε* "not provided"), so its
  restart branch (Protocol 2) cannot be *predicted* quantitatively until either the
  constants are supplied or fitted to Protocol-2 data — it is deliberately **not**
  invented here.
- Depth-porosity and reversal fixtures are the same instrumentation gaps listed as
  external blocks in PAPER_B §7.

## Cross-references
- `ANALYSIS_P2.md` §2.2 — the partial verdict this protocol would close.
- `PAPER_B_DRAFT.md` §4 (Result 2) and §6–§7 (open gaps).
- Cards: `fasano2000_partI.md`, `fasano2000_partII.md`, `waszkiewicz2025.md`,
  `mo2023_2.md`, `cameron2020.md`.
