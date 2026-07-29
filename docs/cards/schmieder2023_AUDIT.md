# Cross-check audit: `schmieder2023.md` vs uploaded source

**Upload:** Schmieder, Pannusch, Vannieuwenhuyse, Briesen, Minceva, "Influence of Flow
Rate, Particle Size, and Temperature on Espresso Extraction Kinetics." *Foods* 12, 2871
(2023). DOI 10.3390/foods12152871.
**Standing card:** `/mnt/project/schmieder2023.md` (data-only, effort S).
**Action taken:** no-redundancy rule — the upload is the paper of record for an existing
card, so this is an audit, **not** a second card. This document does not follow TEMPLATE.md.

**Standing status: CONFIRMED with corrections.** Equations 1–4 are faithfully transcribed;
Table A1 central-point parameters are correct to the digit; the validity-range and
interface sections hold. The verdict class (`data-only`, effort S) is unchanged. Eleven
deltas below: one is a factual error in the parameter table, one is an availability
upgrade that changes acquisition priority, and the Overlaps section predates six cards
that now bear on it.

---

## D1 — **Correction (material).** The 9.3 / 7.4 / 3.8 bar pressure triple is misattributed

Card, Parameters row: `brew pressure vs grind @ F 2.0 | 9.3 / 7.4 / 3.8 (GL 1.4/1.7/2.0) | bar | measured`.

The `@ F 2.0` annotation is a card-side inference and is contradicted by the paper's own
Table 2. §3.3.3 states the triple without naming a flow rate. Table 2 at F ≈ 2 mL s⁻¹
gives **3.9 / 3.4 / 3.3 bar** (Exp 3 / Exp 7 CP / Exp 4) — a 0.6 bar spread, not 5.5.

Reproduction test across all Table 2 groupings (mean weighted by replicate count; pooled
SD includes between-group scatter):

| grouping | mean (bar) | pooled SD | mean + 1 SD |
|---|---|---|---|
| GL 1.4 @ F≈1.0 (Exp 8,9) | 2.85 | 0.12 | 2.97 |
| GL 1.7 @ F≈1.0 (Exp 1) | 2.70 | 0.11 | 2.81 |
| GL 2.0 @ F≈1.0 (Exp 10,11) | 2.75 | 0.17 | 2.92 |
| GL 1.4 @ F≈2.0 (Exp 3) | 3.90 | 0.20 | 4.10 |
| GL 1.7 @ F≈2.0 (Exp 7) | 3.40 | 0.53 | 3.93 |
| GL 2.0 @ F≈2.0 (Exp 4) | 3.30 | 0.11 | 3.41 |
| GL 1.4 @ F≈2.7 (Exp 12,13) | 8.00 | 1.18 | **9.18** |
| GL 1.7 @ F≈2.8 (Exp 2) | 5.30 | 1.87 | **7.17** |
| GL 2.0 @ F≈2.9 (Exp 14,15) | 3.55 | 0.28 | **3.83** |

No mean at any flow reproduces the triple. `mean + 1 SD` at the **high** flow rate gives
9.18 / 7.17 / 3.83 against the printed 9.3 / 7.4 / 3.8 — and §3.3.3's own preceding
sentence speaks of the "maximal brew pressure." Best reading: these are per-shot **maxima
at F ≈ 3.0 mL s⁻¹**, not means at F 2.0. Not resolvable from the printed material.

**Patch (Parameters):**
```
| brew pressure vs grind, high flow (F≈3.0) | 9.3 / 7.4 / 3.8 (GL 1.4/1.7/2.0) | bar | measured — basis ambiguous; §3.3.3 prints no flow rate and no averaging rule. NOT reproducible as a Table 2 mean at any flow; ≈ mean+1SD at F≈2.7–2.9. Read as per-shot maxima. Do not use as a Darcy ΔP(Q) point. |
| brew pressure vs grind, mean @ F≈2.0 | 3.9 / 3.4 / 3.3 (GL 1.4/1.7/2.0) | bar | measured (Table 2, Exp 3/7/4) |
| brew pressure vs grind, mean @ F≈1.0 | 2.85 / 2.70 / 2.75 | bar | measured (Table 2, Exp 8,9 / 1 / 10,11) |
| brew pressure vs grind, mean @ F≈2.8 | 8.00 / 5.30 / 3.55 | bar | measured (Table 2, Exp 12,13 / 2 / 14,15) |
```

**Discriminating computation (named, not run):** the DE1 logs P(t) per shot. If the
Mendeley deposit (D4) or Supplementary S4.1 carries per-shot pressure traces, compute both
the shot-mean and shot-maximum P per experiment and test which reproduces 9.3 / 7.4 / 3.8.
If neither deposit carries pressure, this goes to the author-correspondence queue
(same lab as `pannusch2024`, so one query can cover both).

## D2 — Correction, downstream of D1

Card, Interface mapping: "measured P 2.6–9.3 bar." Table 2's actual measured range is
**2.6–8.4 bar** (Exp 11 → Exp 12). The 9.3 is text-only and of ambiguous basis.

## D3 — **Upgrade.** The pressure data are a *flow-dependent* grind constraint, which the card understates

Card, Overlaps: calls the pressure(grind, flow) points "a clean external constraint on
kappa(P) / clogging." Sharper, and more useful:

At F ≈ 1.0 the three grinds are indistinguishable (2.85 / 2.70 / 2.75 bar). At F ≈ 2.8
they separate hard (8.00 / 5.30 / 3.55 bar). The GL1.4 : GL2.0 pressure ratio moves from
**1.04 to 2.25** as flow triples. Under Darcy with a grind-dependent-but-constant `k`, that
ratio is flow-invariant. It is not. At a fixed 20 g dose and near-identical PSD
(d₃₂ 28.3 / 26.9 / 29.2 µm, not significantly different), this is a direct signature of
either an inertial/Forchheimer term or a flow-rate-dependent clogging — i.e. the card
should name the **flow backlog item (Forchheimer/inertial correction)**, which it currently
does not, alongside the bed_dynamics κ(t) item it does.

**Confound to record with it:** the DE1 switches out of preinfusion when P > 2.5 bar.
Every F ≈ 1.0 reading (2.6–2.9 bar) sits within ~0.4 bar of that threshold, so the
grind-insensitivity at low flow may be partly a control artifact rather than physics.
Do not use the F ≈ 1.0 triple as a κ constraint without resolving this.

## D4 — **Availability upgrade (changes acquisition priority)**

Card, Extractable data: "Raw/segmented data otherwise 'from corresponding author on
request'" — which is what the paper's Data Availability Statement says. But
`pannusch2024.md` records the Schmieder 2023 extraction-kinetics dataset (TDS, caffeine,
trigonelline, CGA vs beverage volume; F 1–3 mL s⁻¹, T 80–98 °C, three grinds) as published
in a **public Mendeley repository, DOI 10.17632/y2tz67f6ry.1**. The paper predates that
deposit and does not cite it.

Verification action (S): resolve the DOI, confirm the Schmieder kinetics are in it, and
confirm whether pressure traces are included (feeds D1).

## D5 — Validation framing: an external error metric now exists

Card reports only adj. R² 0.94–0.996 for the Eq. 2 fits. `pannusch2024` re-fits the same
data and reports the **MAPE of Schmieder's exponential fits: TDS 16.12 %, caffeine
11.03 %, trigonelline 16.51 %, CGA 13.01 %**. That is a far less flattering and more
honest scale for Eq. 2's per-point error than adj. R². Add it, with the caveat that
Pannusch is the same lab and the same apparatus — this is a re-analysis, not independent
replication.

## D6 — Overlaps section predates six cards

The standing Overlaps names only `cameron2020.extraction_bdf` + backlog items. Now also:

- **`pannusch2024` (implement-now) — Schmieder is its parameterization *and* validation
  dataset.** This is the biggest status change in the audit: Schmieder is no longer a
  nice-to-have dataset, it is a **gate dependency**. The pannusch2024 gate (reproduce
  MAPE 6.07 / 4.59 / 7.85 / 4.98 %) cannot be run without transcribing these kinetics.
  Also means the pannusch2024 validation inherits every single-bean/single-machine
  limitation listed in Schmieder's validity range.
- **`andueza2007` (skip)** — that card already cites schmieder2023 as superseding it on
  brew-ratio chemistry. Reciprocal note absent here.
- **`maille2024` (calibration-provider)** — that card proposes a λ-ordering consistency
  check against Schmieder (cumulative-mass domain vs time domain). Reciprocal note absent.
- **`angeloni2023` (data-only)** — the paper's own cross-study comparison target; see D11.
- **`egidi2024` (data-only)** — independent 12-condition EY/TDS campaign; Schmieder's
  EY range (D7) is the comparable quantity and neither card cross-references the other.
- **`wale2023`, `taip2025` (skip)** — both cite schmieder2023 as dominating them.

## D7 — **Missing derived observables: no EY or TDS% anywhere in the card**

The card claims outputs → `ShotResultState` but never converts Table 2's TDS *mass* to the
contract's `EY_pct` / `tds_pct`. Derived (not measured) at the fixed 20.00 g dose:

| BR | beverage (g) | EY (%) range | EY mean | TDS (%) range | TDS mean |
|---|---|---|---|---|---|
| 1/1 | 20 | 13.35–16.10 | 14.85 | 13.35–16.10 | 14.85 |
| 1/2 | 40 | 17.65–20.90 | 19.37 | 8.82–10.45 | 9.68 |
| 1/3 | 60 | 19.05–22.30 | 20.76 | 6.35–7.43 | 6.92 |

Mean row reproduces the paper's own stated 9.68 g (100 g)⁻¹ TDS at BR 1/2 exactly.
The whole 15-experiment × 3-BR campaign spans **EY 13.4–22.3 %**, comfortably under
`cameron2020`'s 29.6 % per-bed-volume ceiling — an independent DE1 consistency point the
card does not currently make. Tag every value **derived**.

## D8 — TDS measurement basis is omitted (normalization hazard)

The card never states how TDS was measured. Paper §2.7: sample centrifuged 4700 rpm /
10 min, thawed, diluted 1:3 by volume, refractive index at λ = 589 nm and 20 °C, calibrated
per **DIN 10775** by correlating refractive index against the mass of **dried** samples.

This is a gravimetrically-anchored TDS, not a raw Brix/sucrose-scale reading, and it is
taken on a centrifuged supernatant (fines excluded). Both facts matter for any cross-source
TDS comparison. **Candidate entry for the ROADMAP normalization-hazards table (P1)**,
alongside the Gagné 2019 moisture/CO₂ offset.

## D9 — Supplementary cross-reference erratum (transcription hazard)

The SM manifest lists S1 = experiment raw data, **S2 = extraction-kinetic fitting
parameters for single experiments**, S3 = component mass in cup for single experiments.
But §3.2 of the body text points to "Supplementary Materials **Table S3**" for the
per-replicate kinetic-curve parameters. The manifest is the one to trust; a transcription
pass following the body text will pull the wrong table. (Card's Extractable data section
follows the manifest and is correct — this note is to protect the transcription.)

## D10 — Internal-consistency verification (positive; card claims none)

Eq. 2 + Eq. 3 with the Table A1 central-point TDS fit (c₀ = 0.24827 g g⁻¹, λ = 17.47261 g,
mean fraction mass 6.0 g) reproduce Table 2 Exp 7 cup TDS as **2.951 / 3.892 / 4.192 g**
against the printed **2.92 / 3.88 / 4.19 g** — +1.1 % / +0.3 % / +0.05 %. The equation
transcription is implementable as printed, and the Eq. 3 discrete-first-fraction term is a
small correction that a pure-integral form would miss by ~1 % at BR 1/1 only. Registry
validation hierarchy: *internal consistency*, one rung above the card's current
"post-fit reconstruction." Strengthens the surrogate gate the card proposes but never
substantiates.

## D11 — Missing concordance scalars (schmieder2023 ↔ angeloni2023)

Paper §3.2 gives overall averages across all 15 experiments at BR 1/2, and compares them to
Angeloni et al. (their ref. 13 = the registered `angeloni2023`), also 20 g Arabica at ~BR 1/2:

| component | Schmieder | Angeloni 2023 | ratio A/S |
|---|---|---|---|
| trigonelline | 2.45 mg g⁻¹ | 3.39 mg g⁻¹ | 1.38 |
| caffeine | 4.57 mg g⁻¹ | 5.18 mg g⁻¹ | 1.13 |
| 5-CQA | 2.96 mg g⁻¹ | 5.27 mg g⁻¹ | **1.78** |
| TDS | 9.68 g (100 g)⁻¹ | 10.02 g (100 g)⁻¹ | 1.04 |

TDS agrees to 4 % across two labs, two machines and two beans, while 5-CQA differs by
1.78× — the authors attribute the gap to 5-CQA's roast sensitivity (their refs. 41, 42).
This is a usable cross-source spread estimate for the multi-class backlog: **bulk TDS
transfers between labs; per-species concentrations do not.** Neither card records it.

---

## Registry amendments proposed (deferred to your next registry-state revision)

1. `schmieder2023.md` — apply D1, D2 (factual corrections); add D3, D5, D7, D8, D10, D11;
   extend Overlaps per D6; upgrade Extractable data per D4.
2. `pannusch2024.md` — add a reciprocal line naming schmieder2023 as its parameterization
   and validation dataset, and inheriting its single-bean/single-machine validity range.
3. `angeloni2023.md` — add the D11 concordance row.
4. `maille2024.md` — the proposed λ-ordering check is now cheap; the data are public (D4).
5. ROADMAP normalization-hazards table (P1) — add the D8 entry (DIN 10775 refractometry on
   centrifuged supernatant).
6. ROADMAP / flow backlog — add the D3 flow-dependent-ΔP(grind) datum under the
   Forchheimer/inertial item, with the 2.5 bar preinfusion-threshold confound attached.
7. Acquisition queue — Mendeley 10.17632/y2tz67f6ry.1 (D4), verify pressure-trace presence.

**Standing verdict, unchanged in class, raised in priority:**

VERDICT: data-only — transcription targets and corrections only, no mechanism to implement; but the dataset is now the parameterization *and* validation input for `pannusch2024` (implement-now), so it is a gate dependency rather than an optional dataset, and the raw data appear to be public — effort S.
