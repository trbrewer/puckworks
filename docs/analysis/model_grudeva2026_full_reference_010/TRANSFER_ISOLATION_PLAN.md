# 010 finite byte-transfer experiment

This prospective plan authorizes diagnostic rows A, B and C once each, in that
order. It performs no espresso calculation, full trajectory or dense replay.
The exact identities and resource limits are in `TRANSFER_ISOLATION_PLAN.json`.
All historical plans, failures, payloads and successful replays remain unchanged.
Full-reference qualification remains incomplete; PHYSICAL_VALIDATION=NOT_ESTABLISHED.

The question is where bytes first diverge in an instrumented transfer, or whether
the discrepancy is absent on these declared tests. The original 54-byte extraction
comparison is reused; no full comparison is repeated to expand its witness table.
The original archive failure, replacement capture failure and extraction incident
remain three separate incidents with unestablished mechanisms.

## Inputs and hash domains

The failed parent archive's individually matching `segment-1.npz:D.npy` is the
source. Resolve it and the complete failed extraction through the retained
execution configuration; private locators are bound externally by `INPUTS.json`.
Neither input is admitted as a qualified trajectory or accepted-state recovery.

| Domain | Length (bytes) | Identity rule |
|---|---:|---|
| Entire ZIP file | 20,116,525,410 | Original manifest SHA, before A and after C |
| Compressed D member | 15,260,274,506 | Interval at ZIP offset 2,427,743,805; no separate digest claim |
| Decoded complete NPY member | 21,458,960,192 | 128-byte header plus payload; prospective ordered chunks and aggregate |
| Numeric payload / canonical C bytes | 21,458,960,064 | Original D SHA; opaque bad fixture has its own distinct SHA |
| NPY header | 128 | Exact header SHA and restricted parse: `<f8`, C, `(18002,6,24834)` |

No pickle, Python expression evaluation, array loading or floating-point conversion
is used. The standalone command imports neither Puckworks, NumPy nor SciPy.

## Finite rows and checkpoints

**A** uses the actual installed `shutil.copyfileobj` at 4 MiB with read/write taps.
Every decoded chunk is prospectively hashed and retained in a separate complete
raw-member spool. The spool write and source buffer are checked; pre-write and
post-write buffer digests, requested/returned counts, logical and descriptor
offsets, timestamps and blocking status are recorded. Destination bytes are read
after each flush, after final flush, after fsync, and in a fresh process after
close. Later passes verify every chunk against its prospective commitment and
the retained decoded chunk. The ordered JSONL commitment file and full decoded
member have distinct aggregate identities. ZIP CRC/EOF are recorded.

This is an **instrumented transfer**, not an exact timing reproduction: the
additional spool, hashes, flushes and reads change buffering and allocation timing.
The historical buffered writer's missing short-count check is inspected, not
declared the historical cause. Neither absent fsync nor close floating values
establish a mechanism.

**B** admits the quarantined file against its own bad-copy identity as an
`OPAQUE_BYTE_FIXTURE_NOT_SCIENTIFIC_RECOVERY`. GNU `dd` uses ordinary reads/writes,
`iflag=fullblock conv=excl,fsync`, with a syscall summary; no reflink or sparse
shortcut. A fresh reader checks the full source and destination, exact counts,
both hash domains and source stability.

**C** uses installed Info-ZIP `unzip -p` to decode the same original member into
two GNU hash processes (complete member and payload), cross-checked with the
bounded standard-library reader. It records all three exit codes and requires
the original payload identity. If A passed, C also compares every chunk to A's
retained spool, reverifies that spool's whole/payload identities, and retains all
observed differing offsets. Without an available verified spool, a C digest
disagreement has no byte-location claim. No further large destination is written. Info-ZIP
does not link libz; CPython does. Both hash commands use libcrypto, and all local
rows share the host, kernel, filesystem and source; these are explicit limits.

Essential failure JSON precedes witness writing. Disagreements retain bounded raw
chunks, all differing byte offsets/counts and secondary write errors. A digest
alone is never called a saved prior byte. Failed outputs remain exclusive and
quarantined; there is no successful reference manifest or loader exception.

## Resources, controls and stopping

The three retained complete new files require 64,376,880,576 bytes. Application
buffers are bounded (estimated under 256 MiB concurrently); filesystem cache can
grow and is accounted separately. Intake showed about 259 GB available memory
and 1.30 TB disk. An exclusive supervisor checks 8 GiB available memory / 100 GiB
disk before starting, samples process-tree RSS and headroom each second, and
stops at 2 GiB available memory or 8 GiB disk. Existing cgroups have no memory
maximum and report no OOM events; limits are not changed.

Thirty-three inexpensive byte controls pass, including small A/B/C executions and fresh
process witnesses. A development control caught an invalid initial `dd` option;
its failure is retained and the installed documented conversion operand is used.
That correction is to this new diagnostic, not a cause of the historical incident.
These fixtures invoke zero solvers. Focused review identified two further defects
in this new diagnostic: eager secondary witness reads could hide a known mismatch,
and destination-only extension chunks repeated offsets. Both are corrected and
covered by negative controls. The unexecuted first plan is retained externally
by its original identity; the revised binding explains this pre-execution delta.

Each row runs once. After a mismatch an independent row may proceed only with
stable admitted inputs and safe headroom. A demonstrated code defect would need
a separately recorded correction identity before any affected diagnostic rerun.
No blind re-extraction, resident replay, scientific retry or hardware stress is
authorized. Accessible kernel error records show no entries; SMART access is
denied and EDAC counters are unavailable. These are visibility limits, not health
certificates. Current systemd/virtualization/mount observations do not establish
which physical host handled historical incidents.

No already authorized independent host is presently available. Another process,
CI worker without matched data, or same-host environment is not that contrast.
If no owner-provided access becomes available, deliver the reproducer with
`INDEPENDENT_ENVIRONMENT_CONTRAST_UNAVAILABLE`; do not provision resources.
