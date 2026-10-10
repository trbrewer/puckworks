# 010 transfer isolation: bounded result

**EXECUTION_ENVIRONMENT_INTEGRITY_UNRESOLVED.** The instrumented ZIP transfer
and independent decoding passed. The plain-file row stopped before copying:
its quarantined input no longer reproduced its recorded identity. A bounded
inspection also found seven discrepancies among 32 previously recorded witness
values. The mechanism remains unestablished; another anchor is not recommended
on the current unresolved environment.

**FULL_REFERENCE_QUALIFICATION_INCOMPLETE. PHYSICAL_VALIDATION=NOT_ESTABLISHED.**
Two historical full trajectories / four BDF segments remain the entire scientific
execution history. This continuation adds **zero** full trajectories, zero dense
replays and zero qualified full rows. Thirteen frozen scientific rows remain
NOT_RUN. There was no model, solver, precision, parameter or threshold change.

## Actual finite executions

| Row | Outcome | Recorded wall seconds | Peak sampled process-tree RSS (KiB) |
|---|---|---:|---:|
| A: instrumented CPython ZIP-member transfer | PASS; all 5,117 chunks and later checkpoints match | 331.21 | 81,168 |
| B: ordinary file-to-file transfer | FAILED INPUT ADMISSION; `dd` never invoked, no copy created | 22.01 | 27,864 |
| C: independent Info-ZIP decoding/check | PASS; 5,117 chunks, original payload and A spool match | 299.25 | 41,788 |

Each row was attempted once, in frozen A/B/C order. There were no retries or
substituted inputs. B's failure did not invalidate the independently admitted
original ZIP used by C. Minimum sampled available memory was 258,789,011,456
bytes; disk headroom remained above 1.25 TB. No safety stop or resource-limit
change occurred. Two complete new diagnostic files retain 42,917,920,384 bytes;
the planned third file was never created.

A preserves exact decoded chunks, prospective per-chunk commitments, pre-write
and post-write buffer identities, requested/returned byte counts, offsets and
timestamps, immediate destination reads, final flush/fsync checks, and a fresh
reader after close. ZIP CRC matches and EOF is reached. Every requested count
was returned, including the last 900,928-byte chunk. No divergence was observed
at these boundaries. Instrumentation changed timing and buffering; this is not
an exact recreation of the historical copy operation.

C uses Info-ZIP's independent decoder, with whole-member and payload GNU hash
processes and a standard-library cross-check. All three subprocesses returned
zero. C also reread and reverified A's actual spool and found no differing
bytes. The final whole-ZIP hash matches the original manifest. GNU/Python
hashers share libcrypto; all local rows share the execution environment.

The verified original payload remains
`dde6342fe349b2c33890c66d8316c2535f993121fcddeee4cc1b58a08292ae3a`.
The complete decoded NPY member (128-byte header plus payload) is
`eceeca99f75e30e7dbad8656b43a7ef3790f6b0c09b7b23c028bd7ccb3d0d871`.
These identities qualify diagnostic bytes only, not the failed parent trajectory.

## New divergence and bounded witnesses

B expected the retained bad-copy payload identity
`e461a67c1e5e347dbd57c2440fa332280b11b376399e1fb7c900624b2bdb64ca`.
Its single admission scan instead produced
`23e17d8ac0033a09e370834f49339200b5fafde7beb69f59d828bcc18982109c`.
The earliest new observed discrepancy is therefore **source admission before
the plain-file copy**, not a `dd` write or an A extraction boundary.

`B/FIRST_FAILURE.json` durably records both digests and the failure time. No
prospective per-chunk record exists for that admission scan, so its new mismatch
cannot be fully localized. The early return did not retain the scan's complete
member hash or read-buffer bytes; those fields are unavailable, not inferred
from later reads. Header/length/dtype/shape checks reported no other failure.

A prospectively recorded, solver-free follow-up read only the existing 32
eight-byte witness locations: **256 bytes total**. Twenty-five match the retained
bad-copy witness values; all seven differing sampled values are listed below.
Offsets address the complete NPY member, including its 128-byte header.

| Member byte offset of eight-byte value | Prior recorded target bytes | Current read bytes |
|---:|---|---|
| 14,389,286,776 | `faec3c29af80c0be` | `faec3c88af80c0be` |
| 14,389,294,520 | `52ff6d70ccedd0be` | `52ff6df0ccedd0be` |
| 14,389,296,440 | `1d9779a4db1ec6be` | `1d9779a5db1ec6be` |
| 14,389,309,624 | `f65d921c417de1be` | `f65d929c417de1be` |
| 14,389,310,200 | `0ea4c31837b6e2be` | `0ea4c31c37b6e2be` |
| 14,389,317,944 | `06d592b39edcfabe` | `06d592b59edcfabe` |
| 14,389,318,136 | `3b3edb8b0240f1be` | `3b3edb8f0240f1be` |

Each sampled discrepancy is one byte within the listed value. Seven is the
complete count **within these 32 sampled witnesses**, not the full file's new
difference count. The first original witness still matches its recorded bad
bytes. No full comparison, search over substitutions or reconstruction was run.
The earlier 54-byte comparison remains unchanged historical evidence.

Device, inode, length, mtime and ctime match intake. This does not prove byte
stability or a physical cause. No historical artifact was opened for writing by
this continuation; both original locations remain retained. The bad copy's
historical byte identity is currently unreproduced, so its unchanged contents
cannot be claimed merely from preservation of its path/metadata.

## Interpretation and infrastructure recommendation

The A extraction discrepancy was **NOT_REPRODUCED_ON_DECLARED_TRANSFER_TESTS**.
C independently confirms the original decoded bytes on this workload. B provides
an unresolved historical-record/current-read discrepancy outside espresso code;
the plain-file transfer contrast is unavailable because its input failed admission.
No mechanism is established for this new observation or any of the three earlier
incidents. **HISTORICAL_ROOT_CAUSE_UNESTABLISHED** remains unchanged.

No model-side fix follows from these results. Preserve the affected file and
records. The concrete next infrastructure step is owner/admin read-only access
to relevant memory/storage-health evidence and a matching byte test on separately
authorized independent hardware/storage, with transferred input identities
verified. No independent host/access was available here:
**INDEPENDENT_ENVIRONMENT_CONTRAST_UNAVAILABLE**. Do not change expected hashes,
repair evidence or retry this packet until a favorable result appears.

An instrumented anchor is **not recommended on the current unresolved environment**.
A future decision can use A/C's positive evidence, the earlier successful resident
replays and an adequately established execution environment; it requires separate
owner authorization. Lost historical internal state need not be reconstructed
as an impossible prerequisite, but the current byte disagreement remains a
concrete operational concern.

Current observations show systemd, `systemd-detect-virt` returning `none`, and
ext4 on the visible storage device. Historical records do not prove the same
physical host handled earlier incidents. Accessible kernel error windows have
no entries, SMART permission is denied, and EDAC counters are unavailable.
Neither this visibility nor passing CI/fsync/fresh reads establishes hardware
health. No unrelated historical scientific result is invalidated by this packet.

## Controls, preservation and delivery

Thirty-three bound byte controls pass, including negative controls and fresh
process witness reproduction. Development retained one failed control from an
incorrect new `dd` option; installed `conv=excl,fsync` fixed that diagnostic.
Independent review also identified two new-checker defects, corrected before
large execution: a secondary witness read could hide a known mismatch, and
multi-chunk destination extensions repeated offsets. No demonstrated historical
transfer or numerical defect was corrected. These controls invoke zero solvers.

The 40 prior 010 documents and six existing implementation files are unchanged.
The original matrix, continuation and dense diagnostic bindings are preserved.
Both successful resident replays are reused by their original identities; no
replay, original scientific campaign or publication comparison was rerun.

Base: `3cd308ac5bed39acff3d995108b5178a53c982ee`; starting head:
`84702ddaa6e91b64e807381a2199286f8cad6fbf`. The new plan SHA is
`c10511966bb505fd0d0235ea73388933ad1f1a846b961b96eeea334bc632e366`.
Exact command/environment identities, machine-readable outcomes and external
record hashes are in [the results](TRANSFER_ISOLATION_RESULTS.json),
[plan](TRANSFER_ISOLATION_PLAN.json) and [evidence manifest](TRANSFER_ISOLATION_EXTERNAL_EVIDENCE.json).
[Reproduction instructions](TRANSFER_ISOLATION_REPRODUCE.md) include the small
controls and recorded commands. Delivery head/tree, ordinary QA, exact-head CI
and the scoped independent review are separate receipts; successful software QA
does not promote this transfer packet or full reference to numerical qualification.

PR #333 remains draft/unmerged with auto-merge disabled; issue #67 remains open.
Production, defaults, locks, source cards, 001–009 evidence, October 9 review and
EWP are unchanged. No release, adoption, full-versus-reduced comparison,
publication rescore or automatic successor is authorized or started.
