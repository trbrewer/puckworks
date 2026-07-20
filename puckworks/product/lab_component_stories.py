"""Per-component narratives for the Full Laboratory Tour's novice results (#43).

For every registered component: its espresso **process stage** (chronological), the **Role** and
**What physics it represents** text (an exact snapshot of the README model map — verify_component_stories
fails if the snapshot drifts from the live README), a plain **what it computes**, and a layperson
**espresso implications** note.

IMPORTANT — the espresso-implications notes are GENERAL, illustrative relationships from coffee science,
NOT validated predictions from a specific model of a specific shot. Puckworks computes physical
quantities; how they map to taste/texture/quality/caffeine depends on the beans, roast, machine, grinder,
and the drinker's palate. Every note states what the model computes, then a widely-held general
relationship, then a caveat. No note claims this model predicts a cup outcome.
"""
from __future__ import annotations

import dataclasses

PROCESS_ORDER = ("Grind", "Puck formation", "Machine delivery", "Wetting", "Flow", "Puck change",
                 "Extraction")

STANDING_DISCLAIMER = (
    "The 'what this might mean for your cup' notes below are GENERAL relationships from coffee science, "
    "not validated predictions from this model of your specific shot. Puckworks computes physical "
    "quantities; how they translate to taste, texture, strength, or caffeine depends on your beans, "
    "roast, machine, grinder, and palate. A check passing is a consistency check, not proof.")


@dataclasses.dataclass(frozen=True)
class ComponentStory:
    component_id: str
    process_stage: str
    role: str
    physics: str
    what_it_computes: str
    espresso_implications: str

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


# exact snapshot of the README model map (role / physics / stage). verify_component_stories() checks it
# still matches the live README, so the two can never silently drift.
_README_MODEL_MAP = {
    'brewer2026.coupled_kappa_t': {"stage": 'Puck change', "role": 'Exploratory synthesis', "physics": 'Explores how swelling, compaction, fines movement, and extraction-driven porosity change might combine into a time-varying puck resistance. A framework only — as sound as its shakiest donor branch.'},
    'brewer2026.lb_reference': {"stage": 'Flow', "role": 'Pore-scale reference solver', "physics": 'Resolves low-Reynolds pore flow with a D3Q19 two-relaxation-time lattice-Boltzmann solver (verification twin; a Puckworks model).'},
    'brewer2026.lb_taichi': {"stage": 'Flow', "role": 'Pore-scale reference solver', "physics": 'Accelerated (CPU/GPU) build of the same pore-scale flow physics; the `taichi` dependency is optional, so it is not run by default.'},
    'brewer2026.pack_generator': {"stage": 'Puck formation', "role": 'Pore-scale reference', "physics": 'Builds synthetic overlapping-sphere pucks with controlled heterogeneity for pore-scale flow experiments (a Puckworks model).'},
    'brewer2026.streamtube': {"stage": 'Puck change', "role": 'Executable model (separate)', "physics": 'Uneven flow through parallel, non-exchanging paths whose permeability follows a statistical distribution. Calibrated at low dials; interpolated, not externally validated (a Puckworks model).'},
    'cameron2020.extraction_bdf': {"stage": 'Extraction', "role": '**Runs in Guided Pull**', "physics": 'One-dimensional saturated extraction with advection, in-particle diffusion, and nonlinear dissolution from fine and coarse particle families. EK43 dial 1.1–2.3; 20 g in / 40 g out class recipes.'},
    'fasano2000_partI.fines_migration': {"stage": 'Puck change', "role": 'Calibration / comparison', "physics": "Tracks mobile fines, deposition and release, compacted layers, and their effect on Darcy flow. A mechanism demonstration; the closures are ours, not the source paper's."},
    'foster2025.infiltration': {"stage": 'Wetting', "role": 'Executable model (separate)', "physics": 'Tracks a sharp water front advancing through an initially dry puck under a measured or prescribed pressure history. Validated against CT, fine grind.'},
    'foster2025.machine_mode': {"stage": 'Machine delivery', "role": 'Executable model (separate)', "physics": 'Couples pump behavior, pipe resistance, trapped-air headspace, and puck filling to predict delivered pressure and flow. Fine grind; nominal pump.'},
    'grudeva2025.reduced': {"stage": 'Extraction', "role": 'Legacy — rights-blocked pending [#73](https://github.com/trbrewer/puckworks/issues/73)', "physics": "A reduced asymptotic extraction model with a moving wetting front and fine/coarse particle families (saturated-fines regime; prescribed flow). Retained in current history but **not available for Guided Pull Laboratory execution or new integration**: its code is a self-documented port of an unlicensed upstream solver (the article's CC-BY does not license the solver code)."},
    'lee2023.feedback': {"stage": 'Flow', "role": 'Calibration / comparison', "physics": 'Competing flow paths in which extraction changes porosity and permeability, redistributing water. A qualitative fine-grind-dip hypothesis only — the decline needs an unphysical density.'},
    'liang2021.desorption': {"stage": 'Extraction', "role": 'Calibration / comparison', "physics": 'An immersion-derived equilibrium extraction ceiling and retained-liquid correction. **Not** itself a flowing-puck model — it supplies a ceiling and a kernel.'},
    'mo2023_2.coupled_bed': {"stage": 'Extraction', "role": 'Executable model (separate)', "physics": 'Extraction resolved by bed depth using fine/coarse diffusion, partitioning, and a moving filling front under fixed flow. Type-M, cup mass below ~30 g; absolute yield needs one inventory scale.'},
    'mo2023_2.swelling': {"stage": 'Puck change', "role": 'Executable model (separate)', "physics": 'Water entering particles, swelling, loss of pore space, and the resulting decline in permeability and flow. The fixed-pressure flow-decay ratio is reproduced; the swelling claim is unvalidated in the source.'},
    'moroney2016.surrogate': {"stage": 'Extraction', "role": 'Calibration / comparison', "physics": 'A reduced constant-pressure extraction model that captures early release, a plateau, and later wash-through. Qualitative reproduction of the source figure.'},
    'pannusch2024.closures': {"stage": 'Extraction', "role": 'Calibration / comparison', "physics": 'Supplies diffusivity, viscosity, density, Sherwood-number, temperature, and equilibrium relationships used by the pannusch extraction model.'},
    'pannusch2024.solver': {"stage": 'Extraction', "role": 'Executable model (separate)', "physics": 'Extraction from fine and coarse particles with interphase mass transfer and temperature- and flow-dependent transport. 80–98 °C, 1–3 mL/s; the fitted Sherwood law lacks generality.'},
    'romancorrochano2017.extraction': {"stage": 'Extraction', "role": 'Executable model (separate)', "physics": 'Molecular-size-dependent diffusion from spherical coffee grains with partitioning between solid and liquid. Solver verified against the analytic solution; supplies a flow *trend*, not absolute yield.'},
    'sourcing2026.g10_liquor_rheology': {"stage": 'Flow', "role": 'Source-data constraint', "physics": 'Supplies coffee-liquid viscosity and density versus temperature and concentration for flow-resistance studies. Measured on soluble-coffee extract and extrapolated to espresso; the bulk-cup effect is near-negligible.'},
    'sourcing2026.g1_glassbead_analog': {"stage": 'Wetting', "role": 'Source-data constraint', "physics": 'Uses glass-bead retention and relative-permeability measurements as a *shape* prior for wetting. This is an analogy, **not** coffee-specific validation of absolute values.'},
    'sourcing2026.g3_pump_characteristic': {"stage": 'Machine delivery', "role": 'Source-data constraint', "physics": 'Bounds the pump pressure–flow envelope from manufacturer endpoints and community curves. Endpoints are reference-strength; the curve shape is qualitative.'},
    'wadsworth2026.grindmap': {"stage": 'Grind', "role": 'Calibration / comparison', "physics": 'Maps a grinder dial to measured mean particle radius and size spread. Grinder-specific and **not portable** to other grinders.'},
    'wadsworth2026.inertial': {"stage": 'Flow', "role": 'Executable supporting model', "physics": "Adds a Forchheimer inertial-resistance correction where Darcy's linear pressure–flow law starts to fail. A regime flag; the fitted constant is extrapolated for tamped coffee."},
    'wadsworth2026.permeability': {"stage": 'Puck formation', "role": 'Calibration / comparison', "physics": 'Permeability from particle size, porosity, and grain angularity. Validated untamped; the tamped range is an extrapolation.'},
    'waszkiewicz2025.poroelastic': {"stage": 'Puck change', "role": 'Executable model (separate)', "physics": 'Couples puck deformation, pressure, permeability, and dissolution-driven pore change in a saturated poroelastic bed. One rig and coffee; quantitative only above about 5 bar.'},
}

# authored plain-language content per component: (what_it_computes, espresso_implications)
_CONTENT = {
    'brewer2026.coupled_kappa_t': (
        'how several puck-changing effects might combine into a resistance that drifts during the shot.',
        "Real pucks are not static: swelling, settling, and migrating fines make resistance (and therefore flow) drift, which is why late-shot flow often differs from early-shot flow. This is an exploratory synthesis — a framework for that drift, explicitly not a validated law, so read it as 'here is why the shot can change', not a forecast."),
    'brewer2026.lb_reference': (
        'the flow of water through pore geometry, checked against an exact textbook solution.',
        'This is a numerical microscope for pore-scale flow — it underpins the permeability numbers that set shot time and strength, rather than predicting a cup itself. Its tour result is a code self-check (simulated vs the exact analytic answer), so it speaks to trustworthiness of the flow engine, not to taste.'),
    'brewer2026.lb_taichi': (
        'the same pore-scale flow physics as the reference solver, GPU-accelerated for bigger pucks.',
        'It exists to run realistic, large pucks fast enough to study; it is an engine, not a cup predictor. It needs an optional accelerator library, so on a plain runtime it is shown but not run — its absence changes nothing about your shot.'),
    'brewer2026.pack_generator': (
        'a synthetic 3-D coffee puck with a controlled amount of unevenness, for flow experiments.',
        'How evenly the puck is packed governs whether water flows uniformly or races through weak spots (channeling). More even packing generally means more even extraction and a cleaner, more balanced cup; heavy unevenness tends toward thin, sour-and-bitter shots. This is a lab construction tool, not a prediction of your specific puck.'),
    'brewer2026.streamtube': (
        'how uneven paths of different permeability split the flow across the puck.',
        'When some paths run faster than others, water over-extracts the fast lanes (bitter) and under-extracts the slow ones (sour) — the classic channeling signature of a thin, unbalanced shot. This model illustrates that spread; it is calibrated at one grinder setting, so use it to understand channeling, not to score your cup.'),
    'cameron2020.extraction_bdf': (
        'how much soluble coffee is extracted over the shot, giving extraction yield, strength and flow.',
        "This is the model that actually turns your recipe into numbers a drinker feels: extraction yield (how much coffee was pulled from the grounds) and strength/TDS (how concentrated the cup is). As a rule of thumb, higher yield up to roughly the high-teens/low-20s % reads as sweeter and more complex, and beyond that as bitter/astringent; higher TDS reads as heavier and more intense. These are the model's own outputs for one bounded scenario, not a taste guarantee."),
    'fasano2000_partI.fines_migration': (
        'how tiny particles (fines) move, clog, and re-open the puck, changing its resistance.',
        'Migrating fines can pile up and choke flow (a shot that slows or stalls) or wash through and speed it up, and they contribute to the muddy or astringent notes of an unstable pull. This is a mechanism demonstration — it shows the effect exists, not how much it changes your particular shot.'),
    'foster2025.infiltration': (
        'how fast water soaks through the dry puck, and when the first drips should appear.',
        'Even, complete wetting before flow starts is what lets the whole puck extract together; slow or patchy wetting leaves dry pockets that under-extract (sour) while wet channels over-extract (bitter). The timing of first drip is a useful, tangible checkpoint, but it is a bracket, not an exact promise for your machine.'),
    'foster2025.machine_mode': (
        'the pressure and flow the machine actually delivers, given the pump, plumbing and puck.',
        'Delivered pressure and flow shape the whole shot: a slow, controlled pressure build tends to give a gentler, more even extraction, while an abrupt surge can provoke channeling and harshness. This is the machine side of the equation — the same recipe on a different machine can pull very differently.'),
    'grudeva2025.reduced': (
        '(not run) a reduced extraction model — shown for completeness, never executed.',
        "This model is shown but never run: its code is a port of an unlicensed upstream solver, so it is rights-blocked pending a maintainer decision (issue #73). It contributes nothing to your results here — it appears only so the catalogue is complete and honest about what is and isn't available."),
    'lee2023.feedback': (
        'how extraction can feed back on flow by opening or closing pore space as the shot proceeds.',
        'If extraction erodes or swells the bed unevenly, water can progressively favour some paths over others — a driver of channeling and of the flow-rate drift baristas see mid-shot. This is a qualitative mechanism here: it illustrates *why* flow can wander, not a precise flavour outcome.'),
    'liang2021.desorption': (
        'the maximum soluble coffee available and how much liquid the grounds retain.',
        'There is a ceiling to how much a given coffee can give up; this sets that ceiling and accounts for liquid trapped in the grounds (which slightly lowers what reaches the cup). It bounds what is achievable — you cannot out-extract the beans — rather than predicting the flavour of a specific flowing shot.'),
    'mo2023_2.coupled_bed': (
        'how extraction differs from the top to the bottom of the puck as water moves through.',
        'The top of the puck sees fresh water and gives up more; the bottom sees already-loaded water and gives up less — depth-uneven extraction that affects balance in the cup. This resolves that top-to-bottom picture; it runs at a fixed flow, so read it as insight into *where* extraction happens rather than a full recipe result.'),
    'mo2023_2.swelling': (
        'how coffee grains swell as they wet, shrinking pore space and slowing the flow.',
        'Swelling is part of why a shot slows after it starts — grains take up water and close the gaps between them. More swelling generally means a slower back half of the shot and longer contact, nudging strength up; the size of the effect depends on bean, roast and grind, so take the direction, not the exact number.'),
    'moroney2016.surrogate': (
        'the overall shape of extraction over time — a fast start, a plateau, then a tail.',
        'Most of the flavour comes out early and fast, then the shot tails into weaker, wash-through solubles that can taste thin or drying if you pull too long — which is why shot length matters. This captures that shape qualitatively; it is a comparison model, not a calibrated predictor of your cup.'),
    'pannusch2024.closures': (
        'the physical/chemical property relationships (diffusion, temperature, solubility) an extraction solver needs.',
        'These are the underlying property relationships — how fast solubles diffuse, how temperature speeds things up, how much dissolves — that let a full extraction model run. On their own they predict no cup; they matter because temperature and diffusion nudge how quickly and completely a shot extracts (hotter usually extracts a little faster and fuller, within limits).'),
    'pannusch2024.solver': (
        'extraction of several distinct coffee compounds, each with its own diffusion behaviour.',
        'Different compounds leave the grounds at different rates — caffeine and some acids come out readily, while larger, often bitter molecules lag — so *which* compounds you favour shapes taste and caffeine as much as total yield does. This multi-compound view is what makes species-level questions (like caffeine) approachable, though the mapping to your palate is still general.'),
    'romancorrochano2017.extraction': (
        'how compounds of different molecular size diffuse out of the grains at different speeds.',
        'Small molecules (like caffeine and simple acids) diffuse out quickly; large ones (heavier, often bitter or body-giving compounds) come slowly — so a shorter, faster shot skews toward the bright, caffeinated, lighter-bodied end and a longer one pulls more of the heavy, potentially bitter fraction. The model captures that size-based ordering; the flavour labels are general rules of thumb, not its predictions.'),
    'sourcing2026.g10_liquor_rheology': (
        'how thick and dense the brewed coffee liquid is, versus temperature and concentration.',
        'A more concentrated, cooler liquid is slightly thicker and flows a touch slower, which feeds back on shot time. In espresso this effect is small next to grind and pressure, so it mostly matters for precise flow modelling rather than as a taste lever you would notice.'),
    'sourcing2026.g1_glassbead_analog': (
        'the general shape of how partly-wetted porous media hold and release water (from glass beads).',
        'Before a puck is fully saturated, only some of the pore space carries water, which changes how resistance builds early in the shot. Because this comes from glass beads, not coffee, treat it as an analogy for the *shape* of wetting behaviour — it says nothing quantitative about your cup.'),
    'sourcing2026.g3_pump_characteristic': (
        'the plausible range of pressure-vs-flow a typical espresso pump can deliver.',
        'The pump sets the ceiling on how much pressure remains as flow increases; a pump that sags under flow limits how hard you can push a fine grind before pressure drops. This is a bounding constraint on the hardware, not a taste prediction — it mostly tells you what shots are even physically reachable.'),
    'wadsworth2026.grindmap': (
        'how a grinder dial setting corresponds to the average particle size and the spread of sizes.',
        'Grind size is the single biggest lever a barista has: finer grinds pack tighter, slow the water, and (up to a point) raise extraction — often a more intense, sweeter-then-bitter cup — while coarser grinds run faster and can taste weak or sour. This map is specific to one grinder, so treat the dial numbers as illustrative, not universal.'),
    'wadsworth2026.inertial': (
        'when fast flow becomes turbulent enough that simple linear flow laws under-predict resistance.',
        "At high flow the simple 'pressure is proportional to flow' rule starts to under-count resistance; this flags that regime. For normal espresso it is usually a small correction — useful for keeping the flow model honest, not something that reshapes the taste of a standard shot."),
    'wadsworth2026.permeability': (
        'how easily water can pass through the packed coffee, from its particle size and packing.',
        'Permeability sets flow rate for a given pressure: lower permeability (finer/denser) slows the shot and lengthens water–coffee contact, which typically raises strength (TDS) and extraction yield up to the point of over-extraction. The tamped-espresso range is an extrapolation here, so read the direction of the effect rather than an exact number.'),
    'waszkiewicz2025.poroelastic': (
        'how the puck deforms under pressure and how that couples to flow and dissolution.',
        "Under pressure the whole puck compresses and its resistance shifts, which is why the same dose can pull differently as pressure changes — a lever behind pressure-profiling. This is fit to one rig, so it captures the coupled behaviour qualitatively rather than predicting your machine's cup."),
}

_STORIES = {cid: ComponentStory(cid, _README_MODEL_MAP[cid]["stage"], _README_MODEL_MAP[cid]["role"],
                                _README_MODEL_MAP[cid]["physics"], c, e)
            for cid, (c, e) in _CONTENT.items()}


def component_story(component_id):
    return _STORIES.get(component_id)


def all_stories() -> dict:
    return dict(_STORIES)


def ordered_component_ids() -> list:
    """Registered component ids in chronological process order (alphabetical within a stage)."""
    import puckworks
    reg = {c.name for c in puckworks.components()}
    have = [cid for cid in _STORIES if cid in reg]
    return sorted(have, key=lambda cid: (PROCESS_ORDER.index(_STORIES[cid].process_stage), cid))


def _norm(text):
    import re
    return re.sub(r"\s+", " ", text or "").strip()


def _readme_model_map() -> dict:
    """Parse the live README model-map table (role/physics/stage). Returns {} when the README is not
    on disk (installed wheel), so the drift check is a dev/CI guard."""
    import os, re
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(root, "README.md")
    if not os.path.isfile(path):
        return {}
    md = open(path, encoding="utf-8").read()
    m = re.search(r"<!-- puckworks-model-map:start -->(.*?)<!-- puckworks-model-map:end -->", md, re.S)
    block = m.group(1) if m else md
    out = {}
    for stage, cid, role, physics in re.findall(
            r"^\|\s*([^|]+?)\s*\|\s*`([\w.]+)`\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", block, re.M):
        physics = re.sub(r"\s*\(\[card\].*", "", physics).strip()
        physics = re.sub(r"\s*\(\[models\].*", "", physics).strip()
        out[cid] = {"stage": stage.strip(), "role": role.strip(), "physics": physics}
    return out


def verify_component_stories() -> list:
    """Every registered component has a story; the embedded README snapshot matches the live README")
    (role/physics/stage). Returns problems (empty == clean)."""
    import puckworks
    problems = []
    registered = {c.name for c in puckworks.components()}
    for cid in registered:
        if cid not in _STORIES:
            problems.append(f"{cid}: registered component has no narrative story")
    for cid in _STORIES:
        if cid not in registered:
            problems.append(f"{cid}: story names an unregistered component")
    live = _readme_model_map()
    if live:
        for cid, snap in _README_MODEL_MAP.items():
            r = live.get(cid)
            if not r:
                problems.append(f"{cid}: snapshot has a component absent from the live README map")
                continue
            for k in ("stage", "role", "physics"):
                if _norm(snap[k]) != _norm(r[k]):
                    problems.append(f"{cid}: snapshot {k} != live README {k} (regenerate the snapshot)")
        for cid in live:
            if cid not in _README_MODEL_MAP:
                problems.append(f"{cid}: live README map has a component missing from the snapshot")
    return problems
