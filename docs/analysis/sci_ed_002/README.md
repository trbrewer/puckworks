# SCI-ED-002 prospective paired inventory and extractability design

Disposition: `SCI_ED_002_PROTOCOL_FROZEN_COMMISSIONING_NOT_AUTHORIZED`.

This is a prospective protocol and deterministic capacity projection. It contains no measurements, does not rerun SCI-MD-007, and does not establish predictor eligibility, physical validation, `Q_production_solid_initial`, or `c_s0`. The governing-physics declaration is `NO_GOVERNING_PHYSICS_CHANGE`.

The open core is VG01–VG05: 30 primary material–roast units from 20 base materials. VG06 contains six units from four additional base materials and remains sealed. Four laboratory roles share the open core; a 144-preparation common bridge is QC-only. Run `python tools/generate_sci_ed_002_package.py`, `python tools/validate_sci_ed_002.py`, and `pytest tests/test_sci_ed_002.py`.

The frozen design is owned here. Espresso Whole Pull may consume only the compact export and crosswalk after pinning the exact candidate commit and tree.
