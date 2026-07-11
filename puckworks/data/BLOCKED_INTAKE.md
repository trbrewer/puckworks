# Blocked Phase 0 intake — needs manual download (Tim drop)

Sprint D1 ran 2026-07-10. This CC environment reached **Zenodo** and the
**Mendeley public API**, but **MDPI** (`www.mdpi.com`) and **Royal Society**
(`royalsocietypublishing.org`) both return **Cloudflare 403** to every request
(curl and WebFetch, browser headers included), and the Mendeley *bulk* download
is not exposed by the public API. Per SPRINTS.md D1 note, these need Tim to
download and drop the files. Item **0.2 (Waszkiewicz) is fully done** — only
0.1 and 0.6 are blocked.

## 0.1 — Schmieder / Pannusch (partly blocked)
Two sources; both blocked here:
1. **Mendeley raw kinetics** — DOI `10.17632/y2tz67f6ry.1`, dataset
   `y2tz67f6ry` v1, license **CC-BY-NC-3.0**. The public API lists only the
   root file `Instructions_for_MATLAB_Code.docx`; the **`Experimental_data/`**
   folder (the actual extraction-kinetics data Pannusch fits) needs a folder_id
   the public API will not enumerate headlessly.
   - **Drop:** download "Download all" zip from
     <https://data.mendeley.com/datasets/y2tz67f6ry/1> → unzip
     `Experimental_data/` (+ `Table2` MATLAB params if present) into
     `puckworks/data/pannusch2024/`.
2. **Schmieder 2023 tables + supplementary** — *Foods* 12, 2871,
   DOI `10.3390/foods12152871`, **CC-BY**. Need **Tables A1, 2, 3** and
   **Supplementary S1** (raw fraction concentrations, replicates, fractions
   1/2/3/5/7/10).
   - **Drop:** article <https://www.mdpi.com/2304-8158/12/15/2871>,
     supplementary zip <https://www.mdpi.com/article/10.3390/foods12152871/s1>
     → `puckworks/data/schmieder2023/` (prefer the machine-readable S1 files
     over PDF transcription — do NOT hand-key the numeric tables).
- Unblocks: RC-4 gates (Sprint 6 / item 1.8a). **Not** on Sprint 1's path.

## 0.6 — Wadsworth 22-sample PSD zip (partly blocked)
- Table 1 moments are **already** in `wadsworth2026_table1.csv` (manifest row
  added; **8.1e17 → 8.1e-17 m² erratum recorded**). What is missing is the
  supplementary **zip of 22 full grain-size distributions (R, R_min, R_max)**.
- Host: R. Soc. Open Sci. 13, 252031, DOI `10.1098/rsos.252031`, **CC-BY-4.0**,
  supplementary at
  <https://royalsocietypublishing.org/doi/suppl/10.1098/rsos.252031> (RS is
  Cloudflare-403 here; not on figshare/Dryad under any searched title/DOI).
  - **Drop:** the ESM PSD zip → `puckworks/data/wadsworth2026_psd/`.
- Unblocks: pack_generator PSD inputs. Item **1.5's own gate** (refit β,R₀ from
  Table 1; S(G) monotonicity) uses Table 1, which we already have — so 1.5 is
  **not** hard-blocked by this; only the full-PSD pack_generator feed is.

## ⚠ Card provenance to confirm (not a download issue)
`docs/cards/wadsworth2026_grindmap.md` cites DOI `10.1098/rsos.252031`, but that
DOI resolves to Wadsworth's **permeability** paper ("A model for the permeability
of coffee pucks validated using X-ray computed micro-tomography"). Most likely
one paper covers both the grind map and the permeability model (the existing
`wadsworth2026_table1.csv` carries both grind moments and k), but this should be
confirmed against the card of record before 1.5 lands.
