# Independent scientific review — SCI-MD-PERTICARINI-PRESSURE-GRIND-001

**Disposition: PASS within the frozen retrospective, source-internal, nonscoring scope. No material scientific or software finding; no correction requested. PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

Reviewed 2026-10-24 against base `1398d38ff1986aa85150d55ad9f797bc1aaff1eb` in `/home/tim/sci-md-perticarini-pressure-grind-001`. This receipt identifies the reviewed working files by SHA-256 below; it does not certify an unseen final commit or hosted CI result. The frozen PLAN hash agrees with its freeze receipt: `d576f613f92debc405063e5b501b0577702f3345fa31e9ffc08ed3b421339a47`.

**Reviewer disclosure:** this is a substantive independent **nonhuman Codex agent** review by `/root/independent_review`, separate from the implementation agent. It is not human peer review or experimental validation. The reviewer read the implementation, sources and claims, then constructed separate scratch source/arithmetic and discovery checks without importing the analysis producer. The reviewer made no repository edits, commits, external messages, model runs, fits, experiments or scoring calls; EWP was not accessed or modified. Scratch files and a figure screenshot were written only under `/tmp`.

## Source authentication and semantics

I read AGENTS.md/CLAUDE.md, the applicable onboarding/governance and data-discovery material, the full frozen plan and result bundle, all 396+ lines of the analysis module and its focused tests, the changed source/discovery producers and generated differences, and the accepted Cameron result and numerical contrast records.

I independently inspected the rendered thesis Tables 4.2/4.3 (printed pp.90/91, PDF pp.102/103), their headers/captions and all rows, and the full rendered Egidi PDF p.6 including Table 2 and methods. I also read the thesis methods/measurement text on printed pp.85–89 (PDF pp.97–101). Fresh visual transcriptions compared as exact rational decimal values against both canonical schemas agree on all **18 Cibao conditions/108 numeric cells** and **12 Modœtia conditions/72 numeric cells**. All 12 Modœtia rows and six numeric columns also agree visually in Egidi Table 2. Both original PDF hashes were recomputed and match the declared identities:

- Thesis: `248d480cc2ab3353799fcaa886bb1be3f6cfbe7a9f15e1cdf9d4950827424c7f`.
- Egidi: `1aba69278444d107ce5172eb29ba7b37883491fe0b32dfd9bc8898632e203a33`.

The matching condition tables, coffee/apparatus/recipe and campaign description support retaining **one** canonical Modœtia dataset, `egidi2024/table2`. Neither publication creates additional independent replication. The acknowledged pooled-time discrepancy (thesis Table 4.1 versus Egidi Table 1) is outside the included condition tables and appropriately retained without forced reconciliation.

The source explicitly averages TDS/EY over three extractions and identifies sigma as TDS standard deviation. It does not authenticate the duration statistic, duration n/spread, rounding rule or clock convention. The bundle correctly uses “reported condition duration” and does not turn chemical triplication into 90 timed-shot inputs. Nominal machine pressure labels, recipe-defined ordinal grinds and nominal dose/beverage/tamp context are preserved. No measured puck pressure drop, 40/tau measured-flow conversion, per-shot mass inference from chemical summaries, or permeability/resistance estimate enters the analysis. Both canonical CSVs are byte-identical to the base.

## Independent arithmetic, dependence and reversal

A separate scratch reduction constructed the support and contrasts directly from the canonical CSVs. It confirms 30 unique conditions, exact separate temperature identities and four strata with **12/6/6/6 rows**. All supported ordered finer/coarser pairs are included without imputation. There are **39 distinct contrast IDs: 14 primary D, 19 primary I, 4 secondary D and 2 secondary I**, plus **21 reversal diagnostics**.

Primary D values, in ordinal grind order within the available support, independently recompute to:

| Stratum | Primary D values (s) |
|---|---|
| Cibao 93.4 °C: Extra Fine, Fine, Optimal, Coarse, Extra Coarse | +1, 0, −6, −5, −6 |
| Cibao 90.4 °C: Fine, Optimal, Coarse | −2, −6, −5 |
| Modœtia 93.4 °C: Fine, Optimal, Coarse | 0, 0, −4 |
| Modœtia 90.4 °C: Fine, Optimal, Coarse | +1, +1, −3 |

Thus the primary nominal counts are **D: 3 positive, 8 negative, 3 reported zero; I: 14 positive, 2 negative, 3 reported zero**. At h=0.5 s they are **D: 8 negative, 6 unresolved; I: 12 positive, 7 unresolved**. Both adverse Cibao Optimal−Coarse interactions equal **−1 s**, have L1=4, critical h=1/4 s and conditional range [−3,1] s. They remain visible in records, text and figure; no global monotonicity claim is made.

For all 39 contrasts, I independently checked the signed original-condition coefficients, orientations, nominal value, L1 norm, exact critical h, h=1/2 bounds and statuses. I enumerated every contributing-cell box vertex at zero, h=1/2, each exact critical h and an allowance above that threshold; extrema match L0±hΣ|a|. D has norm 2 and I norm 4. Zero-touch boundaries are unresolved; printed zero with a nonempty coefficient vector is not a structural identity or physical equality. Exact fractions are retained, so display rounding cannot change classification.

All three interval-composition identities independently cancel their shared 9-bar cells in coefficient space. The two D identities and one I identity have empty residual vector, zero residual/radius for every h and null critical h. The code therefore does not add marginal radii as though shared observations were independent. The common entrywise box and limits on jointly combining marginal extrema are explicit in the result.

All 21 diagnostic records agree with their component contrasts. Five primary pairs have nominal opposite nonzero D signs, all with **strict reversal domain 0≤h<1/2 s**. None remains strict at h=1/2. The other 14 primary pairs correctly have no positive reversal threshold. Positive I is never substituted for two resolved opposing component signs.

The secondary Cibao/93.4 extremes independently give **12−9: D=+7/−1, I=+8; 12−6: D=+8/−7, I=+15 s**. Their D thresholds are 7/2,1/2,4,7/2 s, interaction thresholds 2 and 15/4 s, and reversal thresholds 1/2 and7/2 s. Only the secondary 12−6 reversal survives h=1/2. These rows remain separate from the primary question.

The exact breakpoint tables cover every threshold and interval, including zero and the unbounded final interval; independent counts agree at boundaries and interior points. CSV/JSON representations of all observations, contrasts and reversals agree field by field.

## Claims, Cameron comparison and figure

The result stays within descriptive source-duration contrasts and conditional sensitivity. h=0.5 is explicitly an assumed nearest-second illustration, not authenticated timing precision, confidence intervals, significance or experimental variability. Missing timing/pressure/mass information remains unknown even for large critical h. No mechanism, population effect, shared fitted effect, causal temperature test, grinder alignment or physical-validation upgrade is claimed.

The Cameron comparison matches its accepted exact contrast records: central-reading layer A has four positive and four negative pressure contrasts and four positive interactions; displayed-extents layer B has three positive pressure contrasts, one unresolved and four incomplete pressure contrasts, and one positive/three incomplete interactions. B establishes no reversal. The comparison correctly keeps both Cameron layers distinct from Perticarini's assumed box and makes no new tamp-dependence test.

I inspected a fresh Chrome render of the current SVG. All 39 glyphs, four primary strata, two separated secondary intervals, seconds axes, zero lines, source grind labels, negative/zero outcomes and conditional-range labels are visible. The revised footer derives counts and thresholds from the reversal records. Focused reproduction verifies every glyph's contrast ID and exact values and byte-identical regenerated CSV/JSON/Markdown/SVG outputs. The module/SVG hashes below include this bounded footer change; the initially supplied review hash list was stale for these two files only.

## Discovery preservation

Independent base-to-candidate comparisons confirm:

- Manifest remains 127 dataset identities. Only the two intended rows change, and only their `gate_use`/`caveat` fields. All 125 unrelated rows and all source-strength labels remain unchanged.
- Available-data-register and local-family-index changes are confined to the Egidi/Perticarini families apart from propagated input hashes. Chemistry qualification, model p/T limits and unrelated equations/PSD/backlog are preserved.
- The generated relation multiset changes **635→633**, removing exactly the two pre-existing `MEASURES` edges to `observable:pressure`. No relation is added or otherwise changed apart from regeneration commit metadata. Equivalently, **578 of 580 unique relation keys** remain. Both datasets retain TDS and publication derivation relations; no flow-calibration or physical-validation edge appears.
- Active candidates remain 90: **88 unchanged**, with I-032→I-103 and I-084→I-104 replacing only the affected pressure-family memberships. The existing six-dataset slice admits the next existing Gloess/Khamitova entry when Egidi is removed; this is regeneration, not a new executed or scored analysis. The corresponding tensions change T-0047/T-0165→T-0186/T-0187; all 169 other active tensions are unchanged.
- Every historical fingerprint→ID mapping is retained: 102 candidate and 185 tension mappings unchanged, two additions each. Historical IDs are reserved, never reassigned. Candidate status remains SEED with empty scores. The seeded-ID test keeps the existing survival budget and directly checks the justified replacements.

The dataset-specific extractor correction is appropriately bounded and scientifically necessary to preserve nominal-pressure semantics. The large textual generated diff does not conceal unrelated relation or candidate changes.

## Checks performed and limits of this disposition

- Independent scratch source/arithmetic check: PASS (`/tmp/perticarini-independent-check.py`).
- Independent semantic discovery preservation check: PASS (`/tmp/perticarini-independent-discovery-check.py`), plus full relation-multiplicity and active-tension comparisons.
- `PYTHONDONTWRITEBYTECODE=1 /tmp/pw-cameron-venv/bin/python -m pytest -q -p no:cacheprovider --basetemp /tmp/perticarini-independent-pytest tests/test_perticarini2024_pressure_grind.py tests/insights/test_foundry.py::test_the_seeded_ids_from_the_previous_head_survived`: **13 passed in 0.82 s**.
- Source PDF/input/plan SHA checks, independent Cameron-layer count and exact-bound sign checks, fresh SVG visual inspection and `git diff --check`: PASS.

I did not rerun the broad suite, model gates, unrelated campaigns or hosted checks. Their actual dispositions belong in VERIFICATION/PR closeout and are separate from this scientific review. Routine final receipt or hosted-status additions can reuse unchanged scientific evidence by the file hashes below; no further scientific review stage is requested.

## Reviewed file SHA-256 receipt

File SHA-256 values below are hashes of raw file bytes, not Git blob IDs. Source PDF hashes are recorded above. The module, tests, complete bundle, affected source/discovery files and accepted Cameron reference used in this review are covered here.

```text
9a0634972986dde6217a333968332fb613ea4226b15d5a964516ffa7f5a8f72a  docs/analysis/sci_md_cameron_pressure_tamp_001/RESULT.md
1250487c66386855cf30b19c0ba789083dc224b9aad603ba0f6fb11d2e97c5c7  docs/analysis/sci_md_cameron_pressure_tamp_001/contrasts.json
d47ae7af22198a112c24d4dd32c2e4d91ffa6066a7b3740f4c0c627809b6e2d8  docs/analysis/sci_md_perticarini_pressure_grind_001/COMPARISON.svg
f305f55777a4bd56492b1f94ca2c46c949e078b9832d7ae9cdb4b5bea8d88671  docs/analysis/sci_md_perticarini_pressure_grind_001/CONTRASTS.md
d576f613f92debc405063e5b501b0577702f3345fa31e9ffc08ed3b421339a47  docs/analysis/sci_md_perticarini_pressure_grind_001/PLAN.md
5ced3568e30903caa887c554f5df1bcc52ce8767052cf28332f89ea402beabf9  docs/analysis/sci_md_perticarini_pressure_grind_001/RESULT.md
ddf36df048cb56d18f4a454a77bde1ed646b5d2604ef7a656302a9c1fd3df78f  docs/analysis/sci_md_perticarini_pressure_grind_001/SOURCE_NOTES.md
03fa5b616b693abaaab7b6fdabc021804321a8cc7ec31000edf01eaf52e61519  docs/analysis/sci_md_perticarini_pressure_grind_001/VERIFICATION.md
88e803231a93ede2b4b6f11a55cb528b4747e143c0014ba30d24498df67f94b1  docs/analysis/sci_md_perticarini_pressure_grind_001/VIZ_SPEC.json
f23e2f91dd1a728aa08b30112d99432ea1ff1fc681d20e0584e24e4e1786df4e  docs/analysis/sci_md_perticarini_pressure_grind_001/contrasts.csv
b03b3e9b7b6c11ae18a031f8c7bf7d9f9e0307667b08f9fd91aa1af608df2e07  docs/analysis/sci_md_perticarini_pressure_grind_001/contrasts.json
145dc7649bb2dac46a6d73591c84c4804a500fcb869483ebd9d8e9972463b0b3  docs/analysis/sci_md_perticarini_pressure_grind_001/observations.csv
b8e39318800b968c7c09d6f25dc283df7512482e22e77b7e12055f90756a46fe  docs/analysis/sci_md_perticarini_pressure_grind_001/reversals.csv
a55565df8bf5a68e79638b1d9a2dec1a48df757e52ca19a8382a0856265ed3ab  docs/analysis/sci_md_perticarini_pressure_grind_001/reversals.json
25cd4b44be67ccdae9e9c09777fe200a727c4f9a3d7139bfe2585d686792f638  docs/cards/egidi2024.md
d779ff4dc9188bd061af5d0522411bf09384d68bb24f27165eed34bc5c2b1a0a  docs/cards/perticarini2024.md
7681a79ebd82dfd8a2146bca97ab282c5dd22363a3f1b56200b9e3d17390f1ef  docs/data/ESPRESSO_DATA_GUIDE.md
5ca84977f9a147687e5d83bce3a38f84d3b80b03919f5c89f53394300bc581dc  docs/insights/ID_REGISTRY.json
a5ad73f4118e84b9c515deef6aa5f82055775d3b1e6658e1f982ed69478d1f39  docs/insights/generated/INSIGHT_SNAPSHOT.md
36d0b80e7e8bb955faf4c76582892ef4df5bd9ecf8c0c78922f7c8ebf05c7823  docs/insights/generated/candidate_portfolio.json
5a125ab838ea7751ac2aab8733985949e10a85749b5745b89749627a40e03a88  docs/insights/generated/candidate_portfolio.md
672f2418b59db5338f653c666594ab11eb1a5902dc2d753099e81cc455b6e404  docs/insights/generated/corpus_map.json
74bb9102c289fdbe16e3e829ea858e88e26ed4e4b2af9158dfd9ecdbc821ab2c  docs/insights/generated/evidence_lineage_index.csv
45f61322b984de9e3ac1aa27ce5cbd48a839ea9bc1cad2712d41c3352af67543  docs/insights/generated/public_claim_inventory.md
f10083286d6e8be78a2a872b09919ad0cfd22302f9f2f413eabcf84c321306f5  docs/insights/generated/snapshot_manifest.json
84454ee7f1a4cec3a756373e30110edc6e146360e20a0a95181a9f8037276cda  docs/insights/generated/tension_atlas.csv
6fdcd24ce109f2a04bc85460ddae93c7a7cf32d5bacafda1a974398c501f85a3  docs/insights/generated/tension_atlas.md
a2d7a02d80cf10d53456bece33b3933e983474d0e0a74c642412ddbb56324f83  puckworks/analysis/perticarini2024_pressure_grind.py
fc03e0dffbf82069ea3f68e841b513ac2ce6e33d1bfcca70be5e9bfcf1aa68e7  puckworks/data/AVAILABLE_DATA_REGISTER.json
6d82a075fb4386d2e247b75e216b54859c4fb5255152494a961706f6a9544616  puckworks/data/LOCAL_CORPUS_FAMILY_INDEX.json
fe572ee4d332dc356d9ddf6edb28a7ca5736de6038bf0389d1b7b74165fa42df  puckworks/data/MANIFEST.csv
c076fc76c36dff31f817d75bd9b397787b5188cffa5122d849b565b701c1efec  puckworks/data/egidi2024/PROVENANCE.md
1b5cd8891472d2d432fcb96a59e167d8fcca8b8e70a0a75187d810bf8a8e4419  puckworks/data/egidi2024/table2_egidi2024_tds_ey.csv
2c5fae8319d41c690b7e23ea00ddfc722e08c01ebcd8f012dafb1820a8fc6703  puckworks/data/perticarini2024/ey_tds_cibao.csv
bcc1b6f9a3bab6566977aa2ee682523cdd2b4175c75cdfbe28ec4699d3e6bc90  puckworks/insights/extract.py
92edc42d13d584ae13fe3afca5c4badc35be807f2560e80d6461599b009bc49c  tests/insights/test_foundry.py
1eb815f1fbb1510496a3ddb1859cb0d75faf6d375d39d1e5c7b458a1b7ebe90a  tests/test_perticarini2024_pressure_grind.py
f0d6144b1e5de3207ef58935932b5f4130a00d7159add4434306cf188b6679b2  tools/build_available_data_register.py
daac99e08d469f8151d130de33c50a6e6534ee7fcaed5e42503c2290cd65756e  tools/build_local_corpus_family_index.py
```
