"""Shared viz palette — extends the house figure palette (do not fork it).

Imports the print tokens from `puckworks.figures` (one palette, not three) and
adds: the four BADGE colours (matched to the public badge vocabulary) and
colourblind-safe field colormaps for class-2 renders. matplotlib is NOT imported
here — only colour strings + colormap NAMES — so this module stays import-clean.
"""
from __future__ import annotations

# the existing house tokens (figures.py imports matplotlib lazily, not at top)
from ..figures import INK, NULL, GOOD

# Badge colours — one per public.schema.BADGES entry. Blue/amber/green/grey,
# colourblind-safe and consistent with the paper_b status palette convention
# (colour PLUS a text label, never colour alone).
BADGE_COLORS = {
    "OBSERVED": GOOD,                 # measured / digitized data
    "RECONSTRUCTED": "#2c7fb8",       # model on its own calibration data
    "PREDICTED": "#5a3fa0",           # genuine held-out / transfer test
    "EXPLORATORY_SIMULATION": NULL,   # mechanism demo, no empirical identification
}
BADGE_TEXT_COLOR = "#ffffff"

# Colourblind-safe field colormaps (matplotlib built-ins; perceptually uniform).
# Named here so class-2 renders share one convention. cividis/viridis are
# colourblind-safe sequential; PuOr is a safe diverging map for signed fields.
FIELD_SEQUENTIAL = "cividis"         # porosity / speed magnitude / concentration
FIELD_SEQUENTIAL_ALT = "viridis"     # pressure
FIELD_DIVERGING = "PuOr"             # signed fields (e.g. velocity component)

# stage colours for the process schematic (neutral, print-safe)
STAGE_INK = INK
STAGE_FILL = "#f2ebe0"
STAGE_EDGE = "#cdbfad"
