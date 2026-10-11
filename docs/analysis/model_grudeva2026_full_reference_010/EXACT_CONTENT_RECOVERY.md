# Exact-content recovery — stopped before payload admission

**FULL_REFERENCE_QUALIFICATION_INCOMPLETE. PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

The owner authorized exact-content reuse of four retained segment-1 coefficient
members, superseding the earlier cross-execution prohibition for matching bytes
only. The live draft PR matched starting reviewed head
`5177da6b8ffeab54e8b6a29010b5abac4b95b677`; work used a new isolated checkout and
exclusive `controlled-rerun-20261010/exact-content-recovery-20261010` directory.

All four complete numeric identities (dtype, shape and payload SHA256) agree
between committed `RECOVERY.json`, `DENSE_DIAGNOSTIC_AMENDMENT.json` and this
anchor's original `trajectory/SOURCE_COMMITMENT.json`. The latter retains SHA256
`909b775844dbd822979d56b29d0dcd8c64bc27b0ec8d4f5db05a1cabefe9af6a`.
The [compact record](EXACT_CONTENT_RECOVERY.json) contains these direct comparisons.
They are comparisons of recorded identities, **not current payload admission**.

The selected sources were transfer A's complete `decoded-member.bin` for D and
the previously selected diagnostic input files for shift, denom and order. The
known bad extracted D copy was excluded. No historical accepted states or
synthetic diagnostic y arrays were selected.

## Actual stop

The first supervised process exited **-11 (SIGSEGV)** after 2.023 seconds, during
the existing runner's `environment()` call. With `PYTHONFAULTHANDLER=1`, stderr
records garbage collection and `importlib.metadata` file enumeration through
`pathlib`/`posixpath`. This identifies the observed execution location; **the
cause remains unestablished**.

The external supervisor preserved the actual child exit, stdout, stderr and
resource samples. It did not terminate the child for resource safety: sampled
minimum available memory was 259,556,909,056 bytes, minimum free disk was
1,237,848,596,480 bytes, and peak sampled child RSS was 79,592 KiB. These samples
do not establish environment health or exclude other causes.

The crash preceded candidate payload reads, successful environment/executable
identity collection and the prospective recovery receipt. Current candidate
identity/finiteness, complete-set fresh readback, equivalent interpolant fidelity
and full numerical post-processing are therefore **NOT_RUN**. No current payload
disagreement was observed, and no matching payload is newly admitted.

The user's explicit unexpected-crash stop was applied: no retry, alternate
candidate, environment change, additional solver execution or infrastructure
investigation. The metadata-only equality check above was completed for truthful
closeout without importing scientific code or reading numeric payloads.

## Preserved scope and accounting

The earlier 24-member partial recovery and its provisional numerical results
remain at their recorded scope; they were not reverified or promoted here. The
two prior local QA SIGSEGV records and their unresolved causes remain preserved.
This continuation adds **one separate failed preflight process**, not a scientific
trajectory, independent repeat, payload-integrity failure or numerical gate miss.

Recovery adds **zero solver executions**. Cumulative accounting remains **three
completed full trajectories / six BDF segments; zero admitted full reference
rows**. Repeat and twelve refinements remain **NOT_RUN**. Original live-source
interpolant evidence remains unavailable; the proposed equivalent assessment was
not implemented or executed after the stop.

No repository executable, scientific formula, setting, matrix, binding, threshold,
error budget or prior 010 record changed. Unchanged focused tests, mathematical
reviews and large diagnostics are reused under SCI-GOV-001. Only metadata and
generated-status checks apply locally; the final candidate's required hosted CI
and scoped review are recorded in PR #333 and the external delivery receipt.
No additional numerical test or diagnostic replay is used to exercise this crash.

For inspection, read external `candidates-exit.json` and `candidates.stderr.log`
first, then the start/resource records and retained `verify_candidates.py` and
`supervise.py`. Their hashes are in the compact record. The scripts are retained
execution evidence, **not authorization to retry**. No successful archive or
recovery manifest was published.

PR #333 remains draft and unmerged, auto-merge disabled, and issue #67 open.
No production/default/lock/EWP change or downstream comparison.
**EXECUTION_ENVIRONMENT_INTEGRITY_UNRESOLVED. PHYSICAL_VALIDATION=NOT_ESTABLISHED.**
