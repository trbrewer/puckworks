# Available data register

`puckworks/data/MANIFEST.csv` remains the canonical row-level provenance authority. `puckworks/data/AVAILABLE_DATA_REGISTER.json` is deterministically generated from every MANIFEST row and adds a compact decision-use layer: scientific family, resolution, directness, independence, rights, raw-access state, eligible uses, blocked claims, and missing joins.

| Family | Raw access | What it can test | What it cannot establish |
|---|---|---|---|
| Pannusch 2024 | external recovered local corpus; DOI `10.17632/y2tz67f6ry.1` | source reconstruction, physical-replicate variability, species/fraction progression, campaign-separated target-exposed normalized transfer subject to SCI-MD-008 | production M0, closure, hydraulics, local method qualification, target blindness, or independent validation |
| Other registered families | see generated JSON | uses recorded in MANIFEST and family metadata | claims beyond recorded validation strength |

External corpora are logical evidence authorities even when unmounted. Metadata and rights remain visible; raw rights-restricted payloads and user configuration are not committed. Use `python tools/data_availability_preflight.py list` to filter the register.
