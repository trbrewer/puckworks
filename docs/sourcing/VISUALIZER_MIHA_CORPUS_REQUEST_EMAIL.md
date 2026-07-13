# visualizer.coffee corpus-use request email (Miha Rekar)

**To (VERIFY before sending):** Miha Rekar — maintainer of visualizer.coffee.
Suggested address `miha@visualizer.coffee`; confirm the current contact (or use
the site's contact form / a GitHub issue on the visualizer repo) before sending.

**Subject:** Sanctioned research use of the visualizer.coffee public shot data — an
open espresso-model registry

Dear Miha,

Thank you for building and running visualizer.coffee — it is a remarkable public
record of how espresso is actually pulled across a huge range of machines.

I contribute to **puckworks**, an open, non-commercial registry of espresso
process models in which every published model is reproduced as a
provenance-tracked, independently-validated component. Most of our datasets are
controlled single-rig experiments; what those lack, and what visualizer.coffee
uniquely provides, is an *ecological* population — the real spread of achieved
pressure / flow / weight trajectories across many machines and users. We would
like your blessing to use that population responsibly, and to check that the way
we already handle it matches your intent.

**What we would use it for.** Strictly as a reference-strength *population* of
machine-logged hydraulics: a cross-machine pump/flow envelope to sanity-check our
flow and bed-dynamics models against reality at scale, and to characterise the
distribution of real shot behaviour. We do **not** treat any of it as controlled
ground truth.

**How we handle privacy and provenance today** (via the public read API only, at
≤30 requests/min):
- We drop, at ingest and before anything is stored, all identifying and free-text
  fields — user name, user id, avatar, barista, and every notes field. The only
  user linkage we keep is a **salted one-way hash** of the user id, purely so we
  can account for how concentrated the data is among a few contributors
  (selection bias); the raw id is never stored.
- We keep the machine-logged **hydraulic** telemetry and any user-entered
  **TDS / EY / sensory** values as *separate* tiers, and we explicitly label the
  user-entered outcomes as **not** calibrated ground truth — never as a
  benchmark for anyone's shot.
- We do **not** redistribute the corpus. It stays local for internal calibration;
  only small aggregate statistics (counts, coverage histograms) and our code are
  public.

**What we're asking:**
1. Your view on whether this public-API, privacy-reduced, non-redistributed use is
   acceptable to you and to the community whose shots these are — and any
   conditions you'd want us to honor (attribution wording, rate limits, fields to
   avoid, an opt-out mechanism).
2. Whether a **sanctioned bulk export or a documented research endpoint** would be
   preferable to us politely paging the public API — both for your server load and
   so we're working from a form you're comfortable with.
3. How you would like visualizer.coffee (and you) credited in any resulting
   analysis or publication.

We're glad to share back whatever we build on top of it — the aggregate
population views, the code, and our comparisons — and to adjust or stop entirely
if any of this doesn't sit right with you or your users.

With appreciation for the resource,

[Name]
[puckworks repository URL]

---

*Status: **SENT 2026-07-13 by Tim** — awaiting reply. See ROADMAP §5.8 (Miha Rekar row) and the
`visualizer_coffee` data-only card. The public-API harvester
(`puckworks/lib/visualizer_harvest.py`) is already the default fallback and works
without this reply; the corpus is gitignored and not redistributed. This request
gates **redistribution / publication** use of the corpus, not day-to-day internal
calibration. When a reply lands: record conditions in the card + §5.8, and — if a
sanctioned export is offered — prefer it over API paging.*
