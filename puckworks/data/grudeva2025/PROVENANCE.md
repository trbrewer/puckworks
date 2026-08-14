# grudeva2025 — data provenance

Source card: `docs/cards/grudeva2025.md` (ROADMAP items 0.7 / 1.7b).

**Origin:** (S1) Y. Grudeva, PhD thesis, Univ. Portsmouth 2023; (S2) Grudeva,
Moroney & Foster, *Eur. J. Appl. Math.* 37, 496–519 (2026), DOI
`10.1017/S095679252500018X` (open access). Reference solver + experimental data:
`https://github.com/YoanaGrudeva/espresso-model` (S1 ref 45).

## Files
| file | source | extraction | content |
|---|---|---|---|
| `grudeva_params.csv` | card Parameters table | **transcription** | both named dimensional configs (`grudeva_thesis_cafe` = S1 Table 3.1, `grudeva_paper_nominal` = S2 Table 1) + the **adjudicated κ ≈ 2.2e-15** and P_app = 9.2e5 Pa corrections (LOG Issues 2/2a). |
| `exp13_per_vial_stats.csv` | reference repo `exp13.csv` | **derived** (mean/SD I computed) | per-vial solubles mass mean ± SD (g) over the C1 14-shot dataset (16 vials × 2 s). G3 post-fit reconstruction target = the paper's Fig 2.3/6.8. |

## Rights (per file — not one basis for the directory)

| file | rights basis |
|---|---|
| `exp13_per_vial_stats.csv` (derived from the upstream repo) | **`PERMISSION_DOCUMENTED`** — direct written permission from **Dr. Yoana Grudeva**, **2026-08-14**, **LinkedIn direct message**, expressly covering **both code and data**. The complete correspondence is **retained privately by the repository maintainer**; the sanitized public record is `docs/permissions/grudeva2025.md`. **No formal SPDX licence was supplied** — the upstream repo still declares none, is not relicensed, and is not placed under the Puckworks MIT licence (`THIRD_PARTY_NOTICES.md`). Issue #73. |
| `grudeva_params.csv` (transcribed from the publications) | **unchanged: thesis (S1) + EJAM article (S2), open access CC-BY.** Transcribed from the publications, not taken from the upstream repo, so this basis is **not** rewritten as permission-based. The 2026-08-14 permission is noted here only as a cross-reference. |

Superseded, historically correct: until 2026-08-14 the derived vial statistics were carried as "no
explicit license" with the rights question open. That was accurate when written — no permission was then
on record. Permission changes the **rights** basis only; it changes no value, no transformation, no
attribution, and no validation strength.

## Notes / caveats
- `exp13_per_vial_stats.csv` is a **derived summary** (per-vial mean/SD) computed
  from the repo's `exp13.csv`; the raw per-shot file is still **NOT** redistributed
  here. Permission to use and share the upstream material does not by itself
  authorize shipping new upstream payloads (`raw.xlsx`, the raw per-shot CSV) —
  that would be a separate scope decision. Solubles mass = vial beverage weight ×
  TDS. Parsed 14 shots (card cites 13; 14 blocks present).
- κ row: both sources print 2.2e-16 m²; the card **adjudicates 2.2e-15** (decade
  typo, propagated from the P_app 9.2e-6 → 9.2e5 Pa exponent slip). The component
  uses Eq. 6.14 which reproduces 2.27e-15 at 9.2 bar.
- The reduced-model component (`grudeva2025.reduced`) is a **faithful port of the
  reference solver**, used under the same 2026-08-14 permission (see the rights
  table above), whose capacitance carries no ε — confirming the card's
  no-ε adjudication (G0). Validation strength: **post-fit reconstruction**
  (parameters fitted to this same vial data); RC-2 stays verification-gated until
  the forthcoming companion outlet-concentration dataset lands.
