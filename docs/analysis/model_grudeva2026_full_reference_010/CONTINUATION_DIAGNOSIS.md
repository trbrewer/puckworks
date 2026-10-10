# Historical archive diagnosis and recovery eligibility

**HISTORICAL_ROOT_CAUSE_UNESTABLISHED. Exact recovery is not eligible.**
The original failed attempt remains unchanged and incomplete. The continuation
uses a separately identified replacement; it does not repair the old artifact.
The complete new witnesses are in [CONTINUATION_DIAGNOSIS.json](CONTINUATION_DIAGNOSIS.json).

The original frozen code establishes this order:

1. SciPy retains accepted times/states and separate BDF dense interpolants.
2. `capture` allocates dense arrays, copies each interpolant, then copies `t` and
   `y` with `copy()`. These are owned copies, but no prospective identities or
   post-copy source checks existed.
3. `save_archive` builds a dictionary referencing those captured arrays. It
   computes a separate concentration array from `y[:-2].T / min(t,1)` and separate
   physical coordinates before serialization. The transpose is a temporary view;
   the division produces the redundant concentration values. No redundant
   relationship check was made at this boundary.
4. `np.savez_compressed` writes the arrays in insertion order: accepted times,
   amount states, dense coefficients, shifts, denominators, orders, concentrations
   and physical coordinates. Then the writer hashes the whole NPZ file, followed
   by the in-memory arrays. The old array hash calls `ascontiguousarray` and
   `tobytes`, allocating a full canonical byte copy. A contiguity conversion may
   alias an already contiguous source; it is not an ownership guarantee.
5. The manifest is published after those post-write hashes. The loader checks
   each file hash and decoded array identity before any midpoint fidelity test,
   observation or numerical audit. It rejects post-wetting `y`. The subsequent
   observation code was therefore never reached in the original execution.

This order leaves capture, derived-array construction, serialization and hashing
without separate source commitments. It does **not** identify a mutation or
hardware mechanism. Matching retained whole-file hashes support unchanged files
since those commitments; independently streamed raw `y` bytes agreeing with the
decoded `y` hash rule out attributing this mismatch solely to NPZ decoding.
The already established three file hashes, 25/26 array identities, finiteness
checks and failed concentration substitution were reused, not rerun as new work.

The one new full comparison reads the two relevant arrays to recover all 19
witnesses; the earlier record retained only ten. Those ten have one XOR bit at
positions 24, 25, 29 or 31. Across all 19, some XORs have multiple bits and the
union is 24, 25, 26, 28, 29, 30 and 31. Every changed byte is at offset 43 modulo
64 in the declared C-order `y` payload, using
`8 * (state_index * 18003 + time_index)` plus the changed byte within the float.
These are serialized payload offsets, **not process-memory addresses**.
No bit-substitution search or checksum replacement was performed.

The concentration copy omits both boundary accumulators. Their retained exact
raw identity is recorded separately; no independent accumulator checkpoint was
found in the inspected execution records. A small first dense-endpoint sample
has 2,099 differences from the accepted state, including a one-bit accumulator
difference; the largest absolute difference is 2.220446049250313e-16. The inspected
SciPy BDF source sets `self.y = y_new` separately from backward-difference updates.
Consequently dense coefficients are not an exact accepted-state backup. This
observation neither invalidates the interpolant's numerical allowance nor
establishes the original accepted-state byte identity.

No independent accepted-state copy or checkpoint was found in the retained
execution root; core dumps were disabled. This is a scoped search result, not a
claim that no copy could exist elsewhere. Accessible kernel records expose no
contemporaneous memory/storage error. A boot log retains an October 6 journal
"corrupted or uncleanly shut down" rename, without evidence identifying an ongoing
mechanism in this execution. EDAC controller counters were not exposed. No
administrative changes, hardware diagnosis campaign or environment change was
made. These limited records do not certify system integrity.

New source/snapshot commitments, strict payload checks and negative controls
qualify the replacement capture path prospectively. A passing replacement cannot
retroactively establish the historical cause. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
