# I-093 — deep-protocol erratum (execution budget)

```
OUTCOME_NEUTRAL
WRITTEN BEFORE ANY DEEP PERMEABILITY OUTPUT WAS INSPECTED
```

**Dated 2026-08-08.** [`DEEP_SCREEN_PROTOCOL.md`](DEEP_SCREEN_PROTOCOL.md) is **not edited** — it
is the frozen record. This erratum corrects a materially misleading **execution-budget statement**
in it. It corrects no scientific result, no model parameter, and no repository permeability claim.

## Binding

| item | value |
|---|---|
| deep protocol SHA-256 | `4cac31ef784799423a7b0a2a1b411f71d0af1b22944323f6afd482ffd5170460` |
| expected run matrix | [`expected_run_matrix.json`](expected_run_matrix.json) |
| expected run matrix SHA-256 | `c57d56acf8f886f04636715d608e32c94fdec6577e2fc0db61be88b1252a226f` |
| measured timing inputs | L=32 ≈ 18 s, L=48 ≈ 55 s, L=64 ≈ 183 s, L=80 ≈ 403 s, L=100 ≈ 726 s (measured during the cheap screen at the frozen resolution) |
| status at writing | **pre-result** — no deep permeability value had been read |

## 1. What the protocol claimed

§10 stated:

> Measured single-run costs at this resolution: L=48 ≈ 55 s, L=64 ≈ 183 s, L=80 ≈ 403 s, L=100 ≈
> 726 s. The §3 design (4 seeds × {48,64,80,100}) is ≈ 91 min, **leaving headroom for §4.**

## 2. What an outcome-neutral reconstruction shows

Reconstructing the full frozen matrix from the same measured single-run costs — performed **before
inspecting any permeability output** — gives:

| section | cells | estimated |
|---|---|---|
| §3 multi-seed RVE | 16 | 5468 s (91.1 min) |
| §4.1 tolerance sensitivity | 2 | 366 s (6.1 min) |
| §4.2 porosity dependence | 16 | 7272 s (121.2 min) |
| §4.3 trend on means | 12 | 8712 s (145.2 min) |
| **total** | **46** | **21 818 s (363.6 min)** |

**§4 alone requires ≈ 273 minutes**, and the full matrix ≈ **364 minutes**, against a frozen budget
of **150 minutes** — a shortfall of ≈ 214 minutes. The §3 estimate of ≈ 91 min was correct; the
claim that it left headroom for §4 was not.

## 3–6. What is retained unchanged

3. The **150-minute compute budget is retained** exactly.
4. The **budget guard and frozen section order are retained** exactly.
5. **No run, box size, porosity, seed, tolerance, decision threshold or section priority is
   changed.**
6. **Execution does not restart and the budget is not extended.**

## 7–11. Consequences for adjudicability

7. The controlling **§3 finite-size ensemble remains adjudicable** if its 16 frozen cells complete
   and satisfy the frozen convergence requirement — it is first in the frozen order and fits inside
   the budget.
8. **§4.1 is adjudicable only if both** of its two frozen cells complete.
9. **§4.2 is likely truncated.** Completed cells are retained and reported, but a partial prefix is
   **not** a porosity-dependence adjudication: the frozen protocol defines no partial decision, and
   the implementation records a porosity only when *both* its sizes complete, so a half-finished
   porosity is dropped rather than reported partial.
10. **§4.3 is expected not to execute**, and therefore **cannot deep-confirm or deep-reject the
    cheap-screen closure trend.**
11. The closure subquestion will be reported as **compute-bounded** if its required matrix is
    incomplete.

## 12–13. What must not be inferred

12. **The cheap-screen monotonic closure observation does not carry forward by default.** It
    remains historical cheap-stage evidence and acquires no deep standing from this shortfall.
13. The shortfall is a **synthetic-compute limitation**, not a need for new empirical data. It is
    not NEEDS_NEW_DATA and must never be described as one.

## 14. What this erratum does not decide

14. The overall deep disposition follows **the exact frozen decision logic** in
    `DEEP_SCREEN_PROTOCOL.md` §8. This erratum **does not predetermine** whether a completed §3
    result can support a surviving insight independently of the closure subquestion; that is read
    off the frozen rule once the run ends.

## 15. Classification

15. This corrects a **materially misleading scientific-protocol execution-budget statement**. It is
    an outcome-neutral scientific-provenance correction, **not** general repository administration,
    and **not** a correction to any scientific result or repository permeability claim.

## Guard semantics, recorded as frozen (not changed)

Read from `puckworks/analysis/deep_screen_i093_rve.py`:

- the budget is checked **before launching** each cell (`if spent > budget_s: break`);
- a cell admitted before the cutoff **runs to completion** — the guard never terminates in-flight
  work;
- `spent` accumulates measured wall time, so the cutoff falls mid-section;
- `porosity_dependence` records a porosity only when **both** sizes completed;
- `trend_on_stabilised_means` returns `skipped` when fewer than two porosities completed.

## Seed semantics, established outcome-neutrally

Classification: **`RELATED_NON_NESTED`**.

> Equal seeds initialize a common pseudorandom stream, but size-dependent coordinate mapping,
> placement history, stopping behavior, and draw count produce non-nested geometries. Equal-seed
> cases are not interpretable as the same physical realization at increasing size. No paired
> finite-size analysis is used. Cross-size statistical independence is not established.

Evidence, from `pack_generator.make_pack` and geometry-only tests (no permeability inspected):
same seed + same L is exactly reproducible; different seeds at the same L differ; the smaller
geometry is **not** a spatial subset of the larger; `rng.integers(0, L, batch)` makes coordinates
L-dependent; the placement loop runs until `solid.mean() >= phis_target`, so the draw count is
size-dependent (5 spheres at L=32 versus 42 at L=64 for seed 0). Voxel agreement between L=32 and
the L=64 corner was **0.5057** against a chance-level expectation of **0.5001** — supporting
evidence of weak spatial correspondence for that case only, **not** proof of statistical
independence, which was not quantified.
