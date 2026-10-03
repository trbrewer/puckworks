# Owner handoff — MODEL-GRUDEVA2026-REFERENCE-002

Disposition: COMPARATOR_QUALIFICATION_INCOMPLETE. One draft PR referencing #67;
auto-merge disabled. Do not merge or close #67. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
The owner can review the bounded negative result; no successor is selected.

The comparator failed conservation and bed/time refinement. Its analytical
radial checks do not make it an oracle. No merged-solver or extraction defect
was demonstrated. Figures 3/4 retain their original FAIL dispositions and
Figure 5 remains FIG5_REFERENCE_INCOMPLETE. The two finest-time records lack
the terminal saved observation; the final scheduler fix has focused software
coverage but no new coupled qualification after the 14-attempt cap. Exact
executed source hashes and failed attempts are retained in RESULTS.json.

## Offline reproduction

Python with the repository's declared NumPy/SciPy dependencies; no network on
import. Use an external directory for arrays/logs. `--mode run` exits 2 to mark
an unqualified single run; a successfully executed process is not acceptance.
`analytic` exits zero only when its analytical gates pass. The report exits 2
for incomplete qualification and never feeds the failed comparator to the
publication scorer.

```bash
export OPENBLAS_NUM_THREADS=1
python -m puckworks.analysis.grudeva2026_reference_002 --mode analytic --output "$GRUDEVA_EVIDENCE/analytic.json"
python -m puckworks.analysis.grudeva2026_reference_002 --mode run --bed 128 --shells 64 --dt .001 --horizon 8 --output "$GRUDEVA_EVIDENCE/normal.json"
python -m puckworks.analysis.grudeva2026_reference_002 --mode run --bed 256 --shells 64 --dt .001 --horizon 8 --output "$GRUDEVA_EVIDENCE/bed_fine.json"
python -m puckworks.analysis.grudeva2026_reference_002 --mode run --bed 128 --shells 128 --dt .001 --horizon 8 --output "$GRUDEVA_EVIDENCE/radial_fine.json"
python -m puckworks.analysis.grudeva2026_reference_002 --mode run --bed 128 --shells 64 --dt .0005 --horizon 8 --output "$GRUDEVA_EVIDENCE/time_fine.json"
python -m puckworks.analysis.grudeva2026_reference_002 --mode run --bed 512 --shells 128 --dt .0005 --horizon 8 --output "$GRUDEVA_EVIDENCE/combined.json"
python -m puckworks.analysis.grudeva2026_reference_002 --mode run --bed 32 --shells 16 --dt .01 --horizon 8 --diffusivity 0 --output "$GRUDEVA_EVIDENCE/limit.json"
python -m puckworks.analysis.grudeva2026_reference_002_report --runs-directory "$GRUDEVA_EVIDENCE" --baseline-directory "$GRUDEVA_308_ARCHIVE" --output "$GRUDEVA_EVIDENCE/replayed-report.json"
```

These commands document reproducibility, not authorization for another local
execution in this capped task. The final scheduler fix changes endpoint
observations; current-source reruns receive new identities. Exact historical
replay uses the source-at-execution copy with SHA in RESULTS.json, held beside
the raw runs. Pilots use (64,32,.002,.4) and (128,64,.001,.4). The frozen
extra initial bed-finer row uses (512,64,.001,8). The full attempt ledger
records both scheduler failures and every successful call; no failed trial was
removed from the count. `--attempt-manifest` optionally attaches that retained
ledger to a report. Reports without it do not recover historical resource use.

Independent publication extraction, leaving the fixture untouched:

```bash
python tools/grudeva2026_extract_reference.py --article-pdf "$GRUDEVA_ARTICLE_PDF" --output "$GRUDEVA_EVIDENCE/reextracted.json"
```

Resolve private paths through the existing data-source configuration. Do not
publish source PDFs, supplement text, raw arrays or private correspondence.
The source PDF's container hash may differ while the embedded figures and
coordinates agree; compare the recorded identities explicitly.

## Acceptance checks

Baseline focused QA: 34 passed, 3 deselected. Baseline full offline QA:
5450 passed, 65 skipped, 63 deselected, one warning, 1118.94 seconds. This
minimal dev environment has optional dependency skips; totals differ from
#308's fuller environment and are not concealed as identical coverage.
Candidate focused QA: 47 passed, 3 deselected (including the independent-review
observer-support regression). Analytical/source/observer tests
are software evidence separate from the comparator's failed numerical gates.

```bash
python -m pytest -q tests/test_grudeva2026_reference_002.py tests/test_grudeva2026_cli.py tests/test_grudeva2026.py -m 'not slow'
python -m pytest -q -m 'not slow and not live and not gpu and not external_data'
ruff check puckworks/ tests/
mypy
python -m build --outdir "$GRUDEVA_EVIDENCE/dist"
python tools/packaging_check.py "$GRUDEVA_EVIDENCE/dist"
```

Candidate full QA, hosted checks and the one independent nonhuman exact-head
review are recorded in the PR receipt after the candidate commit exists.
At document preparation they are pending, not PASS. Required hosted contexts
are read from the active ruleset. No repeated review of unchanged work is
requested. Publication-reference failure and CI status remain separate.

Production Grudeva 2025/2026, failure-first CLI, unavailable dimensional outputs,
censored/zero-discharge behavior and #308 historical artifacts are unchanged.
EWP's owner checkout remains at its original clean local head (which is not its
live main head); no checkout, dependency refresh, solver execution or file edit
was performed there. Preserved tag v0.1.4-public.1 remains
26359865621510510e381bc69bb280d2d8dae412. Owner worktrees are preserved.
