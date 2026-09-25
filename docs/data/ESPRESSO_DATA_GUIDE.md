# External espresso data — start here

An external espresso research collection exists beyond this checkout. It contains
published-source tables and digitizations, Pannusch/Schmieder workbooks and author
code, permissioned machine histories, and prior private analysis/simulation outputs.

<!-- snapshot:start -->
**Checked 2026-09-23 UTC** (local evening may be the preceding date): 1 declared root, **31,503 regular files / 4,482,119,523 bytes** (4.482 GB apparent file bytes), 17,859 unique byte contents; 39/39 registered source families found. Status: `SCANNED_WITH_DECLARED_LIMITS`. Full hash census; bounded structural inspection and sampled semantic review. Protected sources and private generated outputs are hash-only. No corpus-wide observation count is established.

Snapshot identity: `f46181ee8c461fab055b73511148dd26888c7c5b3cb1bc908aad6ab9db2bb766`. [Machine-readable snapshot](../../puckworks/data/LOCAL_CORPUS_SNAPSHOT.json).
<!-- snapshot:end -->

Use hydraulic evidence from **waszkiewicz2025**, fraction delivery from
**pannusch2024 / schmieder2023**, material/structure evidence from **G10,
Wadsworth, Vaca and Maillé**, and operating histories from **visualizer**. The
question table below distinguishes their uses. These are discovery metadata,
**not a new scientific qualification or a production dependency update**.

Local agents resolve the owner-controlled collection and private manifest through
`PUCKWORKS_EXTERNAL_DATA_ROOT` or `~/.config/puckworks/data_sources.json` (explicit
`--root` overrides the environment). Browser-only agents can read this guide,
source cards, registers and committed normalized subsets; they cannot retrieve
private source files by following a GitHub link. Missing local access means
**known evidence unavailable in this environment**, not nonexistent or exhausted.
Repository-only recommendations may proceed provisionally with that limitation.

## Choose evidence for a question

| Question | Family / canonical dataset IDs | What is available now; maximum useful scope |
|---|---|---|
| Hydraulic pressure response | `waszkiewicz2025/traces_per_brew`, `waszkiewicz2025/traces_time_dependent` | Processed line/basket pressure, mass and derived flow; controlled source-internal reconstruction and baselines. Preserve 56-brew grouping and accepted negative adoption results. |
| Extraction / fraction delivery | `pannusch2024/experimental_kinetics`; `schmieder2023/raw_fractions` | Shot/fraction mass and analytes, source inputs and replicate structure; source reconstruction, observation operators and source-internal comparisons. Shared campaign, no independent doubled cohort. |
| Material properties | `g10_liquor_rheology/telisromero2001_tables`, `sobolik2002/rheology` | Measured-table transcriptions versus digitized/refitted/computed viscosity subsets; bounded property sensitivity, with industrial-extract transfer and extrapolation limits. |
| Structure / PSD | `wadsworth2026/table1_full`, `vacaguerra2023a/dry_porosity_validation`, `maille2024/psd_dispersion` | Source-specific PSD, porosity, surface/transport descriptors. Separate priors/operators; no common cross-source shot join or universal dial conversion. |
| Wetting / bed change | `foster2025_2`, `hargarten2020`, `mo2023_2` families | Front/headspace digitizations, swelling anchors and model curves; source reconstruction and mechanism sensitivity. No newly discovered synchronized wet-bed/pressure/chemistry campaign. |
| Temperature | Pannusch programmed-temperature subsets; G10 property tables; Egidi endpoint table | Controlled/set temperatures and source-specific property response. No verified local puck-temperature field; programmed temperature is not a measured spatial boundary. |
| Machine operating histories | `visualizer/hydraulic_timeseries`, `gagne2021` family | Time-series structure and descriptive operating envelopes. Machine pressure is not qualified puck-inlet pressure; user outcomes are separate from chemistry. |

The family sections link every registered subset to its source locator, units,
extraction method, rights and caveat. Exact private file/member locators and hashes
are in the private manifest, not this page. Source cards supply the DOI/citation,
apparatus and reported conditions; a missing condition is **UNKNOWN**, not a default
espresso recipe. A source paper's full supplement must not be inferred from a card.

## Access and three non-scoring entry commands

From a Puckworks checkout, use a Python environment with `openpyxl`, `xlrd`, NumPy
and SciPy for workbook/array readers; unavailable optional readers produce explicit
parse diagnostics. The census itself needs only Python's standard library.

The existing configuration `sources` records retain their original meaning. The
optional top-level `inventory` object locates this task's private output and root:

```json
{"inventory": {"root": "OWNER_LOCAL_COLLECTION", "manifest": "OWNER_PRIVATE_MANIFEST"}}
```

The commands below assume the owner has added this `inventory` locator after a
scan. For first-time use, set `CORPUS_ROOT` and `PRIVATE_OUTPUT` to explicit
authorized paths, run the scan command in the next section, then set
`PRIVATE_MANIFEST="$PRIVATE_OUTPUT/manifest.json"`; configuration is optional.
`XDG_CONFIG_HOME` is supported by the resolver.

These are placeholders for owner-local absolute paths; never commit the filled
configuration. Pannusch's existing `sources.PANNUSCH2024_MENDELEY_FULL_REPOSITORY.path`
continues to locate the collection or its extracted source repository. A configured
collection root is recognized by its registered family subdirectories before
applying a source-specific root mapping. The CLI adds accessible, explicitly
registered roots, deduplicates roots already covered by the explicit root, records
unavailable references, and never searches unrelated directories.

```bash
# Run in the Puckworks checkout. Read local configuration without echoing it.
CORPUS_ROOT=$(python3 -c 'import json,os; from tools.inventory_local_corpus import config_path; c=json.loads(config_path().read_text()) if config_path().exists() else {}; print(os.environ.get("PUCKWORKS_EXTERNAL_DATA_ROOT") or c.get("inventory",{}).get("root",""))')
PRIVATE_MANIFEST=$(python3 -c 'import json; from tools.inventory_local_corpus import config_path; print(json.loads(config_path().read_text())["inventory"]["manifest"])')

# Each query resolves local files, rehashes them, and prints only identity/structure.
# Output includes PRIVATE local locators: keep it outside Git.
python3 tools/inventory_local_corpus.py query "$PRIVATE_MANIFEST" --family waszkiewicz2025
python3 tools/inventory_local_corpus.py query "$PRIVATE_MANIFEST" --family pannusch2024
python3 tools/inventory_local_corpus.py query "$PRIVATE_MANIFEST" --family telisromero2001
```

These inspect a hydraulic CSV family, original XLS/XLSX/array source repository,
and Markdown property-table transcriptions respectively. Queries do not score,
calibrate or invoke corpus code. Structural summaries refer to the verified scan;
`identity_matches_snapshot: false` means they must not be trusted for the changed
file. Existing scientific loaders are in `puckworks/data/__init__.py`; qualified
Pannusch exports and source adapters remain the authorities linked by its card.
Do not substitute a generic workbook parse for that reconstruction.

## Refresh without changing scientific authority

```bash
# Choose a NEW private output directory OUTSIDE the source collection.
python3 tools/inventory_local_corpus.py scan --root "$CORPUS_ROOT" --output "$PRIVATE_OUTPUT"
# Optional --compare-repo "$EWP_CHECKOUT" identifies byte copies there too.
python3 tools/inventory_local_corpus.py compare "$PRIVATE_MANIFEST" "$PRIVATE_OUTPUT/manifest.json" --output "$PRIVATE_OUTPUT/changes.json"
python3 tools/inventory_local_corpus.py validate "$PRIVATE_OUTPUT/manifest.json"
python3 tools/inventory_local_corpus.py project "$PRIVATE_OUTPUT/manifest.json" --output puckworks/data/LOCAL_CORPUS_SNAPSHOT.json
python3 tools/build_available_data_register.py
python3 tools/build_local_corpus_family_index.py
python3 tools/validate_local_corpus_coverage.py
python3 tools/build_espresso_data_guide.py
python3 -m pytest -q tests/test_inventory_local_corpus.py tests/test_local_corpus_family_index.py tests/test_available_data_register.py tests/test_espresso_data_guide.py
```

`MANIFEST.csv` owns dataset identity/provenance/rights; source cards own scientific
interpretation; `build_available_data_register.py` owns its curated capability
fields; `build_local_corpus_family_index.py` owns reviewed family aliases and
curated discovery notes. The new snapshot stores only observed aggregate counts.
Refreshes never infer new scientific eligibility, change accepted receipts, or
update EWP's production lock. Review amended curated notes separately. Snapshot
identity excludes times, root absolute paths and runtime details; it includes
relative entry identities, sizes, stable hashes and mappings. Same content and
mapping yield the same identity on a rescan. Copies are not new experiments.

The scanner records directories, files, links, inaccessible entries and excluded
output subtrees, streaming SHA-256 with before/after metadata checks, then rechecks
the entry set. This is an interval census, not an atomic snapshot. Symlinks are
recorded and never followed (two of seven targets lexically leave the declared
root; private locators retain those references). Hardlink entries contribute apparent file bytes,
not distinct allocated disk blocks. Hash duplicates do not prove experimental
independence; different hashes do not prove distinct shots.

Readers never execute source scripts, notebooks, macros or pickled objects.
Archives are inspected in memory, without extraction, with traversal/link checks,
a 64 MiB member/read bound, 256 MiB expansion budget per physical archive,
10,000-member bound and depth two. Unsupported, malformed, encrypted or
limit-exceeding content remains an explicit exception. CSV comments and semicolon
variants are recognized; ragged tables and malformed quotes are not zero data.
Workbook sheet rows include headers and blanks. Array shapes are not observations.

Private outputs and protected/reserved paths receive hashes only. All Angeloni
material is conservatively hash-only. This task exposed ordinary already-public
source values and Pannusch workbook preview values (already target-exposed source
lineage), but no new protected target values, no scoring and no model outputs from
private analysis. Semantic review covered 38/39 registered source families (Angeloni excluded) through
headers, source notes and distinct format strata; it did not read every numerical
cell or transcribe every paper. Three distinct held PDFs received metadata and
first-two-page text inspection; no OCR was run. Private analysis groups remain lineage inventories,
not freshly reviewed scientific results. Source-specific claim ceilings persist.

## Reconciliation and exceptions

<!-- reconciliation:start -->
36,531 entries: 31,503 regular files, 7 symlinks; 31,503/31,503 files hashed, 0 unreadable entries, 0 unstable files, 0 concurrent entry changes, 0 excluded output subtrees, 0 unavailable roots. Hardlink extra entries: 123.

354 physical files received full lightweight structured parsing; 582 physical archives/compressed streams yielded 1,885 logical member entries (759 parsed structures, 303 parse failures). 562 archive members match physical file hashes. Physical parse failures: 3; ragged tables: 2. These are inspection denominators, not experimental observation totals.

8,694 files match inspected repository bytes; 10 same-path canonical comparisons differ. 30,113 files do not map to a registered source-family directory; private reconciliation retains every group and locator. Other registered datasets absent from this external root may still be packaged in Git. A found family does not certify every registered subset or every source supplement.

| Provisional content role | Physical files | Apparent bytes |
|---|---:|---:|
| author_code | 57 | 256,373 |
| digitized_figure | 8 | 27,906 |
| experimental_measurement | 225 | 9,078,948 |
| literature | 5 | 11,496,812 |
| machine_log | 596 | 260,810,148 |
| model_output | 2,984 | 1,031,331,543 |
| normalized_data | 174 | 8,872,374 |
| private_analysis | 27,365 | 3,001,708,908 |
| unrelated | 0 | 0 |
| unresolved | 89 | 158,536,511 |

The canonical MANIFEST contains 115 dataset rows; 108 IDs route through the reviewed family index. Remaining canonical rows: `acre2024/tables1_2`, `de1_fixtureA`, `dias2015/table2`, `pannusch2024 (Mendeley repo)`, `sci_md_007_r1/registers`, `viencz2023/tables1_2`, `wadsworth2026_table1`. These are reconciled below, not silently omitted.

Roles are conservative routing classifications; mixed/unknown files remain unresolved. Duplicate groups are an orthogonal field in the private manifest, not a second experiment class.
<!-- reconciliation:end -->

The historical 39-family index is a reviewed scientific-family register, not a
current disk census. All other top-level material is accounted for privately:
completed Visualizer preflight/play/machine-prior programmes, the hydraulic
feasibility contract, an earlier data assessment with repository/virtual-environment
snapshots, root-level helpers/manifest/templates and bytecode. These are generated,
code, administrative or unresolved holdings, not newly declared experiments.
Their exact group counts, paths and next bounded lineage-review step are in
`reconciliation.json` beside the private manifest. No unknown group is silently
assigned an established dataset ID. Nested repository copies do not become new
source families.

Additional canonical rows outside the historical 39-family index:

- `de1_fixtureA` and `wadsworth2026_table1`: root-level files are held and hashed;
  these are existing fixture/compact-table records, not new independent families.
  Their private rows retain exact repository-byte matches where present.
- `pannusch2024 (Mendeley repo)`: historical whole-repository intake alias for the
  now-recovered Pannusch family, not an additional experiment or missing source.
- `acre2024/tables1_2`, `dias2015/table2`, `viencz2023/tables1_2`,
  `sci_md_007_r1/registers`: canonical repository/source authority exists, but no
  corresponding original source-family directory was found in this external root.
  Check the packaged SCI-MD-007 material registers and source cards. This census
  does not certify an external original for those rows.

Objective discrepancies retained without rewriting scientific history:

- **Cameron PSD:** a 618-bin local PSD table is held, but the family has only the
  figure-5 deviation dataset registered. This is a provisional, unregistered
  subset; verify source/rights provenance and assign a reviewed subset ID before
  scientific use. It is not a newly discovered physical campaign.
- **Smrke:** the source card's intake-time “supplement not held” statement is
  historical. Fig S1 digitization is now present; native raw logs are not established.
- **Schulman:** the initial reader failed on quoted comments/header layout. The
  final comment-filtered receipt recovered 14 structurally consistent rows; this
  corrects the stale parse warning, without qualifying a pressure-loss experiment.
- **Pannusch:** old local PROVENANCE text still says “deferred” and describes an
  earlier center-grind approximation. Use the newer qualified canonical register
  and reconstruction; this task did not newly recover the already-recovered corpus.
- **Previously reported unavailable:** EWP [open PR #117](https://github.com/trbrewer/espresso-whole-pull/pull/117)
  reported no Visualizer store in its checked repository/predecessor locations.
  This external-root census finds the store and its compressed raw/normalized
  families. That location-specific absence must not be generalized to this
  collection; the later accepted private-work record already documents its use.
- **Visualizer:** older catalog readiness labels precede completed private empirical
  and EWP work. Read the [EWP private work record](https://github.com/trbrewer/espresso-whole-pull/blob/main/docs/analysis/data_leverage/VISUALIZER_PRIVATE_WORK_RECORD.md)
  for current decision-specific limits; no raw-publication clearance follows.
- **Waszkiewicz:** 57 source labels versus 56 physical brews is documented duplicate
  lineage, not a discovered independent replicate. The existing negative scientific
  dispositions are unchanged.
- **Same-path mismatches:** ten individually tracked differences are listed below.
  A pathname is not a content identity; the local versions are not substitutes for
  accepted hash-bound inputs. No original or historical receipt was overwritten.
- **MATLAB/text:** opaque MATLAB table objects and legacy text encodings cause
  explicit parse failures. The qualified Pannusch adapter, not unsafe object loading,
  is the bounded recovery path. Archive resource-fork members also fail parsing;
  those failures do not erase the corresponding intact source files.

Reopen a scientific disposition only for a named material change in source
semantics, compatible input/observation mapping or genuinely different question,
with the relevant prior-use record cited. A recovered file or successful parse
alone does not reopen a negative result.

### Historical identity differences

Comparison authority is Puckworks base `2058d0e947ee9eb92c52d64f6165b810f1fb4732`.
The private `final-review-mismatches.json` beside `RESULT.json` pairs each observed
snapshot hash with that base's exact Git-blob SHA-256 and locator. These public
record IDs are inventory exceptions, not newly qualified dataset IDs. Except for
DCG-M06, the originating version and impact on accepted scientific inputs remain
**UNKNOWN**; metadata differences must not be presumed harmless or used to
invalidate prior results. Resolve a proposed use against its own accepted receipt.

| Record ID | Public counterpart / dataset scope | Inspection and provenance limit |
|---|---|---|
| DCG-M01 | Root intake record (`BLOCKED_INTAKE.md`) | Hash-only local administrative copy; historical authority/impact UNKNOWN. |
| DCG-M02 | Root dataset register (`MANIFEST.csv`) | Hash-only local register copy; no silent replacement of canonical dataset identities. |
| DCG-M03 | Root loader (`__init__.py`) | Hash-only author-code copy; not executed; historical consumer overlap UNKNOWN. |
| DCG-M04 | `grudeva2025` provenance record | Text decoded; scientific/rights equivalence not established. |
| DCG-M05 | `pannusch2024` provenance record | Text decoded; earlier intake account is not current reconstruction authority. |
| DCG-M06 | `pannusch2024/experimental_kinetics` | Structured 90-row export; verified legacy/corrected distinction below. |
| DCG-M07 | `vacaguerra2023a` provenance record | Text decoded; impact on accepted porosity/source interpretation UNKNOWN. |
| DCG-M08 | `visualizer` provenance record | Text decoded; no redistribution grant or accepted-input equivalence inferred. |
| DCG-M09 | `wadsworth2026/table1_full` provenance record | Text decoded; accepted scientific-input impact UNKNOWN. |
| DCG-M10 | `waszkiewicz2025` provenance record | Text decoded; accepted scientific-input impact UNKNOWN. |

**Known scientific lineage overlap (DCG-M06):** the observed local hash equals
`base_file_sha256` in the existing
[kinetics correction ledger](../../puckworks/data/pannusch2024/experimental_kinetics_correction_ledger.json),
whereas the compared canonical file equals `candidate_file_sha256`. The accepted
PANNUSCH-RAW-REPRO-001 correction excluded spilled samples from valid-only means;
its [metric attribution](../../puckworks/data/pannusch2024/metric_attribution.json)
already records downstream metric effects without parameter refitting. The legacy
hash also appears in the historical
[SCI-MD-004 training contract](../analysis/sci_md_004_stage_e0/training_contract.json).
This is a traced, previously documented scientific-input difference, **not source
equivalence** and not a new adjudication of that historical result. Preserve both
versions and receipts. Any untraced downstream adoption remains UNKNOWN; a proposed
reuse must name its accepted input hash and consult the existing correction before
seeking separate adjudication of an actual conflicting claim.

### Inspection exception lookup

The private manifest is the exact-file/member lookup; the following public records
make limitations selectable without exposing private locators. Content role and
inspection state are separate: an unresolved role does not mean unreadable data.

| Exception ID / scope | Permitted state, reason and bounded next step |
|---|---|
| DCG-E01 / `angeloni2023` | All material hash-only under protected-source restrictions; no target exposure. Nine files fall in the unresolved-role class. Consult the existing holdout contract before any deeper inspection. |
| DCG-E02 / 89 unresolved-role physical files | 12 generated/unmapped hash-only; 9 protected hash-only; 23 format-not-parsed; 22 decoded text without file-level semantic review; 20 structurally parsed; 2 bounded archives; 1 parse failure. These disjoint states total 89. Exact family/locator routing is retained privately. Review role/lineage for the selected question, never infer 89 failed datasets. |
| DCG-E03 / `pannusch2024` MATLAB array | One physical `Experiments.mat` parse failure: TypeError on opaque MATLAB content. Use the qualified source adapter or a separately authorized safe export; do not deserialize unsafe objects. |
| DCG-E04 / `pannusch2024` author code | Two physical MATLAB-text failures (`controlfunctions.m`, `physical_parameters.m`): UnicodeDecodeError. A bounded encoding-aware text read is the next step; do not execute code. Together E03/E04 account for all three physical parse failures. |
| DCG-E05 / `g10_liquor_rheology` | Ragged liquor-rheology table; exact bytes match the canonical table. Check documented row/header conventions before an adapter; raggedness alone does not invalidate the measurements. |
| DCG-E06 / `g1_glassbead_analog` | Ragged retention table; exact bytes match the canonical table. Check row/header conventions before a source-specific reader. E05/E06 account for both ragged physical tables. |
| DCG-E07 / `schulman2011/basket_geometry` | Initial strict-reader problem with quoted comments/header retained as history. Final comment-filtered receipt: 14 rows, six columns, consistent widths; not a physical PARSE_FAILED entry. Check geometry conventions against the source card before scientific use. |
| DCG-E08 / archive members | 303 member parse failures, all in Pannusch archives: 128 UnicodeDecodeError, 92 ValueError, 70 XLRDError, 12 BadZipFile, 1 TypeError. Resource-fork/opaque or encoding-incompatible members remain explicit exceptions. They are not 303 additional physical failures or absent experiments. Use the private member diagnostic to select one relevant member; retain depth/size/traversal limits and never execute archive code. |

## Curated task outcomes

[SCI-MD-MO-TRANSFER-001](../analysis/sci_md_mo_transfer_001/RESULT.md) implemented an analysis-only conservative S0/S2/D2 reference and audited all 51 supplied rows. Both absolute transfer axes remain `BLOCKED_SOURCE_CONTRACT`; numerical application is separately `NUMERICALLY_UNRESOLVED`. Original institutional manuscript inspected; no real fit/score or production integration. Historical reconstruction remains unchanged.

## Publication and storage

No raw data, screenshots, real sample records, permission correspondence or large
assets are uploaded by this task. Source access, technical readability, scientific
eligibility and redistribution permission are four separate axes.

| Material | Recommendation and actual rights boundary |
|---|---|
| Small cleared normalized tables | Existing Waszkiewicz/Wadsworth CC-BY factual subsets are candidates for ordinary Git, with per-source attribution and provenance; preserve current source notices. No new data upload here. |
| Pannusch full source (~305 MB including copies) | Prefer the authoritative Mendeley v1 locator `10.17632/y2tz67f6ry.1`. Local provenance states CC-BY-NC-3.0; a later curated fraction/PSD bundle must retain noncommercial terms and separate author code/binaries. A versioned archive is more suitable than bulk Git. |
| Schmieder workbooks/paper/derived tables (~111 MB including copies) | The held article first page explicitly states CC BY (4.0 link); prefer the publisher supplement and DOI/card. A compact workbook-derived fraction bundle is useful after confirming the supplement inherits that grant and preserving shared Pannusch lineage. Article, data and derived fits are separate materials. |
| Smrke digitizations | Useful later flow/PSD observation bundle under the source's CC-BY-4.0 statement, with figure/algorithm attribution and pixel uncertainty. It cannot be marketed as native machine measurements. |
| Visualizer | Keep raw/bronze/normalized records and private analyses external. Inspected provenance records research-use permission and collective user attribution, explicitly withholding raw redistribution. Public permission status is owner-attested. Original permission correspondence was not located in scoped roots; any broader grant remains UNRESOLVED and needs the owner's original grant, not an application-code MIT license. |
| Paywalled papers, rheology tables, community material | Retain papers externally and reference source cards. Compact factual transcriptions already have bounded rights records; publication of original tables, rheograms or images needs source-specific clarification. Do not apply repository software MIT terms to them. |
| Grudeva code/data | Follow the existing [permission record](../permissions/grudeva2025.md), with its stated scope and attribution. Permission is not an SPDX license and is not a blanket grant for other sources. |
| Private output, correspondence and unknown licenses | Keep external. Review ownership, source grant and disclosure risk per proposed subset before any future release. |

Most useful later bundles: an attributed source-internal fraction-delivery package
(Pannusch/Schmieder with deduplicated lineage), a controlled hydraulic observation
package (Waszkiewicz), and a digitization-aware structure/flow package (Smrke).
These are recommendations for separate rights review, not uploads or acquisitions.

## Family and subset guide

The following projection is generated from the existing canonical sources. Counts
are current disk files/bytes, not scientific replicates. `UNKNOWN` counts mean no
verified physical-shot count was established. For every subset, its quoted units
and provenance retain their source conventions; no implicit basis conversion or
cross-campaign join is supplied. Source cards document apparatus/coffee/conditions
when available. Unreported sampling origin, resolution, lot and uncertainty remain
unknown and require that source's bounded metadata recovery.

<!-- families:start -->
### angeloni2023

**Access:** FOUND on 2026-09-23; 16 files / 151,147 bytes; 0 structured files, 15 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

Fraction and endpoint chemistry; protected comparison lineage. Existing source cards and manifest carry analyte, basis and fraction details.

Source-conditioned extraction comparison only under its existing exposure contract. Hash-only this census; no target values or headers opened. Next step is a contract-authorized reader, not automatic reuse.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `angeloni2023/inventories` — [angeloni2023](../cards/angeloni2023.md); Table 7 | transcription (article tables; no repository); published: mg/L (=mg/kg); registry: mg/L | Angeloni et al. Appl. Sci. 2023, 13, 2688 (MDPI, open access; Cloudflare-blocked for fetch); 8 species x 2 varieties; the 66-shot chemistry (Tables 2-5) is a PENDING drop -- not in card, MDPI unreachable |
| `angeloni2023/bioactives` — [angeloni2023](../cards/angeloni2023.md); Tables 4+5 joined to Table 1 | transcription (article tables, xlsx drop); published: g/L; C; bar; registry: g/L; C; bar | Angeloni et al. Appl. Sci. 13 (2023) 2688 (MDPI, open access; Cloudflare-blocked for fetch); transcribed from article tables, no repository; 66 shots (33 A + 33 R); 11 species; on_grid flags 54 calib vs 12 off-grid; 'Average' row dropped \| PER-CONDITION analysis (gate_pannusch_angeloni_per_condition) maps angeloni pressure->flow by a REFINED Darcy map q~p/mu(T) (registered water viscosity; single physical anchor, granulometry O; NOT fitted to the concentrations); a crude linear-tau baseline is also available. The refinement closes ~5 pp of the gap (31->26% overall; caffeine to ~15% with inventory-matching). The residual >> angeloni's ~9-13% is cross-coffee INVENTORY + per-species KINETIC mismatch, not flow -- closable only by refitting to the angeloni coffee. Treat per-condition MAPE as regime-level, not accuracy-grade. |
| `angeloni2023/total_solids` — [angeloni2023](../cards/angeloni2023.md); Table 2 joined to Table 1 | transcription (article tables, xlsx drop); published: g/100mL; %; registry: g/100mL; % | Angeloni et al. Appl. Sci. 13 (2023) 2688 (MDPI, open access; Cloudflare-blocked for fetch); transcribed from article tables, no repository; 66 shots; TS g/100mL ~ TDS %; cameron reads ~2-4 pts LOW (bracket miss, informative) \| PER-CONDITION analysis (gate_pannusch_angeloni_per_condition) maps angeloni pressure->flow by a REFINED Darcy map q~p/mu(T) (registered water viscosity; single physical anchor, granulometry O; NOT fitted to the concentrations); a crude linear-tau baseline is also available. The refinement closes ~5 pp of the gap (31->26% overall; caffeine to ~15% with inventory-matching). The residual >> angeloni's ~9-13% is cross-coffee INVENTORY + per-species KINETIC mismatch, not flow -- closable only by refitting to the angeloni coffee. Treat per-condition MAPE as regime-level, not accuracy-grade. |
| `angeloni2023/lipids` — [angeloni2023](../cards/angeloni2023.md); Table 3 joined to Table 1 | transcription (article tables, xlsx drop); published: g/100mL; %; registry: g/100mL; % | Angeloni et al. Appl. Sci. 13 (2023) 2688 (MDPI, open access; Cloudflare-blocked for fetch); transcribed from article tables, no repository; 66 shots |
| `angeloni2023/total_solids_lipids_rsd` — [angeloni2023](../cards/angeloni2023.md); Appl. Sci. 13,2688 Tables 1-3 (author-deposited PDF, hashed) | transcription (programmatic parse + independent check; TB-2 handoff 2026-07-13); published: g/100mL (TS/lipid); percent (RSD); registry: g/100mL; percent; sd_reconstructed=\|mean\|*RSD/100 | Angeloni et al. Appl. Sci. 13 (2023) 2688 (MDPI open access); author-deposited PDF hashed; 66 conditions x (TS+lipid)=132 mean/RSD pairs; 'almost in duplicate' n_reported=2 qualified; A21 lipid RSD printed 0.0% = rounded (apply variance floor, not infinite weight); caffeine/trigonelline/CGA solute-specific RSD NOT recovered (Tables 4-5 give only global ranges 0.3-19.7%); raw replicates still owed. See angeloni2023/MANIFEST_UNCERTAINTY.md + docs/data_intake/ANGELONI_TRANSCRIPTION_AUDIT.md. |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### bruno2026

**Access:** FOUND on 2026-09-23; 2 files / 12,345 bytes; 2 structured files, 2 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

Roasted-composition long table: 40 compound/source rows; wide table: 10 compound rows for four origins. mean, sd, unit, basis and n_measurements are explicit columns.

Upstream roasted-inventory context and uncertainty priors; long/wide are alternate representations, not independent batches. No matched brew, pressure or fraction delivery.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `bruno2026/roasted_composition` — [bruno2026](../cards/bruno2026.md); Bruno et al. Sci. Rep. 16, 15857 (2026) Table 2 (4 origins x 10 compounds, mean±SD, n=3) | transcription (open PDF); published: mg/kg; % w/w; registry: mg/kg; % w/w | CC BY 4.0 (Scientific Reports, open access); Roasting is UPSTREAM of every registry stage -> DATA-ONLY (the Bruno ODE model is NOT implemented, per card: over-parameterised non-identifiable fit). mg/kg roasted powder (non-lipid); lipids % w/w dry basis. Bean-averaged; no solubility/diffusivity/partitioning (bruno card) -> use as an inventory PRIOR only, never Bruno-ODE -> extraction. Medium Arabica (Mexico/Rwanda) + hard-roast Robusta (Nicaragua/Indonesia). |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### cameron2020

**Access:** FOUND on 2026-09-23; 2 files / 20,094 bytes; 2 structured files, 2 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

Figure 2 PSD: 618 diameter bins, particle_diameter_um and four volume-percent grind columns. fig5_grind_deviation has three points.

The PSD file is a provisional subset without its own MANIFEST row; fig5_grind_deviation does not register it. Verify its source/rights locator before adding a stable subset ID. Grind-specific PSD and coarse/fine behavior reconstruction. Bins are not shots; dial cannot be mapped to a different grinder. Local holdings do not imply the entire experimental supplement.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `cameron2020/fig5_grind_deviation` — [cameron2020](../cards/cameron2020.md); Matter 2, 631-648 (2020) Fig 5 (measured EY deviation below the homogeneous-flow model vs grind) | transcription (values stated in the streamtube module docstring, from Cameron Fig 5); published: percent; registry: fraction | paper (DOI 10.1016/j.matt.2020.06.019); 3 in-campaign grinds GS 1.1/1.3/1.5 (rel deviation 0.131/0.061/0.026); LOO over only 3 points |
| `cameron2020/psd_figure2` — [cameron2020](../cards/cameron2020.md); Figure 2 (measured PSD) | figure digitization (volume% vs diameter, 4 grind settings); published: um ; volume percent; registry: um ; volume percent | Cameron et al., Matter 2 (2020) 631-648; Fig 2 PSD digitized 2026-07-25; Gs 1.0/1.5/2.0/2.5, ~1-1900 um; enables maille's phi closure to be applied to Cameron's grind (an extrapolation above maille's own coarse-grind range) |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### egidi2024

**Access:** FOUND on 2026-09-23; 2 files / 1,830 bytes; 1 structured files, 2 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

table2_egidi2024_tds_ey: 12 condition rows, T [degC], p [bar], tau [s], Granulometry, TDS [%], TDS sigma, EY [%].

Endpoint condition contrasts; no measured pressure history, fraction chemistry or individual shot join. Replicate identities UNKNOWN in held table.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `egidi2024/table2` — [egidi2024](../cards/egidi2024.md); Chaos Solitons Fractals 188,115625 Table 2 (12-cond EY/TDS) | digitization (Tim); published: C; bar; s; percent; registry: C; bar; s; percent | paper (DOI 10.1016/j.chaos.2024.115625); p,T absorbed into q,tau (egidi); EY 19-23%; cameron reads ~15% (below bracket, documented); rho/phi_s undefined in Eq4 (§5.8) |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### ellero2019

**Access:** FOUND on 2026-09-23; 8 files / 85,869 bytes; 7 structured files, 8 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

Figures 2–4 contain nondimensional t_over_tnu, Reynolds number, applied forcing and concentration curves across theta, Db and Dr; reference-8 experimental Reynolds points are separate.

Numerical/source reconstruction and mechanism sensitivity. Most curves are model output; the experimental digitization is not a new experiment or an espresso chemistry validation target.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `ellero2019/fig2_inverse_discharge` — [ellero2019](../cards/ellero2019.md); Ellero & Navarini PARTICLES 2019 Fig 2 (forcing; SPH \|Re\|(t/tnu) x6 theta; Ref.[8] experimental markers) | digitization (pixel extraction from screenshots; axis fit <1px); published: t/tnu; \|Re\|; F/F0 (dimensionless); registry: same | no DOI (conference proceedings); figures digitized, no PDF redistributed; SPH model OUTPUT in dimensionless sim units with NOMINAL parameters -> characterizes the MODEL, not coffee (card VERDICT: skip). theta=0.0058 is FIT to the flow data (circular at that theta). Pump-off windows (t/tnu ~37.6-52.6, 75.2-90.2) read as Re~0. Only the fig2 Ref.[8] markers are experimental (secondary ref, overlaid). Does NOT close G2 -- the raw ASIC 1993/1997 transient-discharge series (refs [13]/[18]) is still owed. |
| `ellero2019/fig3_direct_discharge` — [ellero2019](../cards/ellero2019.md); Ellero & Navarini PARTICLES 2019 Fig 3 (direct-discharge SPH \|Re\|(t/tnu) x4 theta; cumulative output concentration [%] x4 theta) | digitization (pixel extraction); published: t/tnu; \|Re\|; percent (dimensionless); registry: same | no DOI (conference proceedings); figures digitized; Exploratory parameter sweep, NO experimental comparison (card). Simulation units, nominal params -> model characterization, not coffee. Blue curve near-legend gap bridged by column median (notes). |
| `ellero2019/fig4_caffeine_content` — [ellero2019](../cards/ellero2019.md); Ellero & Navarini PARTICLES 2019 Fig 4 (caffeine content [%] vs t/tnu: vary Db @Dr=0.0005; vary Dr @Db=0.005; theta=0.0058) | digitization (pixel extraction); published: t/tnu; percent (dimensionless); registry: same | no DOI (conference proceedings); figures digitized; Exploratory sweep, NO experimental comparison. Simulation units, nominal params. Supports the mechanism claim qualitatively (content rises with Dr, weakly with Db); not a coffee measurement. |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### fasano2000_partI

**Access:** FOUND on 2026-09-23; 5 files / 4,730 bytes; 4 structured files, 5 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

fig8_1: pressure_bar/time_s/discharge_ml_s; fig8_4: direct/inverse segment traces; figures 8.6–8.7 carry asymptotic and threshold curves.

Pressure-response shape and qualitative fines-mechanism context. Separate digitized observations from theoretical curves; published apparatus and original clocks are needed for transfer.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `fasano2000_partI/fig8_1_experimental` — [fasano2000_partI](../cards/fasano2000_partI.md); Fig 8.1 | digitisation (raster, schematic); published: bar; s; mL/s; registry: bar; s; mL/s | Fasano/Talamucci/Petracco, Complex Flows in Industrial Processes ch.8, Springer 2000 (no DOI; no code/data); digitized figures; low fidelity; 3/5/7 bar; transient peak then decay to a pressure-nonmonotone asymptote |
| `fasano2000_partI/fig8_4_reversal` — [fasano2000_partI](../cards/fasano2000_partI.md); Fig 8.4 | digitisation (raster); published: s; mL/s; -; registry: s; mL/s; - | Fasano/Talamucci/Petracco, Complex Flows in Industrial Processes ch.8, Springer 2000 (no DOI; no code/data); digitized figures; 3 segments: direct decay / off-on resume at low plateau / inverted replays full peak |
| `fasano2000_partI/fig8_6_model_q_inf` — [fasano2000_partI](../cards/fasano2000_partI.md); Fig 8.6 (mu=0.5) | digitisation (raster); published: -; registry: - | Fasano/Talamucci/Petracco, Complex Flows in Industrial Processes ch.8, Springer 2000 (no DOI; no code/data); digitized figures; nonmonotone q_inf(p0) for beta1,beta2; peak tracks the Fig 8.7 beta knee (Cor 8.2) |
| `fasano2000_partI/fig8_7_thresholds` — [fasano2000_partI](../cards/fasano2000_partI.md); Fig 8.7 | digitisation (raster); published: -; registry: - | Fasano/Talamucci/Petracco, Complex Flows in Industrial Processes ch.8, Springer 2000 (no DOI; no code/data); digitized figures; monotone-decreasing with a steep drop; beta1 knee ~q=0.33, beta2 knee ~q=0.23 |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### foster2025_2

**Access:** FOUND on 2026-09-23; 7 files / 30,068 bytes; 5 structured files, 7 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

fig6_front_position and fig8_headspace each have nine time points in seconds/mm with error columns. fig12_14 separates fitted and data front/bed/headspace; fig15 has normalized Q and headspace pressure.

Wetting/bed-change observation operators and source reconstruction. Nine points are not nine independent shots; normalized modeled machine response is not a measured inlet-pressure schedule.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `foster2025_2/params` — [foster2025_2](../cards/foster2025_2.md); Phys.Fluids 37,013383 Table I/II (transcribed from card) | transcription (from card); published: SI; registry: SI | paper (DOI 10.1063/5.0245167); fine grind fit; t_shift=0.796 start-align; reported t_p/t_s = model + t_shift; Fig 15 flow-min pending 0.11 |
| `foster2025_2/fig15_flow` — [foster2025_2](../cards/foster2025_2.md); Phys.Fluids 37,013383 Fig 15 (model-reproduced curve) | digitization/model-repro (Tim); published: s; -; -; registry: s; -; - | paper (DOI 10.1063/5.0245167); Q_norm = bed flow min(Qp,f)/Qm (Eq18); flow-min 0.181 @ t=2.0s; reproduced by solving Eqs 32-38, not pixel-traced |
| `foster2025_2/fig12_14_curves` — [foster2025_2](../cards/foster2025_2.md); Phys.Fluids 37,013383 Figs 12-14 (fitted curves + CT data) | digitization (Tim); published: s; mm; registry: s; mm | paper (DOI 10.1063/5.0245167); s_fit/H_fit = paper ODE (0.02s grid); s_data/H_data = pixel-digitized CT (5-line mean); Fig8 -H differs from Fig14 H (do not mix) |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### g10_liquor_rheology

**Access:** FOUND on 2026-09-23; 11 files / 23,613 bytes; 10 structured files, 11 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

Telis-Romero Table 1: 24 eta_Pas cells indexed by Xw_pct/T_K; Table 2: 27 K_Pasn/n cells. Khomyakov: 60 kinematic-viscosity cells indexed by solids fraction and temperature; regression/density conflicts are flagged.

Industrial extract property sensitivity. Water mass percent differs from solids fraction; kinematic viscosity needs an authorized density conversion. Quarantined regression cannot be silently used. No fresh-espresso rheometry.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `g10_liquor_rheology/telis_romero_envelope` — [g10_liquor_rheology](../cards/g10_liquor_rheology.md); Telis-Romero 2001 (J.Food Process Eng 24,217; DOI 10.1111/j.1745-4530.2001.tb00541.x) + 2000 (Int.J.Food Prop 3,375; DOI 10.1080/10942910009524642); 2013 cross-check DOI 10.1080/10942912.2013.833221 | transcription (abstracts/snippets + open 2013 xref; primary tables paywalled); published: Pa*s; kg/m^3; K; mass-fraction; registry: Pa*s; kg/m^3; K; mass-fraction | paywalled (Wiley/Tandfonline, bot-blocked here); ranges/forms from snippets + open 2013 xref; Sources measured INSTANT-COFFEE processing conc (dilute end 90% water); espresso TDS 4-12% solids is BELOW their range -> mu_espresso is EXTRAPOLATION toward pure water (~1.3-2x). Espresso IS Newtonian (validates single-mu assumption; power-law only >36% solids). Quantitative per-cell mu(T,c) needs Tim drop of Telis-Romero tables. No espresso-TDS measurement on file (new open sub-search). |
| `g10_liquor_rheology/telisromero2001_closures` — [telisromero2001](../cards/telisromero2001.md); Telis-Romero et al. J. Food Process Eng. 24 (2001) 217 (DOI 10.1111/j.1745-4530.2001.tb00542.x) Eqs (10)/(12)/(13) fitted closures + Table-1 eta / Table-2 K anchor points | transcription (closure coefficients + 2 measured anchors from card; primary tables paywalled/figure-and-table-only); published: Pa*s; Pa*s^n; K; %w/w water; registry: Pa*s; Pa*s^n; K; %w/w water | paywalled (Wiley, bot-blocked here); coefficients + anchors transcribed from docs/cards/telisromero2001.md, primary Tables 1-2 NOT redistributed; Industrial SOLUBLE-COFFEE extract (51 Brix, one batch), NOT espresso liquor -> unquantified composition bias (no oils/fines/CO2). Newtonian domain X_w 76-90%; power-law only >36% solids. Espresso TDS 4-12% solids sits at/below the source's dilute end -> mu EXTRAPOLATED toward water. Bulk shot-TDS mu ~=1.06x water (negligible); ~1.3-2x belongs to concentrated early in-pore liquor. Table1(24)/Table2(54) per-cell values NOT yet digitized (figure/table-only). Companion rho/thermal in telisromero2000 (card-only). |
| `g10_liquor_rheology/telisromero2001_tables` — [telisromero2001](../cards/telisromero2001.md); Telis-Romero et al. J. Food Process Eng. 24 (2001) 217 Table 1 (24 eta cells, Newtonian, X_w 76-90% x T 295-365K) + Table 2 (27 K + 27 n cells, power-law, X_w 49-64% x T 274-353K); source md in data/telisromero2001/ | digitization (Tim's drop, 2026-07-15; 2-3 sig figs off the paywalled tables); published: Pa*s; Pa*s^n; dimensionless; %w/w; K; registry: Pa*s; Pa*s^n; dimensionless; %w/w; K | paywalled (Wiley); tables digitized by author-side drop, not redistributed beyond this repo; CLOSES the OWED per-cell digitization. Cross-validates the transcribed closures (independent path) against the measured grid -> agreement at the authors' own fit quality confirms both. Table 1 spans exactly the espresso in-pore X_w range (76-90%); used directly (bilinear, data.telisromero_eta_measured) by analysis.g10_viscosity_sensitivity. Composition caveat (soluble-coffee extract != espresso liquor) + dilute-end extrapolation (espresso is >90% X_w, above the box top) stand. |
| `g10_liquor_rheology/telisromero2000_thermal` — [telisromero2000](../cards/telisromero2000.md); Telis-Romero et al. Int. J. Food Prop. 3(3) (2000) 375 (DOI 10.1080/10942910009524643) Eqs (1)/(3)/(4)/(6) direct rho/cp/k/alpha closures + Fig 2-5 endpoint/water-limit anchors | transcription (closure coefficients + figure-read/water-limit anchors from card; data published figure-only); published: kg/m^3; J/(kg*degC); W/(m*degC); m^2/s; degC; mass-fraction; registry: kg/m^3; J/(kg*degC); W/(m*degC); m^2/s; degC; mass-fraction | paywalled (Tandfonline, bot-blocked here); coefficients + anchors from docs/cards/telisromero2000.md, Figs 2-5 NOT digitized/redistributed; COMPANION to telisromero2001 (same batch family) -> mu/rho/cp/k/alpha(T,X_w) liquor set. X_w is a FRACTION here vs PERCENT in 2001 (normalization hazard -> loaders guard). Eq (6) alpha T-coeff has a ~100x EXPONENT TYPO (printed 0.0212e-10; corrected 0.0212e-8 = 2.12e-10 reproduces Fig 5); corrected value loaded, printed noted. Direct alpha convection-biased +~11% vs k/(rho*cp) -> pick ONE path. Espresso TDS at UPPER edge of conc range + brew T 88-96C ABOVE 82C -> extrapolation. Water-referenced Eqs (2)/(5)/(7) NOT loaded (need external water-property tables). Bulk rho ~1003 (<=1% over water); first-drip rho ~1196 (20% mass<->volume effect). DATA-ONLY companion (no separate component; gated under sourcing2026.g10_liquor_rheology). |
| `g10_liquor_rheology/khomyakov_kinematic_viscosity` — [khomyakov2020](../cards/khomyakov2020.md); Khomyakov et al. IOP CSEES 548,022040 (2020) Table 1 (measured kinematic viscosity; 10 solids x 6 temps) | transcription (open PDF); published: wt%; degC; mm^2/s; registry: wt%; degC; mm^2/s | CC BY 3.0 (IOP; open access); MEASURED kinematic viscosity 15-70 wt% x 20-80 C; nu monotone down in T, up in solids (smoke-tested). DOMAIN GUARD: >=15 wt%, ABOVE espresso TDS (4-12 wt%) -> espresso is an EXTRAPOLATION; do not extrapolate below 15 wt% silently. Industrial soluble-coffee extract, not fraction-resolved espresso. Printed density (+0.8*T sign conflict) and dynamic-viscosity power-law (literal eval 5.8-1194x off Table 1) equations QUARANTINED in-dir (_FLAGGED/_QUARANTINED.csv), NOT loaded. See docs/cards/khomyakov2020.md. |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### g1_glassbead_analog

**Access:** FOUND on 2026-09-23; 1 files / 1,903 bytes; 0 structured files, 1 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

glassbead_retention_kr: ten quantity/medium/parameter/value/unit/source rows.

Retention and relative-permeability shape priors only. Glass beads are an analogy; no measured coffee wetting curve or absolute coffee permeability.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `g1_glassbead_analog/retention_kr` — [g1_glassbead_analog](../cards/g1_glassbead_analog.md); arXiv:2501.13361 App. B (Sweijen2017/Culligan2004/Hilpert-Miller2001/Topp-Miller1966 compiled) | transcription (open PDF fetch); published: Pa*m; m^2; dimensionless; registry: Pa*m; m^2; dimensionless | open arXiv:2501.13361 (no journal DOI); underlying bead data per cited 1966-2017 refs; ANALOG (spherical glass beads, NOT coffee): transfers K_r(S) shape + S_r=0.07 + linearized-VG slope, NOT magnitude. Coffee retention search target (g1_retention_search_target.md) STAYS OPEN. Do NOT upgrade without a coffee measurement + §7.1 entry. Valid 0.2<S<0.8 only. |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### g3_pump_characteristic

**Access:** FOUND on 2026-09-23; 1 files / 2,196 bytes; 1 structured files, 1 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

pump_characteristic_ulka: ten pump-model/voltage/quantity/value/unit/source rows.

Machine operating-envelope anchors and sensitivity bounds. Manufacturer endpoints and community curve shapes have different authority; no shot-specific pump identification.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `g3_pump_characteristic/ulka_envelope` — [g3_pump_characteristic](../cards/g3_pump_characteristic.md); Ulka/Repa catalogue (EAX5/EAP5/EP5 datasheets); Decent blog (perfectly_calibrating_decent_flow_measurements); espressoaf flow_and_pressure | transcription (public web); published: bar; mL/s; W; min; registry: bar; mL/s; W; min | public (manufacturer datasheet; Decent blog; espressoaf community); Manufacturer ENDPOINTS only measured (Q_free~10.8 mL/s, P_deadhead 15 bar, +/-15%); interior curve is CONCAVE DROOP not quadratic. True DE1 Q(P) is CLOSED ESP32 firmware (country-calibrated, unpublished). Does NOT replace waszkiewicz2025/brewer_quadratic (operative measured quad). Independent DE1 curve = TB bench pull or Decent request. 120V/60Hz only. |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### gagne2021

**Access:** FOUND on 2026-09-23; 13 files / 458,906 bytes; 2 structured files, 13 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

Eleven .shot machine logs plus eleven resistance-decline summary rows and 14 grinder-arm summary quantities. Time-series text decoded; Tcl-style shot format needs the existing dedicated reader.

Machine response and descriptive decline; summary and logs share shots. Grinder arm is apparatus-specific, pressure is machine telemetry, and inferred resistance is not a permeability measurement.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `gagne2021/grinder_arm_summary` — [gagne2021](../cards/gagne2021.md); Gagne 2021 (Coffee Ad Astra) blog; grinder-arm means (EG-1+SSP ULF n=6 vs Niche n=5) EY/retention/temperature/resistance/drips | card transcription (measured means +/- errors; figure-read quantities flagged read_method=figure); published: % (EY); g (retention); degC (temp); DE1 units (resistance); count (drips); registry: % ; g ; degC ; de1_units ; count | J. Gagne, Coffee Ad Astra / Patreon (2021); no DOI, not peer-reviewed; 11 .shot files published alongside; 11 .shot P/flow/T traces NOT held (external acquisition target data/gagne2021_shots/; verify links); resistance is DE1-firmware instrument-defined; ~20% end-of-shot flow-sensor drift; no PSD; single coffee/machine/profile |
| `gagne2021/shots` — [gagne2021](../cards/gagne2021.md); 11 published DE1 .shot files (shotfiles/); flow-controlled blooming profile, EG-1+SSP ULF vs Niche, 18 g 1:4 | raw .shot files parsed to aligned espresso_* channels (no resampling/conversion); published: s ; bar ; mL s^-1 ; g ; degC (DE1 channels); registry: s ; bar ; mL/s ; g ; degC | J. Gagne, Coffee Ad Astra (2021); .shot files published alongside the post; no explicit licence (blog); not peer-reviewed; DE1 firmware-defined resistance channel; ~20% end-of-shot showerhead-flow drift contaminates R(t); no PSD; single coffee/machine/profile; blog redistribution posture unverified; raw .shot files tracked |
| `gagne2021/resistance_decline_summary` — [gagne2021](../cards/gagne2021.md); per-shot post-bloom apparent-resistance decline ratio (peak/end of R=P/Q), derived from the 11 DE1 .shot traces | computed from the raw .shot traces (puckworks.analysis.gagne2021_resistance); the derived summary ships, raw .shot stays git-tracked but out of the wheel; published: - (ratio); registry: - | J. Gagne, Coffee Ad Astra (2021); derived summary of the published .shot files; not peer-reviewed; apparent resistance from the DE1 flow estimate (drifts ~20% near shot end); single coffee/machine/profile; the raw .shot traces are the provenance (gagne2021/shots), redistribution posture unverified |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### gloess2013

**Access:** FOUND on 2026-09-23; 2 files / 5,077 bytes; 1 structured files, 2 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

de_espresso_endpoint: 17 quantity/value/uncertainty/unit/basis/source-location rows.

Endpoint chemistry and method context. Mixed quantities are not 17 shots; no fraction or time-series join. Consult source card for direct versus derived values.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `gloess2013/de_espresso_endpoint` — [gloess2013](../cards/gloess2013.md); Table 1 + text (exact) and Figs 4a/4c-g/7a (figure-read) | card transcription: text/table values + figure reads, flagged per row in an extraction_method column; published: g; ml; s; degC; bar; um; percent w/w; mg; ml 0.1M NaOH; area counts; registry: g; ml; s; degC; bar; um; percent; mg; ml 0.1M NaOH; area counts | CC-BY (open access; Eur. Food Res. Technol. 236:607-627; DOI 10.1007/s00217-013-1917-x); ONE in-scope condition only (DE Dalla Corte espresso); the paper's 8 other methods are non-espresso and NOT transcribed. Each sample is a composite of FIVE double shots, so the spread is between composites, not between shots. Headline TDS/EY are FIGURE-READS -- the ESM tables were not retrieved. Beverage given as VOLUME (60 ml) with no density, so any volume->mass conversion is an assumption. PSD is mode+FWHM only (400/220 um). Single coffee, single operating point: no parameter dependence is testable. |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### grudeva2025

**Access:** FOUND on 2026-09-23; 3 files / 3,354 bytes; 2 structured files, 2 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

exp13_per_vial_stats: 16 vial rows with solubles_mean_g, solubles_sd_g, n_shots; parameter table distinguishes thesis and paper values.

Source reconstruction and fraction observation support. Means are not new replicate records; permission documented in the existing permission card does not create an SPDX license or resolve the grain/bed-volume basis bridge.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `grudeva2025/params` — [grudeva2025](../cards/grudeva2025.md); card Parameters table (S1 Table 3.1 + S2 Table 1) | transcription (from card); published: SI mixed; registry: SI mixed | thesis + EJAM CC-BY (DOI 10.1017/S095679252500018X); kappa row adjudicated 2.2e-15 (decade typo); P_app 9.2e5 (printed 9.2e-6 typo); two configs not merged; rights basis is UNCHANGED article/thesis CC-BY - transcribed from the publications, NOT from the upstream repo, so the 2026-08-14 Grudeva permission (#73) is a cross-reference only and does not replace it |
| `grudeva2025/exp13_vial_stats` — [grudeva2025](../cards/grudeva2025.md); github YoanaGrudeva/espresso-model exp13.csv (Fig 2.3/6.8) | derived (mean/SD from repo raw); published: g; registry: g | reference repo declares no SPDX license; DIRECT WRITTEN PERMISSION from Dr. Yoana Grudeva 2026-08-14 (LinkedIn) covering code and data - full evidence retained privately (docs/permissions/grudeva2025.md; #73); paper CC-BY is a separate record; derived per-vial mean/SD over 14 shots; raw per-shot file still NOT redistributed (permission does not itself authorize new upstream payloads); solubles = vial weight x TDS; permission is a rights basis only - validation strength unchanged |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### hargarten2020

**Access:** FOUND on 2026-09-23; 2 files / 1,597 bytes; 2 structured files, 2 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

Eight roast/temperature/time/swelling-progress rows plus 14 scalar anchors with units and uncertainty.

Wetting/swelling timescale priors and sensitivity. These are source transcriptions; no synchronized espresso pressure, flow and wet-bed geometry.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `hargarten2020/swelling_progress` — [hargarten2020](../cards/hargarten2020.md); Hargarten, Kuhn & Briesen, J. Sci. Food Agric. 100(11) (2020) Table 2 (swelling progress % at 30s/4min, medium/light roast x 80/25C; 8 printed values) | transcription (printed scalars from card); published: percent; degC; s; registry: percent; degC; s | CC BY-NC (JSFA, open access); PSD/single-particle figures NOT digitized (owed); Ambient pressure ONLY -- the ~9 bar espresso regime is explicitly NOT covered (card's key silence). Progress >100% @4min = 20-min-normalization artifact, not overshoot. Two roasts, demineralized water. Pairs with Mo 2021/2022 swelling/erosion models (not implemented) to become runtime-relevant. Figures (PSD dry/wet, single-particle time-courses) OWED as a digitization drop. |
| `hargarten2020/scalar_anchors` — [hargarten2020](../cards/hargarten2020.md); Hargarten et al. 2020 printed scalar anchors (Δd_rel ~15%, size-independence slopes, dry/wet PSD modes, aspect ratio, EK43 dials) | transcription (printed scalars from card); published: percent; um; dimensionless; EK43-dial; registry: percent; um; dimensionless; EK43-dial | CC BY-NC (JSFA); ~15% ISOTROPIC swelling, size- and roast-INDEPENDENT (non-significant slopes), erosion-corrected via sieving; temperature-enhanced fines erosion (sign only, mass not quantified). No k(swelling) or porosity(t) relation -- direction only. Ambient pressure only. |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### khamitova2020

**Access:** FOUND on 2026-09-23; 5 files / 3,560 bytes; 5 structured files, 5 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

Tables 5.2–5.5 each have nine pressure/temperature rows and four tamp-force groups, analytes in mg/40 mL and mg/mL with RSD. Table 5.6 holds ground-coffee context.

Endpoint analyte response to conditions. Concentration bases must remain explicit; no fraction clock or physical-shot identifiers. Do not join to another campaign by matching pressure/temperature.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `khamitova2020/tamping` — [khamitova2020](../cards/khamitova2020.md); PhD dissertation Tables 5.2-5.6 — total CQA / caffeine / trigonelline / nicotinic acid (mg per 40 mL & per mL + RSD) across pressure x temperature x tamping force 10/15/20/30 kgF; Table 5.6 ground-coffee assay | card/dissertation table transcription (HPLC-VWD lab means + RSD %); published: mg/40mL ; mg/mL ; % RSD ; bar ; degC; registry: mg ; mg/mL ; % ; bar ; degC | Khamitova PhD dissertation, University of Camerino (2020); no DOI; tamping-force effect is approximately null (narrow variation) at fixed 1:2 ratio; single rig/coffee; the 3D model params (Tables 5.8-5.10) are NOT transcribed (rig-specific, superseded); precursor of the angeloni2023 lineage |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### liang2021

**Access:** FOUND on 2026-09-23; 4 files / 11,117 bytes; 3 structured files, 4 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

Figures 3–5 carry brew-ratio, TDS, extraction percentage and cupping/retained-liquid quantities, with nominal versus digitized ratio distinguished.

Immersion extraction ceiling and retained-liquid observation kernels. Not a flowing-puck hydraulic experiment; digitization error and dependent derived yield remain.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `liang2021/fig3_tds` — [liang2021](../cards/liang2021.md); Sci. Rep. 11,6904 Fig 3 (TDS vs R_brew, 1-L) | digitization (Tim); published: percent; g/g; registry: fraction; g/g | open access (DOI 10.1038/s41598-021-85787-1); digitized subset ~42 of 99 pts; refit K*E_max=0.2186 vs card 0.215+/-0.002; R_brew>=3 (excl. moist-sludge R=2) |
| `liang2021/fig4_E` — [liang2021](../cards/liang2021.md); Sci. Rep. 11,6904 Fig 4 (E, E_oven vs R_brew) | digitization (Tim); published: percent; g/g; registry: fraction; g/g | open access (DOI 10.1038/s41598-021-85787-1); measurement col = equilibrium\|oven_drying; equil E ~20.4% (card ~21%); oven under-reads |
| `liang2021/fig5_cupping` — [liang2021](../cards/liang2021.md); Sci. Rep. 11,6904 Fig 5 (cupping) | digitization (Tim); published: percent; g/g; registry: fraction; g/g | open access (DOI 10.1038/s41598-021-85787-1); 5A/5B panels; caf/decaf/roast levels |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### maille2024

**Access:** FOUND on 2026-09-23; 20 files / 31,071 bytes; 19 structured files, 20 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

Batch extraction curves for caffeine, 3-CQA, citric, malic and quinic acids; time and normalized C/Cinf. Tables carry sample IDs, sieve/roast, air/liquid PSD, specific surface and porosity.

Early-release kernels and within-source material comparisons. Join by declared Sample ID/material only; air and liquid PSD methods differ. Stirred batch has no bed-pressure history or matched espresso output.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `maille2024/materials` — [maille2024](../cards/maille2024.md); Table 5.1 | table transcription (thesis); published: - ; um; registry: - ; um | Maille PhD thesis, U. Sheffield 2024 (unredacted tables); White Rose eTheses; digitized 2026-07-25; 21 materials; single Colombian origin; two roasts; coarse sieved + full-PSD |
| `maille2024/phi` — [maille2024](../cards/maille2024.md); Table 6.3 | table transcription (thesis); published: -; registry: - | Maille PhD thesis, U. Sheffield 2024 (unredacted tables); White Rose eTheses; digitized 2026-07-25; 17 materials; TWO-cell-layer shell adopted (printed one-layer form is wrong, ~doubles phi); per-bin PSD unpublished so D[4,3] approximation used |
| `maille2024/psd_hybrid` — [maille2024](../cards/maille2024.md); Table 5.4 | table transcription (thesis); published: um ; -; registry: um ; - | Maille PhD thesis, U. Sheffield 2024 (unredacted tables); White Rose eTheses; digitized 2026-07-25; 21 materials; hybrid = liquid-dispersion fines below 186um + air above (Eq 5.1-5.3) |
| `maille2024/psd_dispersion` — [maille2024](../cards/maille2024.md); Table 5.2 | table transcription (thesis); published: um ; -; registry: um ; - | Maille PhD thesis, U. Sheffield 2024 (unredacted tables); White Rose eTheses; digitized 2026-07-25; 24 materials; documents that GrindState.fines_fraction is dispersion-method-dependent (186um cut here) |
| `maille2024/kinetics_caffeine_3cqa` — [maille2024](../cards/maille2024.md); Table 6.4 | table transcription (thesis); published: s ; - ; percent; registry: s ; - ; percent | Maille PhD thesis, U. Sheffield 2024 (unredacted tables); White Rose eTheses; digitized 2026-07-25; 17 materials; E5: OmegaT/3-CQA lambda_fast CI internally impossible (upper<est) -> UNUSABLE (analysis.maille2024.kinetics_flags) |
| `maille2024/kinetics_organic_acids` — [maille2024](../cards/maille2024.md); Table 6.5 | table transcription (thesis); published: s ; - ; percent; registry: s ; - ; percent | Maille PhD thesis, U. Sheffield 2024 (unredacted tables); White Rose eTheses; digitized 2026-07-25; 16 materials; '*' = unreported; E5: OmegaL/quinic lambda_slow CI internally impossible -> UNUSABLE |
| `maille2024/equilibrium_concentrations` — [maille2024](../cards/maille2024.md); Table 5.11 | table transcription (thesis); published: mg/L; registry: mg/L | Maille PhD thesis, U. Sheffield 2024 (unredacted tables); White Rose eTheses; digitized 2026-07-25; 21 materials; C_inf measured not predicted (no solute-inventory model) |
| `maille2024/normalized_curves` — [maille2024](../cards/maille2024.md); Table 5.10 | table transcription (thesis); published: s ; -; registry: s ; - | Maille PhD thesis, U. Sheffield 2024 (unredacted tables); White Rose eTheses; digitized 2026-07-25; 3 materials x 5 compounds x 7 times; the extraction FIGURES (Figs 4.6-4.10, ~60 events) are a separate digitization OWED |
| `maille2024/ssa` — [maille2024](../cards/maille2024.md); Table 5.6 | table transcription (thesis, unredacted); published: cm2/g; registry: cm2/g | Maille PhD thesis, U. Sheffield 2024 (unredacted tables); White Rose eTheses; digitized 2026-07-25; was redacted in the release the card was written from; supplied here from the unredacted thesis |
| `maille2024/particle_porosity` — [maille2024](../cards/maille2024.md); Table 5.9 | table transcription (thesis, unredacted); published: g/cm3 ; -; registry: g/cm3 ; - | Maille PhD thesis, U. Sheffield 2024 (unredacted tables); White Rose eTheses; digitized 2026-07-25; closed porosity rises with particle size; unredacted |
| `maille2024/extraction_curves` — [maille2024](../cards/maille2024.md); Figs 4.6-4.10 (material Omega_A) | figure digitization (5 compounds x replicates); published: s ; -; registry: s ; - | Maille PhD thesis, U. Sheffield 2024; White Rose eTheses; figures digitized 2026-07-25; single material Omega_A only; per-figure digitization schemas normalized; batch WMBR, coarse grind |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### mckeonaloe2022

**Access:** FOUND on 2026-09-23; 1 files / 482 bytes; 1 structured files, 1 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

basket_open_area_geometry: four basket/face rows with open-area percent, hole diameter and uncertainty; two basket specimens.

Basket outlet geometry context and observation-operator development. Faces of a basket are not independent specimens; no measured hydraulic pressure loss or coffee extraction.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `mckeonaloe2022/basket_open_area_geometry` — [mckeonaloe2022](../cards/mckeonaloe2022.md); Medium (Coffee Data Science) post; open-area + hole-diameter bar charts (2 baskets Wafo Classic/VST x 2 faces exit/coffee) | transcription (card table; open-area direct, mean diameters read off bar charts); published: % ; um; registry: % ; m | R. McKeon Aloe, Medium / Coffee Data Science (2022); non-peer-reviewed; no DOI; n=1 basket each; mean diameters read off bar charts (mean_hole_diam_approx=True); hole count / plate thickness not provided; holes taper wider on coffee face (exit face flow-limiting); geometry only, NO dP/resistance -> does NOT close G9 |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### mo2023

**Access:** FOUND on 2026-09-23; 7 files / 3,807 bytes; 6 structured files, 7 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

PSD table has four capsule types. Four sample tables have six microCT-derived geometries each, porosity/tortuosity and simulated kD/kF/kF1; some entries are missing or zero.

Geometry-conditioned transport priors and unit auditing. Permeabilities are SPH-derived on measured geometry, not 24 independent wet espresso measurements; inertial-unit caveat remains.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `mo2023/forchheimer` — [mo2023](../cards/mo2023.md); arXiv:2305.03911 Tables 2-5 (24 microCT samples) | digitization/transcription (Tim); published: 1e-13 m2 (kD,kF); 1e-9 m2 (k1F); registry: m2 (kD,kF); flagged (k1F) | preprint arXiv:2305.03911 (no journal DOI); K1 UNITS CAVEAT (§5.3): Eq.2 needs [k1]=m but tables give 1e-9 m2; inconsistent ~1e4 vs Fig 8b -> do NOT use k1 quantitatively (author corresp pending) |
| `mo2023/fig8a` — [mo2023](../cards/mo2023.md); arXiv:2305.03911 Fig 8a (kD vs grad P) | digitization (Tim); published: bar/m; 1e-13 m2; registry: Pa/m; m2 | preprint arXiv:2305.03911; Darcy->Forchheimer decline 5.2->2.5e-13; Re NOT interchangeable with wadsworth Fo_F (§5.2) |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### mo2023_2

**Access:** FOUND on 2026-09-23; 7 files / 49,822 bytes; 6 structured files, 6 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

fig3a_qdecay contains powder/swelling setting/time/flow curves; figs6_9 has cup mass, yield/strength and errors; fig6_Ksweep contains model sensitivity curves.

Separate experiment digitizations from simulated swelling and partition sweeps. Source reconstruction and sensitivity only; fitted inventory cannot become an independently measured initial condition.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `mo2023_2/granulometry_table1` — [mo2023_2](../cards/mo2023_2.md); Table 1 | transcription (thesis table); published: um; -; registry: um; - | Elsevier, J. Food Eng. 2023 DOI 10.1016/j.jfoodeng.2023.111843 (paywalled); no code/data published; bimodal fine/coarse split at 100 um; distinct from the mo2023 arXiv PSD table |
| `mo2023_2/k0_table2` — [mo2023_2](../cards/mo2023_2.md); Table 2 | transcription (thesis table); published: m^2; registry: m^2 | Elsevier, J. Food Eng. 2023 DOI 10.1016/j.jfoodeng.2023.111843 (paywalled); no code/data published; t=0 flow closure sanity only, NOT swelling |
| `mo2023_2/yield_strength_figs6_9` — [mo2023_2](../cards/mo2023_2.md); Figs 6-9 | digitisation (raster); published: g; %; registry: g; % | Elsevier, J. Food Eng. 2023 DOI 10.1016/j.jfoodeng.2023.111843 (paywalled); no code/data published; powders E/M/F x q 2/3/4 mL/s; monotone in grind (NO fine-grind dip -- fixed-flow defeats clogging) |
| `mo2023_2/fig3a_qdecay` — [mo2023_2](../cards/mo2023_2.md); Fig 3(a) | digitisation (raster); published: %; s; mm/s; registry: -; s; mm/s | Elsevier, J. Food Eng. 2023 DOI 10.1016/j.jfoodeng.2023.111843 (paywalled); no code/data published; fixed-dP swelling regime; the paper's headline claim rests on ZERO data here |
| `mo2023_2/fig6_Ksweep_typeM` — [mo2023_2](../cards/mo2023_2.md); Fig 6 | digitisation (raster); published: -; g; %; registry: -; g; % | Elsevier, J. Food Eng. 2023 DOI 10.1016/j.jfoodeng.2023.111843 (paywalled); no code/data published; CAPTION HAZARD: 'K=0.9 hindrance factor' is the PARTITION coefficient, mislabeled |
| `mo2023_2/sim_lines_figs7_9` — [mo2023_2](../cards/mo2023_2.md); Figs 7-9 | digitisation (raster); published: g; %; registry: g; % | Elsevier, J. Food Eng. 2023 DOI 10.1016/j.jfoodeng.2023.111843 (paywalled); no code/data published; K tuned to 0.9; implement-later solver reproduction target |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### moroney2015

**Access:** FOUND on 2026-09-23; 13 files / 190,710 bytes; 13 structured files, 13 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

Tables 1–2 mix measured, nominal and fitted parameters; README_manifest identifies per-figure evidence. Figures include PSD, batch/bed extraction, pressure and concentration profiles.

Primary lineage for later Moroney models; use source reconstruction and transport-kernel checks. Simulations, fitted parameters and source experiments are distinct subsets and reused across later papers.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `moroney2015/data` — [moroney2015](../cards/moroney2015.md); Chem. Eng. Sci. 137:216-234 Tables 1-2 + Figs 1,2,3,6,7,8,9,10,11,12 digitized — the primary Philips multiscale dataset (batch + cylindrical), fine (JK) and coarse (Cimbali #20) | verbatim table transcription (Tables 1-2) + figure digitization (per-file README_manifest evidence_strength MEASURED/ESTIMATED); published: kg m-3 ; mg/g ; um ; s ; g ; Pa ; m; registry: kg/m^3 ; mg/g ; um ; s ; g ; Pa ; m | Moroney et al. 2015, Chemical Engineering Science (Elsevier); DOI 10.1016/j.ces.2015.06.003; digitized/transcribed by Puckworks; Philips drip-filter chamber (60 g, 250 mL/min, ~1 L), NOT espresso brew ratio; Fig 8 y-calibration ESTIMATED (raster source); some figure series duplicate others (Fig 9=Fig 1; Fig 11/12 blue=Fig 3); a # provenance header rides on every file |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### moroney2016

**Access:** FOUND on 2026-09-23; 3 files / 2,589 bytes; 2 structured files, 3 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

Table 1 parameters include measured, nominal, fitted and derived roles; Figure 6 has 15 nondimensional exit-concentration points.

Asymptotic/source reconstruction, using Moroney 2015 experimental lineage. No independent new campaign; nondimensional time requires its declared source scale.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `moroney2016/table1` — [moroney2016](../cards/moroney2016.md); SIAM J.Appl.Math 76(6) Table 1 (params + groups) | transcription (from card); published: mixed SI + um; registry: mixed SI + um | paper (DOI 10.1137/15M1036658); fine-grind params; alpha*/beta* fitted; constant-dP baked in |
| `moroney2016/fig6` — [moroney2016](../cards/moroney2016.md); SIAM J.Appl.Math 76(6) Fig 6a (exit conc) | digitization (Tim); published: nondimensional; registry: nondimensional | paper (DOI 10.1137/15M1036658); leading-order matches plateau + wash-through (c=0.5 at t~3.1); tail needs outer soln (Moroney 2015), not on card |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### moroney2019

**Access:** FOUND on 2026-09-23; 1 files / 569 bytes; 1 structured files, 1 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

table2: six fine/coarse and single/two-grain parameter rows, including reported and corrected mass-transfer coefficients and diffusivity.

Parameter/unit reconstruction and mechanism priors. These are fitted model parameterizations, not six experiments or independent diffusivity measurements.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `moroney2019/table2` — [moroney2019](../cards/moroney2019.md); Moroney et al. 2019 PLoS ONE Table 2 (6 grind x model configs); h_sl corrected per cooper2021 author-confirmed errata | card transcription (printed Table 2; corrected columns derived via cooper2021 Erratum A/B); published: m ; - ; kg m^-3 ; m s^-1; registry: m ; - ; kg/m^3 ; m/s | Moroney et al. 2019 PLoS ONE (CC BY 4.0); cooper2021 Quantitative Cafe blog (errata, author-confirmed); h_sl_reported carries the paper's ~10^3 CFD-scaling error; use h_sl_corrected (=reported/965.3). Kinetics duplicate cameron2020 at lower fidelity; pre-dissolution IC overshoots saturation early; single Philips drip-brew dataset, not espresso |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### pannusch2024

**Access:** FOUND on 2026-09-23; 559 files / 304,925,470 bytes; 176 structured files, 2 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

Full archive and extracted repository inspected: fit and prediction HPLC/RI/DoE workbooks, 70 legacy XLS telemetry files, dry PSD workbook, MATLAB arrays/code and generated figures. Prediction DoE includes DoE, pmax, ExpSheet, HPLCWeightsAlcaloids, HPLCWeightsLactones, SampleWeights sheets; RI workbook separates TdS, dilution_factor and raw_data.

Use the qualified fit/prediction/reference reconstruction: 45 fit shots +24 prediction shots, six fractions each, and one 12-fraction reference preparation (three spill exclusions). Programmed flow/temperature are inputs; mass fractions and analytes are targets. Opaque MATLAB tables require the existing qualified adapter. No new M0, same-lot, clock or pressure-boundary equivalence.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `pannusch2024/table2_params` — [pannusch2024](../cards/pannusch2024.md); J.Food Eng 367 Table 2 (fitted A/B/K/gamma/cs0) | transcription (from card); published: mixed (1, K, mg/mL); registry: mixed | CC-BY-NC-3.0 (Mendeley 10.17632/y2tz67f6ry.1) / paper CC-BY; 4 solutes + per-grind psi/d_s2; fitted params lack generality (authors); TDS = caffeine-like pseudo-molecule |
| `pannusch2024/experimental_kinetics` — [pannusch2024](../cards/pannusch2024.md); Mendeley Data 10.17632/y2tz67f6ry.1; hash-bound fit/prediction/reference reconstruction | deterministic external-source reconstruction; valid-only physical-shot aggregation; published: s; g; mg/g; mg; percent; degC; mL/s; registry: s; g; mg/g; mg; percent; degC; mL/s | CC-BY-NC-3.0 (Mendeley 10.17632/y2tz67f6ry.1); 15 fit experiments/45 shots; 8 prediction conditions/24 shots; experiment 46 n=1 operational reference; no independent validation; raw source not redistributed |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### perticarini2024

**Access:** FOUND on 2026-09-23; 3 files / 1,500 bytes; 3 structured files, 3 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

bed_height_time: eight coffee/granulometry/height/time rows; ey_tds_cibao: 18 condition rows with T, p, tau, TDS uncertainty and EY; six granulometry parameter rows.

Geometry and endpoint condition context. Approximate grain-family parameters and prescribed conditions are not matched instantaneous hydraulic measurements.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `perticarini2024/ey_tds_cibao` — [perticarini2024](../cards/perticarini2024.md); Table 4.2 (p.90) | transcription (thesis table, read from the PDF text layer); published: degC; bar; s; percent; registry: degC; bar; s; percent | Universita degli Studi di Camerino PhD thesis (Perticarini 2024), deposited 28 Feb 2024; no DOI, no explicit licence stated -- transcribed table values only, under academic quotation; no code or figures reproduced; 18 conditions for Cibao Altura: 5 granulometries incl. extra fine and extra coarse, T 90.4/93.4 degC, p 6/9 bar plus 12 bar on the two extreme grinds only. Extends the registry's grind envelope past egidi2024's Modoetia set in BOTH directions. EY is the thesis's own TDS x brew-ratio product, not an independent measurement -- implied beverage/dose ratio spans 1.95-2.07, consistent with the stated 40+/-2 g out of 20+/-0.1 g. Table 4.3 (Modoetia) is NOT transcribed: expected to duplicate egidi2024 Table 2 and unverified |
| `perticarini2024/bed_height_time` — [perticarini2024](../cards/perticarini2024.md); Table 4.1 (p.87) | transcription (thesis table, read from the PDF text layer); published: mm; s; registry: mm; s | Universita degli Studi di Camerino PhD thesis (Perticarini 2024), deposited 28 Feb 2024; no DOI, no explicit licence stated -- transcribed table values only, under academic quotation; no code or figures reproduced; Mean tamped height L and mean extraction time per granulometry per coffee; VST Competition basket, inner radius 29.25 mm, 20+/-0.1 g dose, 20 kgF tamp |
| `perticarini2024/granulometry_params` — [perticarini2024](../cards/perticarini2024.md); Table 4.6 (p.96) | transcription (thesis table, read from the PDF text layer); published: um; dimensionless; s; registry: um; dimensionless; s | Universita degli Studi di Camerino PhD thesis (Perticarini 2024), deposited 28 Feb 2024; no DOI, no explicit licence stated -- transcribed table values only, under academic quotation; no code or figures reproduced; Fines/boulder representative radii and fines solid fraction for the six simulated I=1 extractions. a_f, a_b are the two MODES of a bimodal PSD split at 100 um, not independently measured radii. Store WITH the factor-2 a_s convention flag the card records |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### pocketscience2024

**Access:** FOUND on 2026-09-23; 8 files / 2,539,398 bytes; 6 structured files, 3 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

Three source-style CSV exports include LRR dose/water/beverage quantities and multirow basket sheets. Derived edge-EY means have 12 condition rows; LRR summary has two grinder rows.

Retained-liquid and radial extraction context. Multirow exports need a header adapter; source measurements and condition means must not be counted twice. Community methods lack a qualified puck-pressure boundary.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `pocketscience2024/edge_ey_condition_means` — [pocketscience2024](../cards/pocketscience2024.md); Espresso water flow experiment.xlsx (VST18 + Sworks High Flow sheets); 12 condition means per card Parameters table | card transcription (condition means; raw workbook held locally, gitignored); published: % (extraction yield); fraction (outer mass / dose); registry: % ; fraction | used with author's permission (attribution/citation pocketscience2024 required); raw workbook kept local for size, derived summary tracked; shot style confounded with grinder; two-zone radial only (no depth); section EY anchored to shot EY by construction; VST18xbrass cells absent (12 of 16); Gagne MC edge losses differ from raw means; label erratum carried (outer-to-TOTAL, not outer-to-inner); does NOT close G1 or G9 |
| `pocketscience2024/lrr_scalars` — [pocketscience2024](../cards/pocketscience2024.md); Espresso water flow experiment.xlsx (LRR sheet; 10 flush shots, 2 grinders) | card transcription (grinder-level means; raw sheet gitignored); published: g water / g dose; registry: g/g (dimensionless) | used with author's permission (attribution/citation pocketscience2024 required); raw workbook kept local for size, derived summary tracked; lumped POST-FLUSH retention (~285 g water / 14 g dose), NOT in-shot dead water and NOT a retention curve theta(psi); does NOT satisfy the G1 search target |
| `pocketscience2024/workbook_assay_reconstruction` — [pocketscience2024](../cards/pocketscience2024.md); Espresso water flow experiment.xlsx; SHA256 9e9063baea1e8f67d905b1e2d03a61a4227e26ed2964ae118426be09bced01cc; source-export CSVs; docs/analysis/sci_md_radial_obs_001/CONTRACT.json | explicit formula graph and typed assay; 60 experimental rows (3 source rejects), 10 separate flush rows; local replay output external; published: g; numeric TDS percent; Excel percent fractions; registry: kg; dimensionless mass fractions; named display units for replay | recorded permission with attribution to Pocket Science Coffee (2024); original expanded grant not held; new rows/aggregates private only; new task-local subset ID; same workbook lineage as older card means; Sworks and VST use different denominators and retention corrections; Y54 unfiltered anchor anomaly retained; no production dependency authority |

Prior authority: `SCI-MD-RADIAL-OBS-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### ribes2020

**Access:** FOUND on 2026-09-23; 1 files / 485 bytes; 1 structured files, 1 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

radial_ey: nine condition/tamper/filter/zone rows with inner/outer radii, zone EY and shot EY.

Radial observation operators and mechanism discrimination context. Zone observations share shots; no resolved radial flow or transient transport, and no cross-study matched-shot join.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `ribes2020/radial_ey` — [ribes2020](../cards/ribes2020.md); Ribes 2020 slide deck; 3-condition x 3-zone radial EY bar charts (baseline / V60 bottom paper / convex tamper) | card transcription (zone EYs read from slide bar charts; radii from chart axes); published: % (EY); mm (radius); registry: % ; mm | S. Ribes 2020 slide deck (Decent community); no DOI, not peer-reviewed; outlet-side paper filter changes flow distribution + fines retention + resistance at once (unseparable); zone-EY method undocumented so absolute EYs are not cross-source comparable; single machine/coffee/grind; 12 g in a 15 g basket (under-dosed) |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### ribes2021

**Access:** FOUND on 2026-09-23; 1 files / 455 bytes; 1 structured files, 1 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

radial_ey: 12 basket/contact-screen/zone rows, radii and local/whole-shot EY.

Basket/screen radial extraction context, separate from Ribes 2020 conditions. Spatial endpoints do not identify a unique flow mechanism or provide radial time-series truth.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `ribes2021/radial_ey` — [ribes2021](../cards/ribes2021.md); Ribes 2021 slide deck; 4-condition x 3-zone radial EY bar charts (VST/Pullman 20 g x contact-screen no/yes) | card transcription (zone EYs read from slide bar charts; radii from chart axes); published: % (EY); mm (radius); registry: % ; mm | S. Ribes 2021 slide deck (Decent community); no DOI, not peer-reviewed; contact screen ABOVE the puck (inlet-side), 19 g in a 20 g basket; light-polish tamp confound in the no-screen arm; Pullman/no-screen area-weight slack (22.3 vs stated 21); vendor-adjacent (BPLUS under test) |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### romancorrochano2015

**Access:** FOUND on 2026-09-23; 1 files / 384 bytes; 1 structured files, 1 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

table2: 12 grind/bulk-density/permeability/SD rows with Tukey grouping.

Separate source permeability priors and uncertainty context. Bulk density is not wet operating porosity; methods and apparatus must be reconciled before EWP use.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `romancorrochano2015/table2` — [romancorrochano2015](../cards/romancorrochano2015.md); Roman-Corrochano et al. 2015 Table 2 — tamped-bed K (m^2), mean+/-SD triplicate, grind A-D x bulk density 360/400/480 kg m^-3, Tukey groups | card transcription (fully printed Table 2 with SDs and ANOVA letters); published: m^2 (K); kg m^-3 (bulk density); registry: m^2 ; kg/m^3 | Roman-Corrochano et al. 2015 (CC BY 4.0; DOI'd version of record); K-C equations non-predictive (take the table, skip the models); tamped/consolidated regime; d[3,2] per grind and consolidation constants live in the card, not this CSV |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### romancorrochano2017

**Access:** FOUND on 2026-09-23; 11 files / 18,701 bytes; 10 structured files, 10 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

Comment-prefixed CSV tables/figures carry diffusivity, hindrance, partition coefficients, tamped permeability, extraction inventory and model prediction error. Printed thesis pages are retained in comment provenance.

Source reconstruction and mass-basis/unit adapters. Fitted transport parameters and digitized model error are not direct independent observables; strip comments before parsing, preserving source notes.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `romancorrochano2017/tamped_kappa` — `romancorrochano2017`; Table 6.1 (p.227) | transcription (thesis table); published: m^2; registry: m^2 | University of Birmingham e-theses (open access; non-commercial research use); no DOI; 4 grinds x 3 densities; PsiE non-monotone in density (thesis notes kappa noisy at coarsest); NOT a K-C validation (K-C closures are poorer than wadsworth2026.inertial) |
| `romancorrochano2017/deff_table4_9` — `romancorrochano2017`; Table 4.9 (p.153) | transcription (thesis table); published: x1e-11 m^2/s @80C; registry: x1e-11 m^2/s | University of Birmingham e-theses (open access; non-commercial research use); no DOI; grind PsiG not reported; med-MW is the parameter-free bed choice |
| `romancorrochano2017/partition_K_table4_10` — `romancorrochano2017`; Table 4.10 (p.155) | transcription (thesis table); published: - (K); C (T); registry: - ; K | University of Birmingham e-theses (open access; non-commercial research use); no DOI; swelling factor S=1 (none observed) |
| `romancorrochano2017/hindrance_table4_8` — `romancorrochano2017`; Tables 4.8/4.7/4.6 joined | transcription (thesis tables); published: -; registry: - | University of Birmingham e-theses (open access; non-commercial research use); no DOI; keyed by blend not the PsiB..H grind ladder; Hm~=tau/eps_total consistency holds |
| `romancorrochano2017/Db_table3_4` — `romancorrochano2017`; Table 3.4 (p.78) | transcription (thesis table); published: m^2/s @80C; registry: m^2/s | University of Birmingham e-theses (open access; non-commercial research use); no DOI; caffeine Db nominal (Poling 2008); galactomannan rh from lit/DLS |
| `romancorrochano2017/mpe_table5_3` — `romancorrochano2017`; Table 5.3 (p.183) | transcription (thesis table); published: %; registry: % | University of Birmingham e-theses (open access; non-commercial research use); no DOI; keyed by grind; all-grinds-joint vs per-grind single Deff -- NOT the 1-vs-4-Deff comparison (that is Figs 5.11/5.13) |
| `romancorrochano2017/fig5_11_mpe` — `romancorrochano2017`; Fig 5.11 (p.194) | digitisation (raster, ~+/-0.5 pp); published: %; registry: % | University of Birmingham e-theses (open access; non-commercial research use); no DOI; y-axis max 80%; min-MPE class per grind matches thesis text within ~0.2pp |
| `romancorrochano2017/fig5_13_mpe` — `romancorrochano2017`; Fig 5.13 (p.198) | digitisation (raster, ~+/-0.5 pp); published: %; registry: % | University of Birmingham e-theses (open access; non-commercial research use); no DOI; multiple-Deff drops MPE ~50% vs best single; two dialysis/diafiltration weightings |
| `romancorrochano2017/fig7_4_espresso` — `romancorrochano2017`; Fig 7.4 (p.283) + Tables 7.1/7.2 | digitisation (MPE) + transcription (conditions); published: x1e-6 m^3/s; C; kg/m^3; %; registry: SI; % | University of Birmingham e-theses (open access; non-commercial research use); no DOI; 15 conditions; MPE_med_MW is the non-fitted headline 8.6-14.3%; low/high-MW columns worse (wrong class) |
| `romancorrochano2017/y0_extractable` — `romancorrochano2017`; Section 4.4.1 (p.139) + Fig 4.19 (p.140) | transcription (PsiA exact) + digitisation (Fig 4.19 norm, ~+/-0.5 pp); published: kg SS/100 kg RGC (=%); registry: fraction | University of Birmingham e-theses (open access; non-commercial research use); no DOI; PsiC/PsiD not measured; non-PsiA absolute = Fig 4.19 norm x 31.7; Flakes ~ finest |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### schmieder2023

**Access:** FOUND on 2026-09-23; 23 files / 110,706,539 bytes; 12 structured files, 14 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

S1 Fraction Mass & Concentration sheet: 292 sheet rows including headers; normalized raw_fractions: 288 rows with exp/rep/fraction, fraction/accumulated mass g and three analytes mg/g. S2 fits and S3 cup totals are different subsets; copies occur in two directories and an archive.

Fraction delivery and within-campaign replicate analysis via exp/rep/fraction. Fit parameters are derived, cup totals overlap fractions, and Pannusch shares the fit-campaign lineage. No independent cross-corpus doubling or production-inventory bridge.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `schmieder2023/kinetics_fit_params_avg` — [schmieder2023](../cards/schmieder2023.md); Foods 12,2871 Table A1 (JATS XML full text) | transcription (programmatic XML parse); published: mg/g (TDS g/g); g; registry: mg/g (TDS g/g); g | open access CC-BY (Foods 12,2871; DOI 10.3390/foods12152871); authoritative averaged fits; Exp7 caffeine c0=9.70981 lambda=23.09434 == card |
| `schmieder2023/kinetics_fit_params_reps` — [schmieder2023](../cards/schmieder2023.md); Foods 12,2871 Table S2 (supplementary xlsx) | transcription (programmatic xlsx parse); published: mg/g (TDS g/g); g; registry: mg/g (TDS g/g); g | open access CC-BY (Foods 12,2871; DOI 10.3390/foods12152871); 15 exp x 3 reps (Exp7 center point x6) |
| `schmieder2023/cup_masses` — [schmieder2023](../cards/schmieder2023.md); Foods 12,2871 Table S3 = paper Table 2 (xlsx) | transcription (programmatic xlsx parse); published: mg (TDS g); ml/s; C; bar; registry: mg (TDS g); ml/s; C; bar | open access CC-BY (Foods 12,2871; DOI 10.3390/foods12152871); per-rep mass + concentration at BR 1/1,1/2,1/3; mean RSD 2.5% (max 8.5%) |
| `schmieder2023/raw_fractions` — [schmieder2023](../cards/schmieder2023.md); Foods 12,2871 Table S1 (supplementary xlsx) | transcription (programmatic xlsx parse); published: g; mg/g; registry: g; mg/g | open access CC-BY (Foods 12,2871; DOI 10.3390/foods12152871); no TDS column (TDS gravimetric); fractions 1,2,3,5,7,10 per card; earliest brew misfits exponential |
| `schmieder2023/rsm_coefficients` — [schmieder2023](../cards/schmieder2023.md); Foods 12,2871 Table 3 (JATS XML) | transcription (programmatic XML parse); published: mg (TDS g) mixed per term; registry: same | open access CC-BY (Foods 12,2871; DOI 10.3390/foods12152871); adj R2 0.41-0.75 (caffeine worst); authors restrict to qualitative trends; eliminated terms = 0 |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### schulman2011

**Access:** FOUND on 2026-09-23; 1 files / 1,004 bytes; 1 structured files, 1 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

The quoted comment/header layout defeated the initial strict CSV reader; the final comment-filtered structural receipt recovered 14 rows with six consistent columns: basket, D_base_mm, d_hole_um, sigma_hole_um, A_h_mm2, grid.

Basket geometry context is available in the public source card. Structural recovery is not a new scientific qualification: face-side hole area has tapered-hole bias, hole count is derived and plate thickness assumed. Check source conventions for any adapter. No pressure-loss experiment held.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `schulman2011/basket_geometry` — [schulman2011](../cards/schulman2011.md); Part-1 geometry table | transcription (card table); published: mm; um; mm^2; registry: mm; um; m^2 | Schulman, Home-Barista.com (2011); non-peer-reviewed; no DOI; 14 baskets; A_h face-side (tapered holes, unknown bias); hole count derived; plate thickness assumed |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### smrke2024

**Access:** FOUND on 2026-09-23; 18 files / 1,798,156 bytes; 10 structured files, 18 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

Figures 2–7 and supplementary Fig S1 are present as digitized CSVs and images. Fig S1: 18,001 time/flow/series/run-index rows; PSD curves: 4,342 sampled curve rows. Fitted PLSR/sensory curves are separate from experimental marker digitizations.

Fines/PSD/flow-shape and observation-operator context. Dense pixel-derived points are not independent shots. The card statement that the supplement was not held at intake is historical; this census confirms its digitization is held, without recovering native machine logs.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `smrke2024/figures` — [smrke2024](../cards/smrke2024.md); Sci. Rep. 14:5612 digitized figures Fig 2-7 + Supp Fig S1 (EY-vs-time across 0/1/2/4 g added fines; PSD; PLSR; predicted-vs-measured; PTR-MS; sensory; per-shot flow profiles) | figure digitization (axis-tick calibration + colour-masked marker centroids with overlap-split flags); SI Fig S1 from MOESM1; published: s ; % ; um ; g/s ; ncps; registry: s ; % ; um ; g/s ; - | Smrke et al. 2024, Scientific Reports (CC BY 4.0); DOI 10.1038/s41598-024-55831-x; raw on request from S. Smrke; no published coefficients/error stats so no reproduction gate is possible; the fines-mechanism claim is an absence-of-effect argument at n=3/condition; sensory is single Q-grader (not double-blind); PTR-MS IDs tentative; marker-overlap uncertainty on some Fig 3 clusters |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### sobolik2002

**Access:** FOUND on 2026-09-23; 13 files / 73,386 bytes; 12 structured files, 13 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

Tables 1–2 coefficients, figures 1–3 and 6 digitizations, apparatus dimensions and equation-evaluated grids are distinct subsets. omega is solids mass fraction, T in degC, viscosity Pa s; shear-rate/shear-stress columns exist in Fig 1.

Property priors and law sensitivity. Computed grids are model output; Weisser refit and concentrated solution measurements are distinct lineages. Source-domain and 90 C extrapolation limits from rheology work persist.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `sobolik2002/rheology` — [sobolik2002](../cards/sobolik2002.md); J. Food Eng. 51:93-98 Tables 1-2 + Eqs (1)-(11) computed lines + Figs 1-6 digitized — viscosity mu(omega,T) and electrical conductivity kappa(omega,T) of concentrated soluble-coffee solutions | exact transcription (Tables 1-2), equation evaluation (computed lines), and figure digitization (Figs 1,2,3,6; each digitized file carries an evidence_strength column); published: Pa s ; S m^-1 ; omega kg/kg ; degC; registry: Pa*s ; S/m ; - ; degC | Sobolik et al. 2002, Journal of Food Engineering 51:93-98 (Elsevier); PII S0260-8774(01)00042-5; digitized/computed by Puckworks; soluble-coffee (freeze-dried) extract, NOT espresso liquor; omega = dry-coffee mass fraction; Fig 5 deliberately not scatter-digitized (carried by Table 1); Table 1 endpoint anomaly + thixotropy flags in the dir README; Weisser 1972 data available via Fig 3 only |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### telisromero2001

**Access:** FOUND on 2026-09-23; 2 files / 1,474 bytes; 0 structured files, 2 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

Two Markdown table transcriptions: 24 Newtonian viscosity cells and 27 K/n pairs. G10 CSVs are alternative normalized representations; Xw is water mass percent, viscosity table displays 10^3-scaled Pa s.

Measured-source fluid-property anchors and bounded sensitivity; not new shots or fresh espresso. Keep industrial-soluble-extract transfer, dilute continuation and source-table rounding explicit. No article PDF or rheograms held here.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `g10_liquor_rheology/telisromero2001_closures` — [telisromero2001](../cards/telisromero2001.md); Telis-Romero et al. J. Food Process Eng. 24 (2001) 217 (DOI 10.1111/j.1745-4530.2001.tb00542.x) Eqs (10)/(12)/(13) fitted closures + Table-1 eta / Table-2 K anchor points | transcription (closure coefficients + 2 measured anchors from card; primary tables paywalled/figure-and-table-only); published: Pa*s; Pa*s^n; K; %w/w water; registry: Pa*s; Pa*s^n; K; %w/w water | paywalled (Wiley, bot-blocked here); coefficients + anchors transcribed from docs/cards/telisromero2001.md, primary Tables 1-2 NOT redistributed; Industrial SOLUBLE-COFFEE extract (51 Brix, one batch), NOT espresso liquor -> unquantified composition bias (no oils/fines/CO2). Newtonian domain X_w 76-90%; power-law only >36% solids. Espresso TDS 4-12% solids sits at/below the source's dilute end -> mu EXTRAPOLATED toward water. Bulk shot-TDS mu ~=1.06x water (negligible); ~1.3-2x belongs to concentrated early in-pore liquor. Table1(24)/Table2(54) per-cell values NOT yet digitized (figure/table-only). Companion rho/thermal in telisromero2000 (card-only). |
| `g10_liquor_rheology/telisromero2001_tables` — [telisromero2001](../cards/telisromero2001.md); Telis-Romero et al. J. Food Process Eng. 24 (2001) 217 Table 1 (24 eta cells, Newtonian, X_w 76-90% x T 295-365K) + Table 2 (27 K + 27 n cells, power-law, X_w 49-64% x T 274-353K); source md in data/telisromero2001/ | digitization (Tim's drop, 2026-07-15; 2-3 sig figs off the paywalled tables); published: Pa*s; Pa*s^n; dimensionless; %w/w; K; registry: Pa*s; Pa*s^n; dimensionless; %w/w; K | paywalled (Wiley); tables digitized by author-side drop, not redistributed beyond this repo; CLOSES the OWED per-cell digitization. Cross-validates the transcribed closures (independent path) against the measured grid -> agreement at the authors' own fit quality confirms both. Table 1 spans exactly the espresso in-pore X_w range (76-90%); used directly (bilinear, data.telisromero_eta_measured) by analysis.g10_viscosity_sensitivity. Composition caveat (soluble-coffee extract != espresso liquor) + dilute-end extrapolation (espresso is >90% X_w, above the box top) stand. |

Prior authority: `PANNUSCH-PRIOR-IMPACT-001`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### vacaguerra2023a

**Access:** FOUND on 2026-09-23; 6 files / 6,219 bytes; 5 structured files, 5 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

Figure 12: 50 measured/calculated dry-porosity rows; Table C1: nine conditions with distribution, dosage, epsilon_0, pressure/flow/height and errors. Tables 1–3 hold PSD and fitted coefficients.

Dry-porosity source operators and separate priors. EWP qualified two porosity supports across this and Wadsworth; Figure 12 is operator-only, permeability stress-only. Dry does not equal wet porosity.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `vacaguerra2023a/extraction_conditions` — [vacaguerra2023a](../cards/vacaguerra2023a.md); Table C.1 | table transcription (2022-09-27 preprint; Tim drop 2026-07-25); published: g; -; bar; mL/s; mm; registry: g; -; bar; mL/s; mm (Darcy K recomputed in SI) | JFE 340 (2023) 111301 (Elsevier); preprint digitized, not redistributed; mu=3.5 mPa s convention inflates K ~3-7x vs G10 -- renormalize before cross-source comparison; the two loosest 17.5 g beds (B/C) sit ~1.3-1.7x above the stated 1.8e-14..3.6e-13 band (pump curve unpublished); Eq-11 permeability is POST-FIT (lambda=7.5 on these same 9 points) |
| `vacaguerra2023a/psd` — [vacaguerra2023a](../cards/vacaguerra2023a.md); Table 1 | table transcription (2022-09-27 preprint); published: um; -; um; %; -; registry: um; -; um; %; - | JFE 340 (2023) 111301 (Elsevier); preprint digitized; 3 distributions A/B/C; beta is the paper's central variable (widest C packs densest); needs a Rosin-Rammler (alpha,beta)<->GrindState adapter (no home in the contract) |
| `vacaguerra2023a/phi_coefficients` — [vacaguerra2023a](../cards/vacaguerra2023a.md); Table 2 (Eq. 9) | table transcription (2022-09-27 preprint); published: Pa; Pa/m; Pa; Pa/m; Pa/m^2; registry: same | JFE 340 (2023) 111301 (Elsevier); preprint digitized; PRINTED k3 is POSITIVE but the +k3*beta form is unphysical (omega ~0.48-0.62); registry adopts -k3*beta -- material-scoped (dark-roast arabica) |
| `vacaguerra2023a/omega_coefficients` — [vacaguerra2023a](../cards/vacaguerra2023a.md); Table 3 (Eq. 10) | table transcription (2022-09-27 preprint); published: -; 1/m; -; 1/m; registry: same | JFE 340 (2023) 111301 (Elsevier); preprint digitized; same -x3*beta sign correction as phi; material-scoped |
| `vacaguerra2023a/dry_porosity_validation` — [vacaguerra2023a](../cards/vacaguerra2023a.md); Figure 12 | figure digitization (2022-09-27 preprint; Tim drop 2026-07-25); published: - (measured vs calculated dry-bed porosity); registry: - | JFE 340 (2023) 111301 (Elsevier); preprint digitized; two independent vessels (60 mm stainless portafilter + 50 mm acrylic square); same lab, single coffee |

Prior authority: `ESPRESSO-CORPUS-LEVERAGE-002-C1`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### visualizer

**Access:** FOUND on 2026-09-23; 592 files / 263,950,985 bytes; 8 structured files, 1 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

Raw/bronze and normalized compressed JSONL shards, index and provenance are held. Structural inspection checks schemas without exporting values. Prior qualified canonical current-state count is 23,169; shard lines include versions and are not additional shots.

Operating histories and empirical baselines, subject to recent-public-window selection and unknown sensor location. User-entered TDS/EY is not qualified fraction chemistry. Prior boundary/onset and machine-prior decisions are exhausted as documented in EWP; new questions need a distinct decision or new semantics. Research access does not grant raw redistribution.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `visualizer/hydraulic_timeseries` — [visualizer_coffee](../cards/visualizer_coffee.md); visualizer.coffee API /shots/{id} .data series | repository/API pull (harvester); published: bar; g/s; g; degC; s; registry: Pa; kg/s; kg; K; s | public shots used with author (Miha Rekar) permission 2026-07-14 via documented API within published rate limits; PUBLICATION MUST credit Visualizer + collectively acknowledge contributing users; raw corpus gitignored (not redistributed); selection bias (public self-selected shots; showcase+diagnostic skew); no PSD, no basket geometry, no independent EY groundtruth; commanded (*_goal) vs achieved differ; node identity of 'pressure' per §5.9. flow_weight is the trustworthier channel (espresso_flow may be volumetric); privacy: user id salted-hashed, free-text dropped on ingest. |
| `visualizer/user_outcomes` — [visualizer_coffee](../cards/visualizer_coffee.md); visualizer.coffee API /shots/{id} drink_tds/drink_ey + sensory ints | repository/API pull (harvester); published: %TDS; %EY; 1-? sensory ints; registry: fraction; fraction; int | public shots used with author (Miha Rekar) permission 2026-07-14 via documented API within published rate limits; PUBLICATION MUST credit Visualizer + collectively acknowledge contributing users; raw corpus gitignored (not redistributed); sparse, self-reported; sensory sliders not inter-rater calibrated; do NOT use as an extraction-outcome gate (contrast the controlled Schmieder/Angeloni/Egidi sets). |

Prior authority: `ESPRESSO-CORPUS-LEVERAGE-002-C1`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### wadsworth2026

**Access:** FOUND on 2026-09-23; 2 files / 4,383 bytes; 1 structured files, 1 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

Table 1: 22 coffee/dial rows, PSD radius moments in SI, total/connected porosity, connectivity, surface area and permeability/error; 21 nonmissing permeability values.

Separate structure/permeability priors and source operators; keep total and connected porosity distinct. Grinder-specific dial and untamped/compacted states do not transfer automatically to EWP.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `wadsworth2026/table1_full` — `wadsworth2026_grindmap / wadsworth2026 (one paper)`; R. Soc. Open Sci. 13,252031 Table 1 (full: grind moments + porosity + k) | transcription (Tim drop); published: m; m^2; m^3; 1; 1/m; m^2; registry: m; m^2; m^3; 1; 1/m; m^2 | open access CC-BY-4.0 (DOI 10.1098/rsos.252031); CARD DISCREPANCY: OLS refit <R>~G gives beta=5.805e-5/R0=1.380e-4 (R2=0.994), NOT card's 4.3505e-5/1.016e-4 (~1.33x). Moments self-consistent (S=<R><R2>/<R3>). Operative map uses refit; card beta/R0 flagged for reconciliation. Raw 22-PSD zip still pending (0.6). |

Prior authority: `ESPRESSO-CORPUS-LEVERAGE-002-C1`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).

### waszkiewicz2025

**Access:** FOUND on 2026-09-23; 13 files / 3,639,227 bytes; 12 structured files, 12 exact repository byte matches. Remaining mappings are provisional at family level; source adapters establish subset identity.

traces_per_brew: 57,000 samples, 57 source labels; known duplicate leaves 56 distinct brews in 11 conditions. Columns distinguish pressure__bar (line), basket_pressure__bar, mass__g and derived mass_flow_rate__g_per_s. TDS: twelve 5-s fractions; calibration and brewer curves separate.

Controlled source-internal hydraulic reconstruction and fair baselines. Duplicate labels do not add experiments; source aggregation retained them historically. Pressure forcing cannot also validate pressure; derived flow and mass share information. Existing resistance/poroelastic negative decisions stand.

| Dataset / source locator | Directness and units | Rights; use limits |
|---|---|---|
| `waszkiewicz2025/traces_time_dependent` — [waszkiewicz2025](../cards/waszkiewicz2025.md); Zenodo formatted_measurements/time_dependent.csv (Figs 5/8) | repository pull; published: bar; s; g; g/s; registry: bar; s; g; g/s | CC-BY-4.0 (Zenodo 10.5281/zenodo.18046315); code GPLv3 not ingested; soft circularity: m_d(t) from TDS x Q on same rig; 11-13 bar dip below monotone model; basket vs line pressure both present (node id per RC-3/S5.9) \| S5.9 nodes: basket_pressure__bar = P_basket (basket gauge), pressure__bar = line/pump-side. |
| `waszkiewicz2025/tds_fractions` — [waszkiewicz2025](../cards/waszkiewicz2025.md); Zenodo formatted_measurements/tds.csv + replicates (Fig 7B) | repository pull; published: percent; s; registry: percent; s | CC-BY-4.0 (Zenodo 10.5281/zenodo.18046315); code GPLv3 not ingested; 5-s interval fractions; first fraction (2.5 s) single replicate |
| `waszkiewicz2025/static_calibration` — [waszkiewicz2025](../cards/waszkiewicz2025.md); Zenodo fit_parameters/static_model_calibration.csv (Fig 6 fit) | repository pull; published: bar; g/s; registry: bar; g/s | CC-BY-4.0 (Zenodo 10.5281/zenodo.18046315); code GPLv3 not ingested; P_c=12.4+/-3.0 bar weakly constrained (edge of measured range, ~25% unc) |
| `waszkiewicz2025/tds_solids_calibration` — [waszkiewicz2025](../cards/waszkiewicz2025.md); Zenodo fit_parameters/{tds,solids}_calibration.csv (Eqs 19-20 sigmoids) | repository pull; published: percent; g; s; registry: percent; g; s | CC-BY-4.0 (Zenodo 10.5281/zenodo.18046315); code GPLv3 not ingested; first_drop_offset 8.0 s; Phi(t) attributes all porosity change to dissolution (CT shows swelling too - untested) |
| `waszkiewicz2025/brewer_quadratic` — [waszkiewicz2025](../cards/waszkiewicz2025.md); Zenodo brewer_calibration.csv points + params (Fig 2B) | repository pull; published: bar; g/s; registry: bar; g/s | CC-BY-4.0 (Zenodo 10.5281/zenodo.18046315); code GPLv3 not ingested; single rig; DP=aQ^2+bQ+c |
| `waszkiewicz2025/mastersizer_psd` — [waszkiewicz2025](../cards/waszkiewicz2025.md); Zenodo measurements_mastersizer/mastersizer.csv (Fig 3) | repository pull; published: um; volume percent; registry: um; volume percent | CC-BY-4.0 (Zenodo 10.5281/zenodo.18046315); code GPLv3 not ingested; semicolon-delimited, UTF-8 BOM, transposed (bins as columns); bimodal ~50/100-200 um |
| `waszkiewicz2025/constants` — [waszkiewicz2025](../cards/waszkiewicz2025.md); Zenodo constant_parameters/constants.csv | repository pull; published: m; Pa*s; m; g; registry: m; Pa*s; m; g | CC-BY-4.0 (Zenodo 10.5281/zenodo.18046315); code GPLv3 not ingested; mu = pure-water @ 90C (G10 concentration-dependence not modeled); h0 and r_basket 'approximate' per source |
| `waszkiewicz2025/traces_per_brew` — [waszkiewicz2025](../cards/waszkiewicz2025.md); measurements_time_dependent/*.txt (57 raw per-brew JSON-lines traces) | repository pull (Zenodo source zip) + reduction re-implemented from the deposit's documented method; the deposit's own script is GPLv3 and is NOT ingested; published: bar; s; g; g/s; registry: bar; s; g; g/s | CC-BY-4.0 (Zenodo 10.5281/zenodo.18046315, record license); code GPLv3 not ingested; 57 records over 11 reference pressures (9 bar has 5) but 56 DISTINCT brews: 12-8-6_alt is an exact duplicate of 12-8-6 (its raw file is a strict prefix of the alt), declared in puckworks.data.WASZ_TRACE_ALIASES and retained here because the source aggregates both; shot-as-unit analyses pass include_aliases=False. 13 bar therefore has 7 records / 6 brews. Filename prefixes are NOT the reference pressure (10-2 is 11 bar, 12-8-2 is 13 bar) -- pressure is the median line pressure per the source's definition. The source's reduction is BAKED IN: t=0 alignment, Savitzky-Golay flow derivative (window 31, polyorder 1, ~3 s) and brewer-calibration basket-pressure subtraction, so these are smoothed and alignment-dependent, not raw instrument output. The source's excluded/ brews are NOT included. Time stored as an index on the exact 0-100 s 1000-point grid. NOTE the published aggregate's *_std columns are standard ERRORS (sem), so shot spread is recoverable only from this file. |
| `waszkiewicz2025/equilibrium_windows` — [waszkiewicz2025](../cards/waszkiewicz2025.md); measurements_time_dependent/*.txt (raw per-brew traces, NOT truncated at 100 s) | repository pull (Zenodo source zip) + per-window means; reduction re-implemented from the deposit's documented method (its script is GPLv3, not ingested); published: bar; g/s; s; registry: bar; g/s; s | CC-BY-4.0 (Zenodo 10.5281/zenodo.18046315, record license); code GPLv3 not ingested; 57 shots x 3 windows. The 110-120 s window is NOT usable as published: shot 9-1 has ENDED inside it (falling cup mass -> negative flow derivative -> -106 bar via the brewer subtraction), and alone drags the static refit to P_c ~ 82 bar. Excluding it is an exclusion the SOURCE did not make (9-1 is not in their excluded/ set). The repository's equilibrium observable is the 100 s endpoint, which reproduces the published static fit (P_c 12.394 vs 12.39; Q_c 1.907 vs 1.897). |

Prior authority: `ESPRESSO-CORPUS-LEVERAGE-002-C1`; scientific labels and additional uncertainty/use metadata remain in [AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).
<!-- families:end -->
