"""Puckworks Insight Foundry — a bounded research-discovery overlay.

See `docs/insights/INSIGHT_FOUNDRY_DESIGN.md`. The Foundry maps what the repository knows,
surfaces tensions between its parts, and turns them into falsifiable candidate questions. It is
never an authority: every record points back at the registry, a card, the manifest, or a
generated claim, and no Foundry output changes an evidence label or adjudicates a result.
"""
from . import schema  # noqa: F401

__all__ = ["schema"]
