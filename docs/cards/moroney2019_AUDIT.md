# Audit: moroney2019.md vs. re-uploaded source PDF (2026-07-28)

**Source re-uploaded:** Moroney, O'Connell, Meikle-Janney, O'Brien, Walker, Lee, PLoS ONE 14(7): e0219906 (2019). DOI 10.1371/journal.pone.0219906.
**Existing coverage:** `moroney2019.md` (data-only, S) + `cooper2021.md` (errata provider to its Table 2).
**Outcome:** Existing card stands. No new card warranted. Verdict unchanged: **data-only, effort S**.

## Checks performed (card vs. PDF, line-by-line)

| Item | Result |
|---|---|
| Equations 2, 4–15 (CFD flow + LDF extraction, two-grain extension) | Match as printed, including Gidaspow Eq. 6 and the h_sl = D_v/d_s relation stated at Eqs. 21–25 |
| Equations 16–30 (1-D cylindrical + truncated-cone reductions, BCs, ICs) | Match, including Eq. 30 cone pressure solution and virtual-vertex geometry |
| Table 2 (all six parameter columns: d_s, α_s, c_s0, h_sl) | Exact match, all 24 values |
| Table 1 PSD summary (d₃,₂, d₄,₃, vol% < 100 µm, both grinds) | Exact match |
| Auxiliary parameters (ρ_s 1400, φ_v 0.56, φ_0 0.143/0.122, Q, dose, chamber ID, T, Brix calibration, cone geometry) | Match |
| Validation numbers (Δp 2.319/2.3, 0.657/0.65 bar; cone 7.35 vs 8.4, 1.63 vs 1.89 bar; RMSE 7.80→5.81, 11.65→6.23 kg m⁻³; GCI 0.016%/0.005%, p = 1.85) | Match; card's circularity/verification-vs-validation labeling remains accurate |
| "Bed height not stated numerically in text" | Confirmed — L is described only as matching experimental bed heights |
| "No code or raw data published" | Confirmed — SI is two videos + two PDF appendices only |

## Deltas found (minor; addendum candidates, not card errors)

1. **Fine-grind σ(EY) ≈ 5 pp** — the Fig. 10 discussion quantifies the fine grind's in-bed EY spread as "about 5 percentage points in extraction yield level in the target range" (coarse: small). The card describes the σ(EY) observable and Fig. 10 construction but omits this one quantitative anchor. Worth one line in Extractable data if the σ(EY) observable is ever adopted — it is the paper's only numerical uniformity result.
2. **Melrose partition-coefficient note** — PDF (Eq. 12 discussion) records that Melrose et al. suggest a partition coefficient of 0.6 but fit with 1. Contextual only; no card action needed unless a melrose card later needs the cross-reference.

## Standing registry actions confirmed still pending (owned by cooper2021.md, deferred to next registry-state revision)

- Annotate moroney2019.md Table 2 with **Erratum B**: printed h_sl values are CFD-scaled; true values = printed / ρ_l (ρ_l = 965.3 kg m⁻³). The re-uploaded PDF confirms the printed values are as carded — i.e., the erratum applies to this source exactly as documented.
- Resolve the card's "single D_v cannot be recovered" note via **Erratum A** (two species diffusivities D_v1, D_v2; h_sli = D_vi/d_si).
- Transcription-check gate (reproduce RMSE 5.81/6.23 kg m⁻³) must use corrected h_sl values or it fails by construction.

VERDICT: skip (duplicate upload) — existing moroney2019.md verified faithful to source with two minor addendum candidates; all data-extraction and errata actions already tracked — effort S
