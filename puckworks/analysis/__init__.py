"""puckworks.analysis — corpus-analysis harness over the visualizer CorpusSnapshot.

All analyses consume a puckworks.data.CorpusSnapshot (never the raw shard iterator),
share one eligibility engine + the P1 measurement dictionary, and emit deterministic
products carrying the snapshot manifest hash + an EXPLORATORY marker when the snapshot
is not a publication-freeze.
"""


def product_envelope(snapshot, product, results, config=None, metric_defs=None):
    """Wrap an analysis result in a deterministic, self-describing envelope (WP1.7): the
    snapshot manifest hash, classification, an EXPLORATORY marker (true unless the snapshot
    is a publication-freeze), the config, metric definitions, and the results. Every plotted
    number must trace back to one of these."""
    m = snapshot.manifest()
    return {
        "product": product,
        "snapshot_name": snapshot.name,
        "snapshot_classification": snapshot.classification,
        "snapshot_manifest_sha256": m["manifest_sha256"],
        "exploratory": snapshot.classification != "publication-freeze",
        "config": dict(config or {}),
        "metric_definitions": dict(metric_defs or {}),
        "results": results,
    }


def histogram(values, edges):
    """Count finite `values` into half-open bins defined by `edges` (last bin closed)."""
    counts = [0] * (len(edges) - 1)
    for v in values:
        if v is None:
            continue
        for i in range(len(edges) - 1):
            lo, hi = edges[i], edges[i + 1]
            if (lo <= v < hi) or (i == len(edges) - 2 and v == hi):
                counts[i] += 1
                break
    return {"edges": list(edges), "counts": counts}
