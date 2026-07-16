"""puckworks — a component registry for espresso process models.

Not a mega-model: a set of stage implementations with typed contracts,
provenance, and validation gates. A model run is a configuration.
"""
__version__ = "0.2.0"
from puckworks import contracts, registry          # noqa: F401
import puckworks.models                            # noqa: F401  (registers components)
