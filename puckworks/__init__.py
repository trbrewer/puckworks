"""puckworks — a component registry for espresso process models.

Not a mega-model: a set of stage implementations with typed contracts, provenance, and validation
gates. A model run is a configuration.

SUPPORTED PUBLIC API (see docs/API.md for the stability policy). Everything named in ``__all__``
below is covered by semantic versioning; everything else — ``harness``, ``analysis``, ``paper3``,
``paper_a``, ``paper_b``, ``figures``, ``lib``, ``viz``, ``inventory`` — is INTERNAL research
tooling and may change without notice.
"""
__version__ = "0.3.0.dev0"

from puckworks import contracts, registry, validate   # noqa: F401  (public namespaces)
from puckworks.registry import (                       # noqa: F401
    Component, components, get, load_builtin_components)
from puckworks.gate_runner import (                    # noqa: F401
    evaluate_all_gates, GateStatus, GateResult, GateSuiteResult)

import puckworks.models                                # noqa: F401  (registers built-in components)

__all__ = [
    "__version__",
    # public namespaces
    "contracts", "registry", "validate",
    # registry query
    "Component", "components", "get", "load_builtin_components",
    # gate evaluation
    "evaluate_all_gates", "GateStatus", "GateResult", "GateSuiteResult",
]
