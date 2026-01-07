"""
Sine-Gordon Potential.
V(u) = 1 - cos(u)
Used for testing modular extensibility.
"""
import numpy as np
from uet_core.potentials.base import AbstractPotential, HAS_JAX

# Conditionally import JAX decorators
if HAS_JAX:
    from jax.tree_util import register_pytree_node_class
    import jax.numpy as jnp
else:
    def register_pytree_node_class(cls):
        return cls
    jnp = np


@register_pytree_node_class
class SineGordonPotential(AbstractPotential):
    def __init__(self, frequency: float = 1.0, amplitude: float = 1.0):
        self.frequency = float(frequency)
        self.amplitude = float(amplitude)

    def V(self, u: np.ndarray) -> np.ndarray:
        return self.amplitude * (1.0 - np.cos(self.frequency * u))

    def dV(self, u: np.ndarray) -> np.ndarray:
        return self.amplitude * self.frequency * np.sin(self.frequency * u)

    # JAX PyTree methods (only used when JAX is available)
    def tree_flatten(self):
        return ((self.frequency, self.amplitude), None)

    @classmethod
    def tree_unflatten(cls, aux_data, children):
        return cls(*children)
