"""
Standard Quartic Potential (Landau Theory).
V(u) = (a/2)u^2 + (delta/4)u^4 - s*u
"""
import numpy as np
from uet_core.potentials.base import AbstractPotential, HAS_JAX

# Conditionally import JAX decorators
if HAS_JAX:
    from jax.tree_util import register_pytree_node_class
    import jax.numpy as jnp
else:
    # Dummy decorator when JAX is not available
    def register_pytree_node_class(cls):
        return cls
    jnp = np


@register_pytree_node_class
class QuarticPotential(AbstractPotential):
    def __init__(self, a: float = -1.0, delta: float = 1.0, s: float = 0.0):
        self.a = float(a)
        self.delta = float(delta)
        self.s = float(s)

    def V(self, u: np.ndarray) -> np.ndarray:
        return 0.5 * self.a * u**2 + 0.25 * self.delta * u**4 - self.s * u

    def dV(self, u: np.ndarray) -> np.ndarray:
        return self.a * u + self.delta * u**3 - self.s

    # JAX PyTree methods (only used when JAX is available)
    def tree_flatten(self):
        return ((self.a, self.delta, self.s), None)

    @classmethod
    def tree_unflatten(cls, aux_data, children):
        return cls(*children)
