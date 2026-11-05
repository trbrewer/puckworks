# PW-VIS-METADATA-PROBE-001

**The API supplies additional profile configuration, but this probe establishes
no fully qualified format/machine cohort and does not justify a larger harvest
for #419's turnover question.**

**599 shots; 1,029 requests; 1,029 HTTP 200 responses.** A contains 300 frozen
snapshot shots; B contains 299 unique recent-listing shots (one repeated entry
among three 100-item pages, no replacement). There were **427 JSON profile
responses**, no access refusals, no unavailable shots and no rate-limit responses.
Requests ran on **2026-11-05, 15:24:26–16:21:39 UTC** at at most 18/minute and
180/10 minutes, below the documented 50/200 limits.

| Sample and returned format authority | Accessible shots | Machine identity in captured paths | Established full #419 qualifications |
|---|---:|---|---:|
| A: software-written Beanconqueror parser | 150 | UNKNOWN | 0 / 150 |
| A: unresolved upload format | 150 | UNKNOWN | 0 / 150 |
| B: software-written Beanconqueror parser | 22 | UNKNOWN | 0 / 22 |
| B: unresolved upload format | 277 | UNKNOWN | 0 / 277 |

No inspected machine/device path supplied a label. Parser identity identifies
software, not hardware. JSON profiles can expose steps, pump settings and limiter
containers; they do not establish actual active-extraction timing, an inactive
flow limiter or measured scale lineage. For chart-based uploads, the default
serializer returns common arrays instead of native parser data. The GaggiMate
parser can fill common weight/flow channels from measured **or estimated**
inputs, so those channel names are insufficient. No machine type is qualified.

For A, **all 300 top-level `profile_title` fields were historically present and
deliberately privacy-stripped**, as confirmed by saved `profile_present` flags.
This does not mean title information was removed from every native path. The **150
Beanconqueror parser labels were preserved in Bronze**, but not promoted to the
normalized integration label. Profile-endpoint structure is supplemental data
the old harvester never requested. Other current-versus-stored differences
remain source-change/loss UNKNOWN; they are not automatically harvester defects.

Review found a collector defect: numeric types lost the `-1`/zero/positive
distinction and omitted some limiter/exit/legacy subfields. The table marks these
**NOT_CAPTURED**, never absent at source. No extra requests repaired that loss.
Actual full qualification remains **UNKNOWN**: matching, stage assignment,
limiter activity and flow/weight consistency were not evaluated. The zeros above
count established qualifications, not proof that the physical shots cannot
qualify. Public field counts use linked small-cell suppression; no identifiers,
free text, raw arrays or values are released.

Credit: **Visualizer**, with collective thanks to contributing users. EWP,
the existing snapshot, defaults and historical results are unchanged. The
[source interpretation](SOURCE_INTERPRETATION.md) and [reproduction record](REPRODUCE.md)
preserve the partial gain and limits. “Missing fields” below means the remaining
record-supported machine and measured-flow provenance; it excludes profile
configuration already recovered and settings this collector failed to capture.
Within the inspected paths of these sampled default responses, **the API does
not supply the missing fields**.
