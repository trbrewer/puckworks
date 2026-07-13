# DOI verification audit — Paper B flagged records

**Verification date:** 2026-07-13
**Scope:** resolve the two bibliographic flags listed in
`docs/PAPER_B_RELATED_WORK.md`. This is a publisher-record check, not the indexed
novelty search required by `SEARCH_PROTOCOL.md`.

## `lee2023`

**Verified citation**

> Lee, W. T., Smith, A., & Arshad, A. (2023). Uneven extraction in coffee
> brewing. *Physics of Fluids*, **35**(5), 054110.
> https://doi.org/10.1063/5.0138998

**Publisher evidence**

- AIP article record: <https://pubs.aip.org/aip/pof/article/35/5/054110/2889071/Uneven-extraction-in-coffee-brewing>
- The record gives the title, authors, journal, volume 35, issue 5, article
  054110, publication date 9 May 2023, and DOI `10.1063/5.0138998`.
- The arXiv record (`2206.12373`) links the same related journal DOI and records
  acceptance in *Physics of Fluids*.

**Disposition:** remove `UNVERIFIED`; add `lee2023` to `references.bib`.

## `waszkiewicz2026`

**Verified citation**

> Waszkiewicz, R., Myck, F., Białas, Ł., Puciata-Mroczynska, M., Dzikowski, M.,
> Szymczak, P., & Lisicki, M. (2026). Under pressure: Poroelastic regulation of
> flow in espresso brewing. *Physics of Fluids*, **38**, 063113.
> https://doi.org/10.1063/5.0319611

**Publisher evidence**

- AIP article record: <https://pubs.aip.org/aip/pof/article-abstract/38/6/063113/3396119/Under-pressure-Poroelastic-regulation-of-flow-in>
- The record gives *Physics of Fluids* 38, article 063113, DOI
  `10.1063/5.0319611`, and publication date 23 June 2026.
- The formal journal record supersedes the arXiv-only year/key previously used
  by the related-work scaffold.

**Disposition:** use key `waszkiewicz2026`; cite the formal journal article; retain
an arXiv link only as an access route when useful.

## Files reconciled

- `docs/literature_search/references.bib`
- `docs/PAPER_B_RELATED_WORK.md`

## Remaining literature gate

The DOI flags are closed. The Scopus/Web of Science execution, deduplication,
screening, snowballing, and final novelty calibration remain PI-owned and must be
archived before a categorical novelty statement is used.
