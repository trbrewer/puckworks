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

- **arXiv API** (Atom) — preprints.
- **Crossref REST** (`/works`) — published metadata + DOIs. A `mailto` is sent for the polite pool.

A source is added only after: its official API docs are reviewed; rate limits and attribution are
understood; duplicate identity can be handled; and it adds real coverage. **Google Scholar
scraping is prohibited.** No article PDFs are downloaded; no paywall is bypassed; no copyrighted
full text is stored. Source rate limits are respected and an identifying User-Agent/contact string
is sent.

## 4. Query families

Queries live in [`docs/research/radar_queries.yml`](research/radar_queries.yml) — one record per
family, each with `id`, `title`, `enabled`, `source_families`, `terms`, `exclusions`,
`relevance_notes`, `coupled_cards`, `last_human_review`, `owner`, `max_candidates`. Editing the
vocabulary is a **human** action (quarterly cadence); the scanner never edits this file. Families
cover the §2 scope; `public-communication-uncertainty` ships disabled (noisy) and is enabled
per-campaign.

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

Identity is resolved in order: **DOI → arXiv id → normalized-title fallback** (lowercased,
punctuation-stripped, whitespace-collapsed). Duplicates across sources (the same DOI from arXiv
and Crossref) collapse to one record; candidates already recorded in a prior radar are excluded.
Ordering is deterministic (match count, then date, then identity) so a re-run is reproducible.

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

The monthly workflow raises a **human-review reminder** when: the ledger's verification date
exceeds its freshness threshold; a deadline is within 90 days; a call previously marked
*forthcoming* is now due for a check; or a methods/resource-paper venue remains unscouted. A
passed deadline is marked **PASSED**, never deleted. **No deadline is ever rewritten from a
scraper** — official pages are the only authority.

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
artifact** and appends only *new* candidates to the current monthly radar issue — it never commits
generated candidates to the repository and never edits a scientific file. The monthly issue plus
the workflow run history form the audit trail; triage decisions are recorded by humans on the
issue.

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
