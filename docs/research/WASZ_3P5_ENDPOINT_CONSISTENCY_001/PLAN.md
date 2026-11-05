# PW-WASZ-3P5-ENDPOINT-CONSISTENCY-001

Pre-analysis specification; owner-authorized descriptive record/processing audit.
G0 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / TARGET_EXPOSED.
Actual fetched PW base: `4c5ebab5df79929813949df7113c21290dde40cc`.
PR #417 is unmerged at intake; its records are read only at
`0e1944de72819f0a058b99b6c0b2879e2d4ffde6`. EWP remains read-only.

Question: do recorded pressure, timing, mass or processing features help account
for the recurring nominal-3.5-bar endpoint discrepancy, or do the records appear
internally consistent under the inherited definitions? A discrepancy does not
establish defective observations or a linear physical response. No identifiable
inconsistency is a complete answer.

## Fixed inputs and windows

Use the authenticated Zenodo 18046315 v1.0.1 CC-BY-4.0 data, the same 56 distinct
brews/eleven nominal conditions, `WASZ_TRACE_ALIASES` exclusion, stored
`equilibrium_windows.csv` endpoint_100s targets and `traces_per_brew` pressure
histories. Reuse PW loaders and B0 observation helpers; never call model fitting,
prediction or scoring. Reconcile SCI-MD-010, FORM_A, JOINT_CLOCK_001 and pinned
LC_JOINT_TRANSFER_001 observations. The documented 1.5-to-2-bar label mapping and
1-2 correction are known provenance. Raw source programs are GPLv3 and are not
copied or imported. No new campaign or independent evidence is claimed.

1. **Raw integrity first:** parse every original JSON-line in recorded order,
   before any filtering, alignment, interpolation or cleaning. Count blank or
   malformed lines, missing/null/nonfinite fields (including t, p2, m), repeated
   timestamps and adjacent non-increasing timestamps. Sampling intervals use
   only originally adjacent records with finite timestamps: no bridging missing
   rows, sorting or deduplication. Report min/median/mean/SD/max and 5th/95th
   percentiles, plus the five largest positive gaps with record indices. Report
   the literal first/last raw timestamp separately from retained and clean ends.
   Missing/corrupt evidence is unavailable, never repaired silently.
2. **Endpoint pairing:** use the existing endpoint_100s flow unchanged, paired
   with line pressure at t=100 s on its inherited 0–100-s/1,000-point grid
   (stable-pressure zero; final grid point). Do not replace it with a raw-sample,
   clean-course or late-window flow. Report exact differences from SCI-MD-010's
   existing per-brew flow/pressure pairs for all 56 brews. A synthetic trace
   checks time-matched pressure interpolation and rejects unsupported endpoints.
3. **Adjacent descriptive steps:** calculate (mean endpoint flow change)/(mean
   pressure change) for 2→3.5 and 3.5→4, using nominal pressure and then matched
   endpoint pressure. Equal-brew condition means; no fitted curve, new score,
   physical-model claim or imposed linearity. Zero denominators stay undefined.
4. **Supporting summaries:** report every brew at 1/2/3.5/4/5 bar and equal-brew
   condition means, with each column's support kept explicit:
   - Primary reporting pressure: interpolate the retained pressure history onto
     FORM_A's 0.1-s reporting grid and use its exact saved trace_mask (observed
     onset +2 s through min(100 s, clean end)); sample mean and population SD.
     This is neither the longer 0.5-s fitting mask nor the late-trend support.
   - Stable-pressure time: B0.raw_trace's exact alignment, after the last sample
     outside median pressure ±min(10%,0.5 bar) among the first 501 retained
     complete records. Report elapsed time from first raw timestamp and from
     first retained timestamp. No dates, sessions or brew order are inferred.
   - Pressure excursions: separately first retained sample→stable zero and
     stable zero→clean end; report extrema, maximum excess above the inherited
     upper band, time below/above that band and longest contiguous below-band
     duration. Durations use left-held recorded intervals on each support.
     Below-band intervals describe pressure only, not an identified pump pause.
     Report explicit pause metadata if present; do not infer unrecorded events.
   - Final-clean-30-s flow trend: the slope returned unchanged by
     B0.clean_course on native timestamps t≥clean_end−30 s. Its terminal rule
     uses the first post-100-s pressure departure >max(0.5 bar,10% of median
     90–100-s pressure) or mass loss >5 g, retaining the preceding sample.
     Differentiation and the original 31-sample/order-one filter occur only
     after this cleaning. No alternative trend window or flow derivation.
   - Observed onset: unchanged B0 sustained detector, strict baseline-relative
     mass >0.5 g and flow >0.1 g/s for two seconds; return interval start.
     Baseline is median original retained mass on aligned [−2,0] s, with the
     inherited first-sample fallback. Report native clean-end time separately.
   - Beverage mass: linearly interpolate original retained mass at aligned
     100 s and at clean end, then subtract that same baseline; no extrapolation
     and no substitution of the final raw scale reading.

Only continuous descriptive values and required integrity/support counts are
reported; no anomaly labels, new thresholds, exclusion, down-weighting or
relabeling. The models already use measured pressure histories: achieved-pressure
plotting alone cannot explain their error as failure to use measured pressure.

## Delivery and checks

Commit this plan before inspecting new audit results. Produce four requested
CSVs, a half-page numbers-first SUMMARY, one all-56-brew endpoint scatter figure
with 3.5 bar highlighted and no model curve, and REPRODUCE with commands, input
hashes and measured process CPU core-hours (including unsuccessful attempts).
Add author questions only for specific unresolved recorded features, retaining
the existing brew-order/pressure-setting questions. Add exactly the requested
frozen-f=0 diagnostic sentence to JOINT_CLOCK_001/SUMMARY.md; change no old number.

Focused checks authenticate inputs/cohort/alias/endpoint identity, verify the
audit sees unfiltered unsorted records, and test endpoint pairing on a synthetic
trace. Reuse unchanged baseline evidence by exact base identity; run focused
checks, registry/static checks and required PR CI. Preserve failed attempts
outside Git. No model fits/refits/scores, new RMSE/grades, physical validation,
EWP/default changes, merge or successor. Finish with one open draft PR and
auto-merge disabled.
