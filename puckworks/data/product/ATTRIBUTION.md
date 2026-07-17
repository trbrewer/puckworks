# Bundled product fixtures — attribution and licenses

## waszkiewicz2025_9bar_single_shot — **rights review PENDING**

- **Creators**: Waszkiewicz, R.; Myck, F.; Białas, Ł.; Puciata-Mroczyńska, M.; Dzikowski, M.;
  Szymczak, P.; Lisicki, M.
- **Work**: *"Under pressure: Poroelastic regulation of flow in espresso brewing"*
- **Source record**: Zenodo **10.5281/zenodo.18046315** — https://doi.org/10.5281/zenodo.18046315
  (archive `RadostW-espresso-fbc33d3`, supplement to https://github.com/RadostW/espresso/tree/v1.0.1)
- **Upstream member**: `measurements_time_dependent/9-4.txt`
- **Record-level license**: the Zenodo record displays **CC-BY-4.0**
  (https://creativecommons.org/licenses/by/4.0/) at the record level (resource type *Software*).
- **Member-specific license**: **PENDING**. The archive README applies GPLv3 to "this software"
  without a data-specific carve-out, so the effective license for the selected measurement member is
  **not yet resolved**. A rights-clarification request is open upstream:
  **https://github.com/RadostW/espresso/issues/1**. This is **not** a final CC-BY member-license
  conclusion.
- **Proposed attribution (subject to clarification)**: Waszkiewicz, R. et al., *"Under pressure:
  Poroelastic regulation of flow in espresso brewing"*, Zenodo 10.5281/zenodo.18046315. Modified by
  Puckworks (see below). No upstream source code is redistributed. This does not imply endorsement by
  the original authors.
- **Changes made (modification notice)**: model-independent medoid selection of one 9-bar brew (9-4)
  among 5 replicates; time aligned to the source pressure-settle index (ms→s); line pressure kPa→bar;
  **measured channels only** (time, line pressure, mass) retained; derived flow and basket pressure
  dropped; converted to a normalized CSV.
- **Digests**: source member `original_sha256 = faa98cdea1c571e5f69a63ee3252d777dbd2e7409a99792a2d45734cad51a20b`;
  packaged normalized CSV `normalized_sha256 = 5e41c0af1059f5db8c028815bd795f0905131163186872503f4fcb16ace2c9ef`.

> **Rights review status: PENDING.** Redistribution of this fixture in a published wheel is **gated**
> until an authoritative upstream clarification (or a qualified maintainer rights decision) is
> recorded. The public loader refuses the rights-pending fixture. See the fixture manifest
> (`waszkiewicz2025_9bar_single_shot.manifest.json`) for full provenance, channel semantics,
> deterministic transformations, and the model-independent selection method.
