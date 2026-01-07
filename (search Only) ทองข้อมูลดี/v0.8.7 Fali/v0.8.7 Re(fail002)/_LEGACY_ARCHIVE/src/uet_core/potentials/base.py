"""
Base class for UET Potentials.
Uses NumPy by default, with optional JAX support.
"""
from abc import ABC, abstractmethod
import numpy as np

# Try to import JAX, fallback to NumPy
try:
    import jax.numpy as jnp
    HAS_JAX = True
except ImportError:
    jnp = np
    HAS_JAX = False

class AbstractPotential(ABC):
    """
    Abstract base class for potentials.
    Works with both NumPy and JAX arrays.
    """

    @abstractmethod
    def V(self, u: np.ndarray) -> np.ndarray:
        """Compute potential energy V(u)."""
        pass

    @abstractmethod
    def dV(self, u: np.ndarray) -> np.ndarray:
        """Compute first derivative V'(u) = dV/du."""
        pass
