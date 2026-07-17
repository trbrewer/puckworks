# RESEARCH_RADAR.md — literature, venue, and collaboration discovery

The authority for the standing research-radar program (issue **#42**). It defines what the radar
discovers, from where, how often, and — most importantly — the discipline that keeps discovery
*discovery*: a candidate is never evidence, a card change, or a submission until a human says so.

**State clearly, up front:**

- **discovery metadata is not evidence;**
- **abstracts are not substitutes for papers;**
- **a search hit does not become a model component automatically;**
- **only official venue pages establish current calls and deadlines;**
- **deadline facts require a verification date;**
- **no contact is sent automatically;**
- **no submission is made automatically.**

---

## 1. Purpose

Continuously surface — and triage — technical literature, datasets, methods, software, research
groups, collaborators, conferences, workshops, journal special issues, software-paper venues, and
public-science opportunities relevant to Puckworks, so nothing important is missed and nothing
unvetted leaks into the science.

## 2. Scope

In scope (topic families): espresso/coffee extraction kinetics; porous & deformable porous media;
packed-bed flow & transport; granular compaction & rearrangement; wetting & infiltration;
swelling/fines migration/clogging/erosion; reactive transport & dissolution; permeability &
pore-scale simulation; lattice-Boltzmann; inverse problems & identifiability; system
identification & experiment design; pressure/flow/mass/temperature/concentration sensing; food &
beverage process engineering; digital twins & process control; scientific-software methods &
reproducibility; public communication of uncertain results.

Out of scope: anything the radar cannot tie to a query family with a stated relevance note. When a
new gap appears (a model, result, or product lane exposes one), a human adds a query family — the
radar never invents scope.

## 3. Search sources

**Official metadata APIs only** — never scraped search-result HTML.

- **arXiv API** (Atom) — preprints. Requests are paced at **≥ 3 s apart** with an identifying
  User-Agent and bounded retries (honoring `Retry-After` on HTTP 429).
- **Crossref REST** (`/works`) — published metadata + DOIs, via the **polite pool** (`mailto` +
  identifying User-Agent). Recency is filtered server-side with `from-index-date`.

> **Acknowledgment:** Thank you to arXiv for use of its open access interoperability. This does not
> imply arXiv endorses Puckworks. This acknowledgment also appears in the workflow artifact metadata
> and in each monthly radar issue footer.

A source is added only after: its official API docs are reviewed; rate limits and attribution are
understood; duplicate identity can be handled; and it adds real coverage. **Google Scholar
scraping is prohibited.** No article PDFs are downloaded; no paywall is bypassed; no copyrighted
full text is stored.

## 4. Query families

Queries live in [`docs/research/radar_queries.yml`](research/radar_queries.yml) — one **structured**
record per family: `id`, `title`, `enabled`, `lookback_days`, `maximum_candidates`,
`global_priority`, `concept_groups` (synonym groups — the scanner ANDs across groups and ORs within
a group), `exclusions`, `source_families`, `coupled_cards`, `last_human_review`, `owner`. The config
is strictly validated (unknown fields, empty terms, bool-as-int, impossible dates, and excessive
limits are rejected **before** any network request). Editing the vocabulary is a **human** action
(quarterly cadence); the scanner never edits this file. `public-communication-uncertainty` ships
disabled (noisy) and is enabled per-campaign.

## 5. Cadence

- **weekly** — automated metadata discovery (`research-radar.yml`);
- **monthly** — manual venue/deadline verification (`venue-deadline-review.yml` posts the
  reminder; a human does the verification against official pages);
- **quarterly** — review of query vocabulary and source coverage;
- **immediately** — a targeted scan when a model, result, paper, or product lane exposes a new
  evidence gap;
- **at release** — a check for relevant software-paper / demonstration venues.

## 6. Candidate record format

Each candidate (see `tools/research_radar.py`) may retain only: title; authors;
publication/preprint date; DOI; arXiv identifier; venue; source URL; a **short metadata-provided
abstract excerpt** (≤ 500 chars, within source terms); the query that found it; machine relevance
reasons (which terms matched — ordering only, never a decision); and a human triage state. It
retains **no full text and no PDF.**

## 7. Deduplication

Identity is resolved in order: **DOI → arXiv id → normalized canonical HTTPS URL → normalized-title
fallback** (lowercased, punctuation-stripped, whitespace-collapsed). Duplicates across sources (the
same DOI from arXiv and Crossref) **merge** into one record — keeping both identifiers, the more
complete author list, and the earliest preprint date plus the formal publication date separately.

**Cross-month deduplication is durable, not issue-local.** Each posted candidate carries a hashed
marker `<!-- radar-candidate:<sha256-of-normalized-identity> -->`. The weekly workflow reads the
markers from **all** radar issues (open and closed), and a candidate is posted only if its marker
is absent everywhere — so a paper seen last month is not re-posted this month. Ordering is
deterministic (match count, then date, then identity) so a re-run is reproducible.

> **The marker ledger is operational discovery-deduplication only — not the authoritative
> reviewed-paper ledger.** Editing or deleting an issue/comment can remove marker history, and the
> mechanism may be rebuilt or lost. A marker records that a candidate was *surfaced*, never that a
> paper was read, accepted, rejected, or linked to a model. Reviewed intake and model/registry
> dispositions live in the controlled, checked-in ledger tracked by issue #46 — not in these
> markers.

**Date quality.** A candidate's date is classified: `day`/`month`/`year`/`unknown` precision and
`verified_within_window` / `partial_date` / `future_date` / `out_of_window` / `invalid` quality. A
year- or month-only date does **not** satisfy a day-level recency window (it is retained as
`partial_date` for human review, not treated as recent); a full **future** date is `future_date`
(forthcoming), never "already published"; impossible dates and clearly out-of-window full dates are
dropped. Crossref `from-index-date` means recently *indexed*, not necessarily recently *published* —
both concepts are preserved. Because per-query `lookback_days` differ, the scan output reports
**per-query windows** (`query_runs`) plus a `heterogeneous_windows` flag rather than a single
misleading top-level window; result semantics are independent of query order. Broad free-text
queries carry a `required_any` domain-anchor list so a generic term (e.g. "model") cannot alone
qualify a Crossref hit.

## 8. Triage rubric

Every candidate is judged on **multiple axes** — never one opaque score: topical relevance;
methodological relevance; evidence quality; novelty vs current cards; availability of validation
data; data licensing/redistribution; reproducibility; impact on an existing claim; impact on a
current component; product/public-value potential; collaboration potential; venue/submission
potential; urgency.

Allowed triage states: `new` · `inspect` · `relevant` · `already-covered` · `out-of-scope` ·
`method-only` · `data-opportunity` · `collaboration-opportunity` · `venue-opportunity` ·
`rejected-with-reason`. A machine score is used only to order the worklist.

## 9. Model-card integration

A candidate may *suggest* a new or revised card. It becomes one only through the normal card-first
process (`docs/cards/TEMPLATE.md`, CLAUDE.md rules): a human writes/updates the card from the
paper itself — not the abstract — and implementation follows the card. The radar never edits a
card, and a hit never changes assumptions, a validity range, or an evidence-strength tag.

## 10. Manuscript integration

A candidate may be flagged as related work for Paper A/B/B2/3. Inclusion in a manuscript is a human
decision after reading the full paper and reconciling it with the literature search of record. The
radar never edits a manuscript.

## 11. Venue and deadline verification

[`docs/SUBMISSION_TARGETS.md`](SUBMISSION_TARGETS.md) remains the authoritative venue ledger.
Monthly, a human verifies **against the official organizer/journal page** at minimum: the call
page still exists; submission is genuinely open; deadline + timezone; event date/location;
presentation format; abstract length; registration requirement; membership requirement;
prior-publication restrictions; proceedings/publication consequences; cost/logistics; fit with
current evidence; and the internal preparation deadline.

Recurring venue coverage spans: Paper A; Paper B/B2; the Puckworks methods/resource paper (Paper
3); scientific-software venues; visualization/public-science venues; coffee-industry venues; food
engineering; fluid dynamics; porous media; analytical instrumentation; and open-science/software
conferences.

The [`venue-deadline-review`](../.github/workflows/venue-deadline-review.yml) workflow posts a
**monthly human venue/deadline review reminder** (a checklist + the ledger's recorded verification
date). It does **not** parse deadlines, validate official pages, compute submission urgency, or
detect newly opened calls — it reminds a human to do those checks against the official page. While
reviewing, the human flags a venue when the ledger verification date is stale, a deadline is within
~90 days, a *forthcoming* call is now due for a check, or a methods/resource-paper venue remains
unscouted. A passed deadline is marked **PASSED**, never deleted. **No deadline is ever rewritten
from a scraper** — official pages are the only authority. (If automated stale/90-day detection is
wanted later, it requires a separate machine-readable venue config with strict verified dates and
its own tests — not page scraping.)

## 12. Collaboration / contact rules

A radar result may identify a possible collaborator or organizer. It is **never contacted
automatically.** Before any contact a human must: verify identity; verify relevance; state a
concrete purpose; identify the sender; obtain explicit maintainer authorization; and avoid mass
outreach. Private email addresses are never published in repository issues; public contacts are
recorded only when appropriate.

## 13. Copyright and full-text policy

Metadata only. No PDF downloads; no paywall circumvention; no storage of copyrighted full text.
Abstract excerpts are short, source-provided metadata kept within the source's terms. Attribution
and rate limits are honored per each API's policy.

## 14. Audit log

Each automated scan attaches its full machine-readable output (`candidates.json`) as a **workflow
artifact** and appends only *new*, sanitized candidates to the current monthly radar issue — it
never commits generated candidates to the repository and never edits a scientific file. The monthly
issue plus the workflow run history form the audit trail; triage decisions are recorded by humans on
the issue.

**Unattended writes are DISABLED BY DEFAULT.** Merging the radar workflows does **not** by itself
enable scheduled issue writes. A scheduled run scans and uploads an artifact, but it only
creates/comments on an issue when the corresponding repository variable is set to `true` — a
human's recorded opt-in, with **separate** switches per capability:

- **weekly radar publishing** → `ENABLE_RESEARCH_RADAR_PUBLISH`;
- **monthly venue reminder** → `ENABLE_VENUE_REMINDERS`.

A manual `workflow_dispatch` (radar: `publish_issue=true`) is an explicit human action and always
writes, from `main` only. **Unattended publishing requires a SUCCESSFUL scan** — a partial or
failed scan never publishes on the schedule (so an incomplete radar result is never presented as
complete). Publishing a partial scan is possible only via manual dispatch. To enable unattended
writes, a maintainer sets the relevant variable and records that decision on issue #42.

**Labels + safety:** monthly radar issues are labelled `research-radar` + `triage` — **never
`standing`** (reserved for the permanent tracker #42), and may be closed after human triage. A
**failed** total scan writes no issue. A **closed** current-month issue is never silently
duplicated — it is flagged for human action. **Manual dispatch defaults to scan + artifact only**
(no issue write); writing requires `publish_issue=true`. Untrusted metadata (titles, authors,
venues, URLs) is sanitized before rendering — control/bidi characters and HTML stripped, `@`
mentions and `#` refs neutralized, non-HTTPS URLs dropped, lengths and issue-body size bounded — and
the substantial issue logic lives in `tools/research_radar_issue.py` (offline-tested), not in the
workflow YAML. Global caps bound candidates per query, per source, and per scan; omitted counts are
reported, never silently dropped.

## 15. Standing review process

This is a **standing** program (issue #42) — never closed after the first workflow ships.
Quarterly, a human reviews query vocabulary and source coverage and records, on the issue: date,
reviewer, checks performed, changes made (or a no-change rationale), and the next trigger. A
scheduled scan or reminder is **not** evidence a review happened.

### Standing cadences (all programs)

| Program | Cadence |
|---|---|
| Literature metadata (#42) | weekly (automated discovery) |
| Venue / deadline verification (#42) | monthly, and immediately before any submission |
| Search-query review (#42) | quarterly |
| Public homepage (#41) | monthly + every release + every public-API change |
| Accessibility (#43) | quarterly + every release + every platform/dependency change |
