"""puckworks.registry — component metadata, lookup, and gate execution.

A component is a stage implementation with provenance and validation gates.
The 'mega-model' is a configuration: one registered component per stage (or an
offline calibration chain feeding parameters into runtime components).
"""
from dataclasses import dataclass, field
from typing import Callable

STAGES = ["grind", "packing", "machine", "infiltration", "flow",
          "extraction", "bed_dynamics", "observables"]

@dataclass
class Component:
    name: str
    stage: str
    kind: str                       # "runtime" | "calibration"
    paper: str
    doi: str = ""
    module: str = ""
    assumptions: str = ""
    valid_range: str = ""
    gates: list = field(default_factory=list)   # callables -> dict(passed=bool, ...)
    notes: str = ""

_REGISTRY: dict[str, Component] = {}

def register(c: Component):
    assert c.stage in STAGES, c.stage
    _REGISTRY[c.name] = c
    return c

def components(stage: str | None = None):
    return [c for c in _REGISTRY.values() if stage is None or c.stage == stage]

def get(name: str) -> Component:
    return _REGISTRY[name]

def run_gates(name: str, verbose=True) -> bool:
    c = _REGISTRY[name]
    ok = True
    for g in c.gates:
        r = g()
        ok &= bool(r.get("passed"))
        if verbose:
            print(f"[{name}] {g.__name__}: {'PASS' if r.get('passed') else 'FAIL'}  "
                  f"{ {k: v for k, v in r.items() if k != 'passed'} }")
    return ok

def run_all_gates(verbose=True) -> bool:
    return all(run_gates(n, verbose) for n in sorted(_REGISTRY))
