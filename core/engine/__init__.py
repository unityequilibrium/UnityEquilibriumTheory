"""UET engine: one entry point from the topics to the core equations.

    from core.engine import layer1, layer23, lanes

layer1   parent action in canonical variables and SI units (fifth force, DEF, Bose fluid, drag)
layer23  burn law, lifetime, abundance, selection and bits written (same law at every scale)
lanes    lane cards: how a topic declares which part of the engine it uses

See core/engine/README.md. The engine only wraps derived modules that have physics tests; it adds
no physics of its own. Topic-local constants are not allowed: every number is derived, measured
independently, or a registered limit.
"""

from . import lanes, layer1, layer23

__all__ = ["layer1", "layer23", "lanes"]
