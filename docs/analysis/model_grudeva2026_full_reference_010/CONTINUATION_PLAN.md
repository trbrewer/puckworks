# 010 archive continuation (prospective)

Owner-authorized continuation in draft PR #333, same G2 task and frozen synthetic
case. PHYSICAL_VALIDATION=NOT_ESTABLISHED. Original MATRIX.json and the original
failure/results/review bundle remain byte-identical. This is no numerical-method,
physics, parameter, support, threshold, default, dependency or environment change.

The old writer made identities after NPZ serialization. Capture owned copies, but
there was no source commitment before copying, derived-array construction or
writing. A post-write digest cannot localize a discrepancy among those stages.
The new chain commits the solver arrays before copying, verifies owned C-order
read-only snapshots and unchanged sources, commits all archive arrays before
writing, checks sources again after writing, independently streams NPY payloads,
and reloads safe numeric arrays. A final manifest is published only after all
stages and layout/redundancy checks pass. Interrupted files remain incomplete.

Schema v2 uses one numeric NPY per array, retaining every v1 state, coordinate,
coefficient and metadata field plus separate boundary-accumulator copies. This
allows read-only memory mapping, eliminates whole-array hash byte allocations and
avoids retaining multiple decoded dense-coefficient copies. Canonical identities
are exact C-order numeric bytes, with dtype and shape declared independently.
Inputs may be contiguous, transposed or strided; snapshots are owned C-order data.
The original v1 reader stays strict. Interpolant evaluation retains its original
scale-aware numerical allowance; saved-state equality has no tolerance.

Historical diagnosis reuses the three completed diagnostics. One justified read
of y and concentrations records all 19 differences (only ten were previously
retained). All changed bytes have C-order payload offset 43 modulo 64, but not all
19 XORs contain only one bit. Payload offsets are not process-memory addresses.
A small first dense endpoint sample differs in 2,099 entries (maximum 2.22e-16),
including one accumulator. SciPy stores y_new separately from updated backward
differences, so dense endpoints are not assumed exact backups. No independent
accepted-state checkpoint was retained. No bit search or digest substitution.
HISTORICAL_ROOT_CAUSE_UNESTABLISHED; original anchor is ineligible for exact reuse.
Accessible kernel records show no contemporaneous memory/storage error. The boot
log's Oct 6 journal "corrupted or uncleanly shut down" rename is retained; it does
not identify an ongoing memory/storage mechanism. EDAC counters are not exposed.
These access-limited observations do not certify the hardware.

Before a full run: negative integrity tests, original mathematical controls, and
one paired fixed-settings non-campaign integration/capture fixture must pass.
The solver-free large test is fixed here: one float64 array of shape
(24834,18003), plus its transpose and a small strided view for canonical-hash
checks. A deterministic integer-index-derived finite payload includes signed
zeros and marked values at the complete historical witness offsets and around
2 GiB and 4 GiB stream boundaries. Because the original y payload is 3.5767 GB,
a separate one-dimensional uint8 payload of 2**32+257 bytes exercises the 4 GiB
boundary. Execute one write/commit/raw-stream/reload cycle per payload, retaining
logs, prospective identities, source/payload checks and resource measurements.
This is serialization diagnosis, not a new physical case or storage benchmark.
Do not proceed if unexplained mutation recurs.

Original observed archive: 27,685,312,970 bytes; sampled RSS: 91,653,436 KiB.
Initial accessible resources: approximately 259.7 GB available memory, 1.340 TB
free disk; no resource limits changed. Plan for approximately 42 GB arrays/row (from retained NPY member sizes),
original dense solver storage plus owned capture plus mapped files/cache and
scratch: conservatively 160 GiB live-memory headroom and 60 GiB free disk per
largest row; retain up to 840 GiB for the whole remaining campaign.
These are admission estimates, not run quotas. Recheck actual host/cgroup limits
and monitor RSS, available memory and disk. Release avoidable duplicate captures
before observation/audit; do not discard required scientific evidence.

After controls and a scoped independent delta review, a continuation binding
will authorize only listed changed implementation hashes against the immutable
original matrix. One replacement anchor, then all thirteen outstanding rows in
original row_order, serially. The repeat is a separate execution. No automatic
second replacement after unexplained integrity failure. Numerical gate failures
retain all computable integrity-qualified observations and do not prevent other
independent frozen rows. No freeze over the old matrix and no ignore-hashes flag.
