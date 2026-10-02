# Research evidence snapshot — 2026-10-01

Start with the [canonical report](../ESPRESSO_PROGRAMME_REVIEW_2026-10-01.md).
This directory is research-only: production imports and registry entries do not use it.

## Check immediately, offline

From a clean repository checkout, with Python 3.10+ and no external packages:

```sh
python docs/research/espresso_programme_review_20261001/check_aggregates.py
python -m unittest discover -s docs/research/espresso_programme_review_20261001 -p 'test_aggregates.py' -v
```

The checker recomputes signed mass/component sums, units, author denominator,
run/quadrature joins and output/trajectory decompositions from **supplied aggregates**.
It verifies one SHA-256 list for this directory's snapshot, without hashing mutable
production files. Sign, cup-value, kg/g/mg and file-tampering adversaries must fail.
The 0.00000001 mg arithmetic tolerance concerns floating-point summation of stored
values, not the study's separate 0.01 mg reporting target or physical accuracy.
It does not execute trajectories, infer missing observations or validate physics.

## Included evidence

- `sparse/`: original reference/tighter endpoints and quadrature, DAE/Jacobian/N6
  qualification records. These describe producer executions, not new publication runs.
- `balance/`: 27 endpoint rows, 54 timeline rows, 2,616 sampled cumulative history
  records, output/trajectory decomposition, three-run statistics, operator and
  functional checks, and logical identities for omitted raw outputs.
- `review/`: historical gate/delivery census, F13 before/after and F15 conversion
  records. The census is tied to the September audit pin.
- `native/`: synthetic native audit scenarios/endpoints, not measured coffee rows.
- Discrete/Jacobian derivations; minimal sparse adapter and dimensional reducers.

[EVIDENCE_MAP.csv](EVIDENCE_MAP.csv) binds included copies and omitted producer
reports. `manifest_verified=false` means that selected source was not named in
its available original manifest; its observed hash is still recorded, not invented
as a prior attestation. Intentional preface/navigation edits have distinct snapshot
hashes. Original manifests remain unchanged. No logs/private paths/raw rows are
needed for this offline checker.

## Optional pinned-source replay — NOT executed by publication

Obtain `jamiemfoster/Espresso@79ebefb72446eb706084e2392cab64bf0fad93a2`,
tree `cb6f42ce893da256d1d6974e724166044e77af94`, through permitted means.
Use an already-installed supported Octave (the study used 8.4.0 with KLU), a fresh
writable output directory, and NumPy/SciPy for the Python reductions. Verify the
actual backend and thread limits. No installation or network occurs in the scripts.

```sh
python docs/research/espresso_programme_review_20261001/replay/prepare_replay.py \
  --author-source /path/to/pinned/Espresso --out /path/to/NEW-replay --case reference
cd /path/to/NEW-replay
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 BLIS_NUM_THREADS=1
timeout 1800 /path/to/octave-cli --quiet --no-gui verify_sparse.m > qualification.log 2>&1
# Proceed only if fixture/derivative qualification exits zero.
cd reference
timeout 1800 /path/to/octave-cli --quiet --no-gui run_case.m > run.log 2>&1
# Proceed only after exit zero and complete output.
cd ..
python reduce_source.py reference
python reduce_balance.py reference --out new_balance.csv
```

Replace the explicit placeholder paths; they are not owner-private locators.
The preparer refuses an existing output workspace and hashes all six author files.
Cases `tight` and `early` select archived templates; each requires a separate fresh
workspace. This is a recipe, not permission to start another campaign.
The qualified numerical adapter/templates and reduction logic are retained unchanged;
the new preparer and balance CLI only expose explicit paths and fresh destinations.
The original `reference.diff` and `tight.diff` records are inspection aids, not
apply-ready patches: their final no-newline hunk was emitted as `-end+end` and
`git apply --numstat` rejects it. Their original bytes are preserved. The replay
uses the complete, independently hashed `.m` templates, not those diff records.
The optional fixture checks the installed sparse path; another version cannot simply
inherit the original result. No claim of MATLAB equivalence follows.

Returned moment and raw boundary histories are needed to reconstruct the attribution.
Old diagnostic snapshots are not complete trajectories or restart states.
The original short N6 comparison records are included; their full trajectories and
the operator-test input snapshots are omitted. The original operator test is
documented, not claimed runnable from aggregate tables alone.

## Rights, attribution and omissions

Author-code derivatives (templates, Jacobian and related adapters) retain
[Jamie Foster's MIT notice](replay/LICENSE.author), copyright 2018; pinned author
source is external. First-party research utilities are governed by PW's software
license. No new software-authorship claim is made for an automated audit.

Pannusch/Schmieder source files and derived C01 records carry separate CC-BY-NC
terms; **none of their row tables is included** or relicensed under MIT. The report
uses factual prose/citations and identities. Other private observations, predictions,
source PDFs, full trajectories, native fields, environments, prior ZIPs and author
requests/correspondence are omitted. Existing public per-delivery records retain
their own rights notices.

This snapshot supports aggregate verification, **not complete trajectory replay**.
Hashes of omitted records identify bytes; they are not access grants or working
download links. No physical validation, source repair, new fit, Stage F/D,
author contact, deployment or merge is authorized by this archive.
