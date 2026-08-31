# Reviewed local-corpus coverage

The controlling independent review identifies 39 material local source
families. All 39 now resolve to canonical `MANIFEST.csv` dataset IDs and the
generated available-data register; none remains an unregistered local family.

`puckworks/data/LOCAL_CORPUS_FAMILY_INDEX.json` is the deterministic machine
authority. Regenerate it only by running, in order:

```text
python tools/build_available_data_register.py
python tools/build_local_corpus_family_index.py
python tools/validate_local_corpus_coverage.py
```

The index contains metadata and compact reviewed counts only. It contains no
absolute local paths or raw corpus payload. Telis-Romero 2001 is independently
registered as a rights-bounded rheology authority and remains linked to the
existing G10 component. Visualizer raw records remain external, private-record
use and raw redistribution remain unauthorized, and current hydraulic evidence
is descriptive rather than predictively qualified.
