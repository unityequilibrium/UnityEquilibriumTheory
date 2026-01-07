from .base import AbstractPotential
from .quartic import QuarticPotential
from .sine_gordon import SineGordonPotential

def from_dict(d: dict) -> AbstractPotential:
    """Factory method to create potential from dictionary."""
    ptype = d.get("type", "quartic")
    if ptype == "quartic":
        return QuarticPotential(
            a=float(d.get("a", -1.0)),
            delta=float(d.get("delta", 1.0)),
            s=float(d.get("s", 0.0))
        )
    elif ptype == "sine_gordon":
        return SineGordonPotential(
            frequency=float(d.get("frequency", 1.0)),
            amplitude=float(d.get("amplitude", 1.0))
        )
    else:
        # Fallback for legacy configs that might not have type but have alpha/beta
        # Actually usually they have type.
        raise ValueError(f"Unknown potential type: {ptype}")

__all__ = ["AbstractPotential", "QuarticPotential", "SineGordonPotential", "from_dict"]
