# Source authentication and observational contract

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING.
**PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

## Originals actually read

1. Alessia Perticarini, *Predictive Models in Espresso Coffee Percolation*,
   University of Camerino doctoral thesis, XXXVI cycle, deposited 2024.
   [Official PDF](https://pubblicazioni.unicam.it/retrieve/cf1d5052-f17f-4c11-96e2-07533acdbb41/02_28_24%20-%20Perticarini%20Alessia.pdf).
   Downloaded 2026-10-24; **189 PDF pages**, file SHA-256
   `248d480cc2ab3353799fcaa886bb1be3f6cfbe7a9f15e1cdf9d4950827424c7f`.
   It matches the reviewed hash and the configured external collection's existing
   `pdf/06_other_papers/06_other_papers/20260727/02_28_24 - Perticarini Alessia.pdf`.
   The external root was resolved from `~/.config/puckworks/data_sources.json`;
   no corpus rescan was performed.
2. N. Egidi, J. Giacomini, E. Larsson and A. Perticarini, *An improved numerical
   scheme for coffee Extraction Yield evaluation*, Chaos, Solitons and Fractals
   188 (2024), 115625, [DOI](https://doi.org/10.1016/j.chaos.2024.115625).
   [Official deposited PDF](https://pubblicazioni.unicam.it/bitstream/11581/485884/1/2024AnImpNumSchEYEval.pdf).
   Downloaded 2026-10-24; **10 PDF pages**, file SHA-256
   `1aba69278444d107ce5172eb29ba7b37883491fe0b32dfd9bc8898632e203a33`.
   It matches the reviewed hash. No source-identity mismatch occurred.

PDF page numbers here are counted from one. Inspected thesis methods: printed
pp.85–86 / PDF pp.97–98, measurement/repetition text and Table 4.1 context:
printed pp.87–89 / PDF pp.99–101. Table 4.2: printed p.90 / PDF p.102;
Table 4.3: printed p.91 / PDF p.103. Text layers and full rendered tables,
headers, units and captions were inspected. Egidi methods, Table 1 context and
Table 2 were inspected on article/PDF p.6, including its full rendered page.
The time column is τ [s]; p [bar] is the native pressure label; sigma belongs to
TDS [%], explicitly described as its standard deviation in both table captions.

Only factual numerical tables and a new computed figure are committed. PDFs,
facsimiles, text extracts and the source-audit scratch script remain outside Git
(`/tmp/perticarini-pressure-source`, `/tmp/perticarini-pressure-egidi`). No blanket
source redistribution license is asserted. Numerical reproduction needs no PDF,
network, external mount, new dependency or source-artwork access.

## Complete cell authentication and publication lineage

Both schemas were read directly. Each row was matched by temperature, nominal
pressure and normalized grind, with coffee authenticated by the table caption
and methods (also explicit in the Cibao CSV). All six numeric columns were
compared as exact decimal values: T, p, τ, TDS, TDS sigma, EY. Native grind labels
were inspected visually. A separate scratch text-layer parser confirmed the
visual comparison across every row; trailing decimal zeroes are numerically
identical. No scientific value or canonical dataset identity was changed.

| Canonical dataset | Primary location | Rows | Numerical cells | Cross-publication check |
|---|---|---:|---:|---|
| `perticarini2024/ey_tds_cibao` | Thesis Table 4.2, PDF102 | 18/18 | 108/108 agree | Not duplicated in Egidi Table 2 |
| `egidi2024/table2` | Thesis Table 4.3, PDF103 | 12/12 | 72/72 agree | Egidi Table 2, PDF6: all 12 labels and 72 numeric cells also agree |

**Thesis Table 4.3 and Egidi Table 2 present the same Modœtia observations.**
Their condition labels and numerical cells agree, their coffee/apparatus/recipe
and repetition descriptions agree, and Egidi describes the campaign as previously
described (its ref.10). The thesis's RBF discussion is the same publication/model
lineage. Preserve `egidi2024/table2` as the sole canonical identity; no second
12-row table, campaign or independent replicate evidence is created here.
This identity does not turn inferred physical-shot membership into authenticated
raw shot IDs. The derived [observations.csv](observations.csv) is a 30-condition
view, not a new independent dataset or 30 individual shots.

| Input | File SHA-256 (raw bytes) | Git blob SHA-1 |
|---|---|---|
| `puckworks/data/perticarini2024/ey_tds_cibao.csv` | `2c5fae8319d41c690b7e23ea00ddfc722e08c01ebcd8f012dafb1820a8fc6703` | `0c657a30b7c8e048459e79a0b6e34980cba26f75` |
| `puckworks/data/egidi2024/table2_egidi2024_tds_ey.csv` | `1b5cd8891472d2d432fcb96a59e167d8fcca8b8e70a0a75187d810bf8a8e4419` | `2f83cd9b59349cd2cf0e9b085ccf5ac03263cff5` |

File SHA-256 hashes the original bytes; Git's blob SHA-1 includes the blob header.
The two inputs retain their existing line endings; new derived CSVs use LF.
The JSON bundle records these input identities, source hashes/pages and assumptions.
The stable condition ID encodes dataset, authenticated coffee, exact temperature
string, nominal pressure and normalized grind. Source labels (`Extra Fine`, etc.)
and canonical CSV spellings (`extra_fine`, etc.) are both preserved. Row order is
not a join key. Support is exactly 12/6/6/6 across Cibao93.4/Cibao90.4/
Modœtia93.4/Modœtia90.4; missing conditions are not imputed.

## What the methods establish, and what they leave unknown

Procedure 1 uses 20 ± 0.1 g dry coffee, nominal beverage endpoint 40 ± 2 g and
nominal tamp force 20 kgF. Equipment: Mythos 1 grinder, PUQ PRESS M2 tamper,
Victoria Arduino VA388 Black Eagle and VST Competition basket, internal radius
29.25 mm and height 26 mm. The thesis specifies machine settings adjusted by a
professional barista. The nominal 6/9/12-bar labels are retained without conversion.
The pressure reference (gauge/absolute), sensor node and actual pressure history
are not established; no one-bar subtraction or puck pressure-drop interpretation.

The thesis reports three extraction samples per configuration in the chemical
campaign and explicitly states that TDS and EY are averaged over those three.
The displayed sigma is **TDS standard deviation**. The description does not
separately specify the per-condition τ statistic, duration repetition count or
spread, rounding rule, timing equipment or clock start/stop convention. Egidi p.6
does not resolve those gaps. Thus τ is **reported condition duration** throughout:
no n=3 duration means, 90 timed-shot inputs, timing SD/SE/CI, or use of TDS sigma
as duration uncertainty. Integer printing alone does not establish nearest-second
rounding. Unknown shot-to-shot timing variability remains unknown.

The source defines Optimal by the recipe giving about 40 g in 25 s at 93.4 °C and
9 bar; smaller burr gaps produce finer labels and larger gaps coarser labels.
This supports only ordinal `extra_fine, fine, optimal, coarse, extra_coarse`
within coffee. Named grinds are not calibrated particle-size equivalents between
coffees or mapped to Cameron grinder dials. The Cibao extreme 12-bar rows are
only at 93.4 °C; no full-factorial pressure study is inferred.

Table 4.1's per-grind mean times pool pressure and temperature and are excluded.
Egidi Table 1's pooled Fine/Coarse times (40/20 s) differ from thesis Table 4.1
(41/21 s); this contextual difference is retained without reconciliation because
neither pooled table enters the analysis. It does not alter the complete Table
4.3/Table 2 cell agreement. Model times and fitted/model-derived Darcy fluxes
are excluded. Actual condition-specific beverage masses remain unknown. Nominal
endpoint duration is not measured flow: no 40/τ conversion, per-shot mass inference
from TDS/EY summaries, intrinsic permeability or resistance inference occurs.

The new duration analysis leaves Egidi's historical independent EY/TDS **range
bracket only** qualification intact. It neither upgrades that model's p/T
prediction nor reconciles unrelated model equations, PSD conventions or backlog.
