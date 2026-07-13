"""puckworks.lib — ingestion/utility tooling (NOT registry components).

Code here is *tooling* (harvesters, exporters), not physics: it adds no
registered component and no validation gate (CLAUDE.md rule 1 governs
components; a harvester is plumbing). Anything network-facing lazily imports its
optional dependency so the core package still imports without it, mirroring the
taichi/[lb] pattern.

This subpackage was introduced for the visualizer.coffee harvester (ROADMAP item
0.13); it is the first module under puckworks/lib/.
"""
