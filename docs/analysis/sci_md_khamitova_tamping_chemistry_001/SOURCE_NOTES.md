# Source and observation basis

SCI-MD-KHAMITOVA-TAMPING-CHEMISTRY-001 is G1 / RESEARCH_ONLY /
NO_GOVERNING_PHYSICS_CHANGE / RETROSPECTIVE / TARGET_EXPOSED / SOURCE_INTERNAL /
NONSCORING. PHYSICAL_VALIDATION=NOT_ESTABLISHED. The review and source values
were already exposed before [PLAN](PLAN.md); no preregistration or held-out test.

## Identity and access

Gulzhan Khamitova, *Advanced experimental and analytical study for the optimization
of the Espresso Coffee extraction*, PhD dissertation, University of Camerino,
School of Advanced Studies, XXXII Cycle, Chemical and Pharmaceutical Sciences
and Biotechnology (Pharmaceutical Sciences curriculum), supervisor Sauro Vittori.
[Official record](https://pubblicazioni.unicam.it/handle/11581/480144),
[full metadata](https://pubblicazioni.unicam.it/handle/11581/480144?mode=full),
[DOI](https://doi.org/10.15165/khamitova-gulzhan_phd2020-06-25).
The actual `dc.date.issued` is **2020-06-25**, not the acknowledgements date
20 April 2020 (PDF 3). The June date is the repository's issue date; this audit
does not independently authenticate a defence event. Accession is 2024-03-22.
The cover agrees with the official title; the embedded Word/PDF title differs.

The [official PDF](https://pubblicazioni.unicam.it/retrieve/3a8685a5-32a6-4ecd-aff2-eb85df19990f/Khamitova%20Gulzhan%2025.06.2020pdf.pdf)
is 5,146,825 bytes, 189 pages; SHA256
`59065ee31eb23c694c53dd1c7702c141d5c29bdd79413933e1b62e2fc70aa229`.
Direct retrieval returned HTTP 200, no partial Content-Range, Content-Length
5,146,825 and curl success. Received size matched; pdfinfo parsed 189 pages and
the file ends in `%%EOF`. Completeness was checked before numerical use; a
parseable prefix was not accepted. Metadata authentication is separate from the
440-cell numerical audit below. Browser retrieval failed, direct HTTPS succeeded.

The landing page labels open access but leaves the licence field blank and states
an all-rights-reserved default. This bundle records factual values, locators and
hashes; neither the PDF nor page images enter Git. Access status grants no broader
redistribution licence. [source_metadata.json](source_metadata.json) records
bibliographic identity, labels, page mapping, rights and the download check.

The configured external inventory was queried only for this family. Its five
underlying Khamitova CSVs were inspected and match the five packaged files byte
for byte. They are copies, not independent observations. No other collection was
searched for values, no full census was rerun and no exhaustion claim is made.

## Source mapping and numerical audit

All page numbers below pair **printed / one-based PDF**; the chapter offset is 17.

| Material | Printed | PDF | Use |
|---|---:|---:|---|
| §3.1.4–3.1.5 | 29–30 | 46–47 | analytical preparation and method validation |
| §5.3.1–5.3.3 | 95–101 | 112–118 | apparatus, extraction count, tuning and chemical interpretation |
| Table 5.2 | 98 | 115 | total CQA, 9 rows × 4 forces × 3 entries |
| Table 5.3 | 99 | 116 | caffeine, same structure |
| Table 5.4 | 99–100 | 116–117 | trigonelline, first two rows on 99, remaining seven on 100 |
| Table 5.5 | 100 | 117 | nicotinic acid, same structure |
| Table 5.6 | 101 | 118 | ground context, 4 analytes × 2 entries |
| §5.4.3 | especially 105 | especially 122 | explicit fixed-grind/granulometry assertion |
| §5.4.4 | 111–114 | 128–131 | author's interpretation, model comparison and mass–volume assumption |

[Cell audit](cell_audit.csv) retains every literal numeric string and its printed
precision, table, row label, force-group label, page and exact CSV row. The three
columns within each force group are `mg/40ml`, `mg/ml`, `RSD`. The row uniquely
identifies pressure and temperature; the force plus column identifies the cell.
[Ground audit](ground_audit.csv) retains all eight Table 5.6 strings and headers.
All labels, all 432 chemistry entries (144 amounts, 144 related concentrations,
144 RSDs), and all eight ground entries agree numerically with the existing CSVs.
CSV trailing zeros are sometimes absent; the audit recovers precision from the
source, never from float formatting. All 288 chemistry amount/concentration
strings have two decimal places; all 144 RSD strings have one. This is an observed
audit result, not a precision rule inferred from neighbors.

Optional [audit_source.py](audit_source.py) independently extracts layout text and
compares each source-mapped cell numerically with its original CSV column. All
four table pages were also rendered and visually inspected, including repeated
digits, trailing zeros, continued Table 5.4 rows and Table 5.6. Visual review
confirms the Table 5.4 11-bar/88°C boundary between `5.0` RSD and `115.39` amount;
these must remain separate cells. Source degree typography uses a superscript
zero, retained as `⁰C`; Table 5.5's 11-bar/93°C row lacks a comma. Neither changes
condition identity. Caption and narrative cross-reference errors are retained in
the metadata; caffeine is Table 5.3, not the narrative's Table 5.4. Figures 5.3
and 5.4 depict caffeine and CQA respectively despite inconsistent narrative labels.

The primary observation is **reported amount per reference 40 mL**, using only
the first reported column. The second is related-unit context, not a second
observation. Under half-last-place intervals, 143/144 pairs intersect after
multiplying concentration by 40. One does not: Table 5.2, 7 bar / 88°C / 10 kgF
prints **131.84** and **3.29**. Its amount interval is [131.835, 131.845]; the
40-scaled concentration interval is [131.4, 131.8]. The nominal difference from
40×3.29 is 0.24 mg/reference 40 mL. This is a source-level inconsistency, not a
transcription error. Retain both values and source-labelled primary arithmetic;
do not intersect them to sharpen it, average them or infer actual cup mass.
All five original CSV byte hashes are in [results.json](results.json).

## Preparation and unresolved aggregation

**Extraction count versus analysis count.** §5.3.1 printed 95–96 / PDF 112–113
reports 72 extracted samples, and §5.3.3 printed 96 / PDF 113 specifies 36
configurations in duplicate. One coffee (100% Arabica Cibao Altura), one VA388
Black Eagle machine, Mythos 2 grinder, tamping machine and 20 g VST Competition
basket are described. Each table has one reported mean and RSD per analyte and
configuration, but the number/type of analyses entering each mean and RSD,
within-shot averaging, pooling and shot-to-assay join are not established in the
inspected passages. Duplicate extractions do not establish n=2 for the RSD.
The 144 analyte means are not 144 independent extractions.

§3.1.4 printed 29–30 / PDF 46–47 describes 1 mL espresso diluted 50-fold in
mobile phase, centrifugation at 13,300 rpm for 10 min, filtration and HPLC-VWD.
§3.1.5 describes triplicate calibration concentrations, five replicates per
standard concentration over five days, and separate retention-time checks.
These analytical-validation repetitions are not identified as the replication
basis of Tables 5.2–5.5. RSD semantics remain unresolved; use **reported-RSD
scale**, never SD of shots, standard error, confidence interval or RSD/√2.
No raw replicates, shot IDs or cross-analyte covariance are reconstructed.
Total CQA is an aggregate source label, not a species-matched 5-CQA measurement.

**Grind and tuning.** §5.3.3 printed 96 / PDF 113 says the espresso, grinding and
tamping machines were manually tuned/calibrated for each variable to obtain the
intended mass and volume. §5.4.3 printed 105 / PDF 122 explicitly asserts that
chemical composition, granulometry, coffee type, grinding settings and equipment
were the same for all extractions. The latter refers back to the same campaign,
so it cannot simply be dismissed as unrelated simulation-only text. Initial
calibration followed by fixed grind could reconcile the passages, but the phrase
about tuning for each variable does not establish that chronology. No setting
log or shot-level reconciliation is supplied. Disposition: retain the source's
fixed-settings assertion **alongside the tuning ambiguity**. Do not infer that
grind changed in every contrast, call fixed grind unreported, or isolate a causal
tamping effect under either interpretation.

**Mass, reference volume, time and tolerances.** §5.3.1 printed 95–96 / PDF
112–113 specifies 20 g in, 40±2 g out (Acaia balance), 25±1 s and a brew ratio
written `1:2±0.02`. At exactly 20 g dose, ±2 g beverage implies ±0.1 on the
beverage/dose ratio; ±0.02 would imply ±0.4 g. These statements are inconsistent
under that ratio reading; neither is silently repaired. §5.3.3 printed 97 / PDF
114 also summarizes caffeine at 40 mL/26 s, whereas the protocol uses 25±1 s;
26 s lies at that tolerance's upper edge, not a newly authenticated clock per
cell. Tables use 40 mL reference amounts. The tuning passage refers to mass and
volume, but no measured cup-volume series or density is given. §5.4.4 printed
114 / PDF 131 explicitly assumes mass–volume equivalence when comparing the
model's 39.5–41.7 cm³ to a 40 cm³ target. That is a source model assumption, not
an authenticated measurement of volume or beverage density. No conversion to
measured whole-cup recovered mass or extraction yield is supported here.

**Ground-coffee context.** §5.3.1 printed 95 / PDF 112 describes 1 g ground
coffee mixed with 10 mL water, stirred 30 min at 80°C, then a 0.5 mL aliquot plus
0.5 mL mobile phase, centrifugation at 13,000 rpm for 10 min and 0.45 µm PTFE
filtration before HPLC-VWD. Table 5.6's caption says mg/mL, headers mg/10mL.
The narrative's 1 g/10 mL basis supports retaining the header-labelled assay
context, but does not resolve the caption conflict or explicitly document the
dilution back-calculation. Exhaustive recovery, saturation and total soluble
inventory are not established by this preparation. The author's approximately
80%/20%-lower discussion on printed 101 is attributed context, not a qualified
recovery result adopted here. No inventory-recovery, saturation or EY calculation.

## Interpretation and dispositions

On printed 101 / PDF 118 the author calls the between-condition variations
narrow but appreciable relative to mean RSD (roughly two/three times), and
attributes differences to the three varied preparation parameters. On printed
113 / PDF 130 the author explicitly avoids averaging all conditions because
that variability matters for the proposed customization aim. The model pressure
response called nearly imperceptible is not an experimentally established null
for tamping. No original statistical null, p-value or equivalence test is
identified in these passages; none is invented. Our pairwise RSD diagnostic is
new descriptive arithmetic, not the author's dispersion statistic. Nonzero
reported differences neither disprove a statistically nonsignificant finding
nor establish practical importance.

| Unresolved question | Disposition in this task |
|---|---|
| Mean/RSD aggregation and effective analysis count | Report 72 extractions/36 duplicated configurations; scale-only RSD diagnostic; no inferential statistics |
| Tuning versus fixed grind | Preserve both passages and ambiguity; descriptive nominal-force labels only |
| Ratio tolerance and measured cup volume | Preserve conflicting tolerance strings and model assumption; reference-volume amounts only |
| One related-unit mismatch | Retain source amount and flag; 143 other pairs checked; no column fusion |
| Ground caption/dilution/exhaustiveness | Retain Table 5.6 as context only; no recovery denominator |
| Practical adequacy or isolated tamping effect | Unestablished; later consumer needs its own justified error budget and observation basis |

Repository search scope: case-insensitive `khamitova` references in `puckworks/`
(including analysis, models, validation, contracts and loader), `tests/`, card,
MANIFEST and current data discovery producers. The loader and tests consume the
tables; `maille2024/phi_closure.py` and contracts cite the 100 µm fines convention;
I-024 explicitly excludes this dataset as a different rig/design with reference
strength. No current numerical consumer of the blanket null wording was found.
This limited search does not prove a global absence. I-024 and accepted Foster,
Mo, Cameron, Corrochano and Waszkiewicz bundles, equations/status and conclusions
remain unchanged. No production bug, mechanism, calibration/validation edge,
EWP implementation, source independence or physical-validation upgrade follows.
