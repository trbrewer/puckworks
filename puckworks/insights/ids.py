"""Stable identity for tension rows and candidates.

`T-0042` and `I-007` are quoted in decision records, screen bundles, retirement rows, chat
threads and PR comments. If those strings are re-derived from sort position on every build, then
adding one early-sorting row silently renumbers everything after it and every persistent reference
in the repository starts pointing at the wrong record. That is the defect this module closes.

**Identity is a fingerprint, not a position.** A record's ID comes from a hash of the few fields
that say WHAT it is:

    tension    schema version · lens · difference type · sorted entity ids · canonical discriminator
    candidate  schema version · lens · difference type · canonical grouping key

Everything else — the summary prose, the evidence basis, the `why_it_matters` sentence, the sort
order — may be rewritten freely without minting a new ID. That is deliberate: the wording of these
rows *should* improve as the corpus is understood better, and improving it must not cost a
renumber. It is also why `Tension.canonical_discriminator` exists as a slug separate from the
prose `candidate_discriminator`.

**IDs are allocated once and never reused.** `docs/insights/ID_REGISTRY.json` is a tracked,
append-only map of fingerprint to ID plus a high-water mark per prefix. A record that disappears
from the corpus keeps its entry, so:

  * if it comes back — a card is fixed, a manifest row is restored — it gets its ORIGINAL id back;
  * its number is never handed to a different record, so an old reference either resolves to the
    thing it always meant, or resolves to nothing. It never silently resolves to something else.

`build` allocates in memory; `write` persists. `verify` reports `REGISTRY_STALE` when the corpus
contains a fingerprint the tracked registry has not yet recorded.
"""
from __future__ import annotations

import json

from . import schema as S

REGISTRY_REL = "docs/insights/ID_REGISTRY.json"
REGISTRY_PATH = S.REPO_ROOT / REGISTRY_REL

REGISTRY_VERSION = 1

TENSION_PREFIX = "T"
CANDIDATE_PREFIX = "I"
_WIDTH = {"T": 4, "I": 3}


def _fmt(prefix: str, n: int) -> str:
    return "%s-%0*d" % (prefix, _WIDTH[prefix], n)


def tension_fingerprint(t) -> str:
    """Identity of a tension row. Wording-invariant by construction."""
    payload = {
        "kind": "tension",
        "schema_version": S.SCHEMA_VERSION,
        "lens": t.lens,
        "difference_type": t.difference_type,
        "entity_ids": sorted(t.entity_ids),
        "canonical_discriminator": t.canonical_discriminator,
    }
    return S.sha256_text(S.canonical_json(payload))


def candidate_fingerprint(lens: str, difference_type: str, grouping_key) -> str:
    """Identity of a candidate. The grouping key is what the candidate is ABOUT."""
    payload = {
        "kind": "candidate",
        "schema_version": S.SCHEMA_VERSION,
        "lens": lens,
        "difference_type": difference_type,
        "grouping_key": [str(k) for k in grouping_key],
    }
    return S.sha256_text(S.canonical_json(payload))


# ---- the registry --------------------------------------------------------------------------


def empty_registry() -> dict:
    return {"registry_version": REGISTRY_VERSION, "high_water": {"T": 0, "I": 0},
            "tensions": {}, "candidates": {}}


def load() -> dict:
    if not REGISTRY_PATH.exists():
        return empty_registry()
    reg = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    for k, v in empty_registry().items():
        reg.setdefault(k, v)
    return reg


def save(reg: dict) -> str:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(render(reg), encoding="utf-8")
    return REGISTRY_REL


def render(reg: dict) -> str:
    return S.canonical_json({
        "registry_version": reg.get("registry_version", REGISTRY_VERSION),
        "note": "Fingerprint -> stable ID. APPEND-ONLY: an entry is never removed and a number is "
                "never reused, so a stale reference resolves to what it always meant or to "
                "nothing — never to a different record. Regenerate with "
                "`python -m puckworks.insights write`.",
        "high_water": reg["high_water"],
        "counts": {"tensions": len(reg["tensions"]), "candidates": len(reg["candidates"])},
        "tensions": reg["tensions"],
        "candidates": reg["candidates"],
    })


class Allocator:
    """Assigns IDs from a registry, minting new ones in deterministic order.

    Mutates a COPY of the registry in memory; the caller persists it. New fingerprints are minted
    in the order they are offered, and callers offer them in a stable sort, so two builds of the
    same tree mint the same numbers even before anything is written.
    """

    def __init__(self, registry: dict | None = None):
        reg = registry if registry is not None else load()
        self.registry = {"registry_version": reg.get("registry_version", REGISTRY_VERSION),
                         "high_water": dict(reg["high_water"]),
                         "tensions": dict(reg["tensions"]),
                         "candidates": dict(reg["candidates"])}
        self.minted = {"T": [], "I": []}

    def _assign(self, bucket: str, prefix: str, fingerprint: str) -> str:
        table = self.registry[bucket]
        if fingerprint in table:
            return table[fingerprint]
        self.registry["high_water"][prefix] += 1
        new_id = _fmt(prefix, self.registry["high_water"][prefix])
        table[fingerprint] = new_id
        self.minted[prefix].append(new_id)
        return new_id

    def tension_id(self, t) -> str:
        return self._assign("tensions", TENSION_PREFIX, tension_fingerprint(t))

    def candidate_id(self, lens: str, difference_type: str, grouping_key) -> str:
        return self._assign("candidates", CANDIDATE_PREFIX,
                            candidate_fingerprint(lens, difference_type, grouping_key))

    @property
    def minted_any(self) -> bool:
        return bool(self.minted["T"] or self.minted["I"])


def unrecorded(state) -> list:
    """Fingerprints present in a built state that the TRACKED registry does not yet carry."""
    reg = load()
    missing = []
    for t in state["tensions"]:
        fp = tension_fingerprint(t)
        if fp not in reg["tensions"]:
            missing.append("tension %s (%s/%s)" % (t.tension_id, t.lens, t.difference_type))
    for c in state["candidates"]:
        fp = candidate_fingerprint(c.lens, c.difference_type, c.grouping_key)
        if fp not in reg["candidates"]:
            missing.append("candidate %s (%s/%s)" % (c.id, c.lens, c.difference_type))
    return missing
