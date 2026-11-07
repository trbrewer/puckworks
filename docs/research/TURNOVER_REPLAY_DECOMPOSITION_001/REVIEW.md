# Read-only verification

A fresh read-only reviewer found **no concrete defects** and independently:

- authenticated pinned sources and all 224 retained arrays; verified that
  `solute_g` is discharged solute, distinct from internal solute inventory;
- reconstructed all 2,240 windows, 440 condition means, 40 slopes and 36 phase rows;
- checked unchanged native support, observed-onset alignment, achieved-pressure
  pairing, exact brew order and shared resample-bank identity;
- recomputed every late interval using per-brew changes before resampling:
  all twelve cases have positive liquid changes, negative solute changes and
  liquid-dominated totals;
- checked the earlier-phase examples and the limits on interpretation, including
  the provenance disclosure separating original per-array hashes from the index
  file hash newly frozen by this task.

The reviewer ran **11 focused tests**, all passing. The same focused set passes
in the development and retained NumPy 2.0.2 environments. CI-scoped Ruff passes.
Registry gates pass: **66 PASS / one inherited ACKNOWLEDGED_EXCEPTION**.
The figure was visually inspected. Source/document whitespace checks pass;
generated CSV CRLF and Matplotlib SVG path whitespace are preserved.

Required hosted CI results are recorded on the draft PR for its final head.
They are separate from the read-only scientific review and measured main-command
core-hours. No fits, new simulations, EWP writes or historical artifact changes
were performed. No successor is started.
