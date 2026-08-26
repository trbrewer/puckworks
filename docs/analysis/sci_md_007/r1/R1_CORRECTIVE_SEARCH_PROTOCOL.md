# SCI-MD-007-R1 corrective search protocol

This prospective corrective search begins after independent review. The original search log
was not present in frozen contract commit `241eca9`; therefore its claimed completion is not
treated as a frozen search execution. Numerical feasibility thresholds remain exactly those in
that commit. This R1 protocol closes search serialization only and is classified
`R1_CORRECTIVE_CONTRACT_CLOSURE`.

For each of the eight exact queries in the accompanying JSON contract, screen the first 20
results from Crossref and OpenAlex, plus the first 20 results from a general public web search.
If a provider returns fewer than 20, record the returned count. Deduplicate by normalized DOI,
then PMID or stable identifier, then normalized title/year/first author. Each result receives a
numeric rank and a terminal screening state.

Every atlas-included primary publication receives one backward and one forward pass, each
bounded to the first 20 discoverable records. Record individual results, including zero-result
passes. The completion reducer fails closed for a missing provider/query execution, nonnumeric
counts, unterminated candidates, unresolved duplicates, or absent citation passes.

Only public metadata, open primary articles, supplements, and rights-permitted normalized facts
may be used. Paywalls and authentication controls may not be bypassed. Angeloni metadata may
appear only in an explicit exclusion/audit record; no Angeloni numerical row or protected
artifact may be read or copied.

Atlas inclusion and primary-label eligibility are separate. A row is primary eligible only when
it is caffeine or trigonelline measured directly in roasted, unextracted material as total
content, traceable to source/material/roast/method/lineage, rights-usable, nonduplicate, and on
the explicit dry roasted basis through an exact or source-supported same-batch-moisture
conversion.
