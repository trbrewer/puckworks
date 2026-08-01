# Paper 1 — what actually remains before submission

**Status as of 31 July 2026:** no science blocker, no wording blocker, no assurance blocker.
Everything below is metadata, an external action, or a release-time mechanical step.

Authoritative check:

```bash
python tools/paper_a_front_matter.py --check-submission-ready
python tools/paper_a_consistency.py submission
```

Both enumerate the same list. Read them rather than this document if the two disagree.

---

## 1. Author actions — only you can do these

| Field | What is needed |
|---|---|
| `authors` | Names in submission order |
| `affiliations` | Institutional affiliations |
| `corresponding_author` | Name + institutional email |
| `orcids` | ORCID per author |
| `credit_roles` | CRediT roles, author by author. Do not retain roles that were not performed |
| `funding` | Funder and grant number, or the standard no-specific-grant text |
| `competing_interests` | Declaration, or the standard none-declared text |
| `generative_ai_declaration` | Must match JFE's current Editorial Manager wording **and** the actual use of tools |

All eight live in `docs/submission/paper_a_front_matter.yaml`. Fill them there and run
`python tools/paper_a_front_matter.py --write` — the manuscript, package, cover letter and
Highlights all regenerate from that one file.

Two cover-letter sentences are **deliberately withheld** until the corresponding fields exist:
"all authors have approved the submission" and the competing-interests declaration. Neither can be
asserted on the authors' behalf, so the generator refuses to write them.

## 2. External actions

| Item | Why it is not a repository action |
|---|---|
| `novelty_search` | Requires licensed Scopus / Web of Science access. Replace the provisional novelty wording with the archived search result |
| **Angeloni replicate drop** | *Optional.* Tables 4–5 publish only global RSD ranges, so a solute-specific weighted refit is blocked. The analysis is scoped as a descriptive sensitivity study and says so — this is **not** a submission blocker, only a strengthening opportunity |

## 3. Release-time mechanical steps

These are done at release, in this order, and are repository actions:

1. Freeze the release archive; mint the DOI → `release_doi`.
2. Record the release commit → `release_commit`.
3. Regenerate the reproducibility manifest against a **clean** tree (currently `git_dirty=true`,
   `bundle_matches_head=false`, `release_fresh=false` — all expected during development).
4. Re-run the full chain and `python tools/paper_a_consistency.py submission`; it should come back
   clean once 1–3 and §1 are done.
5. Convert the manuscript to `.docx` or `elsarticle` `.tex`, applying the conversion edits in
   `PAPER_A_JFE_PACKAGE.md`. Note that the Highlights file and the standalone caption file upload
   **verbatim** — they are already free of repository paths and process language, and the scanner
   enforces that.

## 4. Recommended but not blocking

- **Domain referee read** — `PAPER_1_DOMAIN_REFEREE_BRIEF.md`. The one substantive gap remaining is
  that nobody has judged the paper *as a paper*: comparator fairness, corpus choice, whether the
  conclusion follows. Twelve rounds examined the wording and the gates; none examined the science.
- **Supplementary Table S7 at journal width** — 44 rows, never proofed in a typeset rendering.

## 5. What is explicitly finished

Do not reopen these without new evidence:

- **Claim wording.** The acceptance criterion is now falsifiable: every one of nine load-bearing
  surfaces must state symmetric non-establishment — the analysis establishes neither that the
  advantage is reproducible/useful nor that it is absent. Enforced by
  `claim_policy.SURFACE_ASSERTIONS`; a wording dispute that does not violate it is editorial
  preference, not a finding.
- **The assurance layer.** Frozen — see `CLAUDE.md`. It is not to be hardened further while the
  procedure registry is empty.
- **Source transcription.** 726 analyte cells and 66 condition rows verified against the article
  PDF, digest pinned, zero mismatches, reproducible via `tools/audit_angeloni_bioactives.py`.
- **The numbers.** Protected values pinned exactly, no tolerance, with mutation tests proving the
  ratchet bites. Three consecutive review rounds found the stale-number category empty.
