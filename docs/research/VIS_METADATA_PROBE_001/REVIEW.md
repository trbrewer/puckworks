# Independent read-only review — 2026-11-05

A fresh reviewer session separate from implementation inspected the frozen
design, source interpretation, collector, final public bundle and private
field-type/request evidence. It made no API requests or file edits. Final
disposition: **no remaining release-blocking defect**, with the capture limits
below explicitly retained.

The reviewer independently verified 1,029 = 3 + 599 + 427 requests, sample and
freeze ordering, all seven declared artifact hashes, the 13 source-file SHA-256
and Git-blob identities, 18/60-second and 180/600-second request maxima and minimum
spacing. Timers sum to 64.24 CPU seconds (0.017844 core-hours). Fourteen new
synthetic tests passed. On the actual final release it checked 402 numeric
membership/count/minimum conditions and 34 published nested links with no
disclosure violations; the full format partition qualifies. No private shot/
user tokens or UUIDs were found in the public bundle.

Findings and disposition:

1. **Capture loss, retained as a limitation.** Type-only extraction collapses
   negative-one/zero/positive settings and omits documented limiter/exit/legacy
   paths. Those distinctions cannot be recovered from retained evidence. The
   report now labels them NOT_CAPTURED/UNKNOWN, not absent at source. The original
   plan's stronger capture requirement was not achieved. No requery, changed
   sample or additional API request was made to repair it. Profile/control
   completeness cannot be claimed.
2. **Linked disclosure defect, corrected.** Independent cell checks allowed a
   parent count of 80 and child count of 79 to disclose a one-shot difference.
   Actual candidate profile tables also contained small nested differences.
   Within-row difference checks, connected-path suppression and linked profile
   suppression now protect the final table; regression tests cover this defect.
3. **Historical comparison clarified.** The report now includes non-null coverage
   for named normalized mappings. The summary distinguishes privacy-stripping
   of the top-level `profile_title` field from information retained in native
   paths such as `brewdata.preparation.name`; nested parser labels were preserved
   in Bronze even when omitted from normalized integration labels.
4. **Claim scope narrowed.** Absence is scoped to inspected paths of sampled
   responses, not all API routes or arbitrary metadata. The conclusion preserves
   the profile-configuration gain and distinguishes zero established full
   qualifications from actual qualification UNKNOWN. No hardware identity or
   measured flow is inferred from parser names or common channel names.
5. **Hosted CI compatibility, corrected after the first run.** The existing
   name-only I-040 reachability audit linked the new generic `get` method to
   unrelated scientific helpers and attempted to execute a non-gate
   `gate_state` helper. The implementation is now named `_bounded_metadata_get`
   with `get` retained as the Session-interface alias. The reviewer independently
   confirmed identical method ASTs apart from the name and identity of the alias;
   request, sample, extraction and privacy behavior are unchanged. There is no
   review blocker. The 96 focused follow-up tests, including I-040, Ruff and
   README governance passed. REPRODUCE preserves both code hashes and the failed
   hosted job; no live request or aggregate export was repeated.

Required hosted CI is tracked on the draft PR at its final head. Review and CI
do not establish physical validation or source-owner endorsement.
