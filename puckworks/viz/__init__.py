"""puckworks.viz — the evidence-bound VISUALIZATION layer (ROADMAP §8).

A CONSUMING layer, NOT a registry component and NOT a physics gate (CLAUDE.md
rule 1): it renders registered components / harness / data. It EXTENDS the
public/ badge system — every visual is a `VizSpec` that binds to a
`public.schema.Producer`, carries ONE public badge + a ROADMAP §0 evidence
strength rendered INTO the graphic, and declares a fidelity ceiling it may not
exceed. Beautiful is allowed; over-claiming is not.

matplotlib / pillow / imageio are the `[viz]` extra; pyvista / vtk are `[viz3d]`.
The package imports WITHOUT any of them (lazy import, like `[figures]`/`[lb]`);
heavy renders (LB, 3D, video) are never run in CI.

    from puckworks.viz import VIZZES, viz_by_id, validate_all
    python -m puckworks.viz list           # the honesty audit at a glance
    python -m puckworks.viz render --class 1
"""
from .spec import VizSpec, FIDELITY_CEILINGS
from .registry import (VIZZES, viz_by_id, render_all, render_spec, validate_all,
                       write_gallery, stamp_fig, source_commit)

__all__ = ["VizSpec", "FIDELITY_CEILINGS", "VIZZES", "viz_by_id", "render_all",
           "render_spec", "validate_all", "write_gallery", "stamp_fig",
           "source_commit"]
