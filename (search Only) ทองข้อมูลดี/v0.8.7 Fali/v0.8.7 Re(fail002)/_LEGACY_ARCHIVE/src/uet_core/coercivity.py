"""
Coercivity / boundedness guards for Ω.
Implements simple *sufficient* checks; does not claim necessity.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Tuple

@dataclass
class CoercivityResult:
    status: str
    code: str
    message: str

def _get_pot_coeffs(pot: Dict[str, Any]) -> Tuple[float, float, float]:
    a = float(pot.get("a", 0.0))
    delta = float(pot.get("delta", 0.0))
    s = float(pot.get("s", 0.0))
    return a, delta, s

def _field_coercive(a: float, delta: float) -> bool:
    return (delta > 0.0) or (delta == 0.0 and a > 0.0)

def check_C_only(params: Dict[str, Any]) -> CoercivityResult:
    pot = params.get("pot", {})
    a, delta, _ = _get_pot_coeffs(pot)
    kappa = float(params.get("kappa", 0.0))
    if kappa <= 0.0:
        return CoercivityResult("FAIL","COERCIVITY_KAPPA_NONPOS","kappa must be > 0.")
    if delta < 0.0:
        return CoercivityResult("FAIL","COERCIVITY_DELTA_NEG","delta < 0 => unbounded below.")
    if delta == 0.0 and a <= 0.0:
        return CoercivityResult("FAIL","COERCIVITY_NO_GROWTH","delta=0 and a<=0 => no coercive growth.")
    if delta == 0.0 and a > 0.0:
        return CoercivityResult("WARN","COERCIVITY_QUADRATIC_ONLY","quadratic-only; boundedness depends on a>0.")
    if 0.0 < delta < 1e-6:
        return CoercivityResult("WARN","COERCIVITY_DELTA_TINY","delta tiny; stiffness/scaling issues likely.")
    return CoercivityResult("PASS","COERCIVITY_OK","Sufficient coercivity holds.")

def check_CI(params: Dict[str, Any]) -> CoercivityResult:
    potC = params.get("potC", {})
    potI = params.get("potI", {})
    aC, dC, _ = _get_pot_coeffs(potC)
    aI, dI, _ = _get_pot_coeffs(potI)
    kC = float(params.get("kC", 0.0))
    kI = float(params.get("kI", 0.0))
    beta = float(params.get("beta", 0.0))

    if kC <= 0.0 or kI <= 0.0:
        return CoercivityResult("FAIL","COERCIVITY_KAPPA_NONPOS","kC and kI must be > 0.")
    if dC < 0.0 or dI < 0.0:
        return CoercivityResult("FAIL","COERCIVITY_DELTA_NEG","deltaC<0 or deltaI<0 => unbounded below.")
    if not _field_coercive(aC, dC):
        return CoercivityResult("FAIL","COERCIVITY_C_NO_GROWTH","C lacks coercive growth.")
    if not _field_coercive(aI, dI):
        return CoercivityResult("FAIL","COERCIVITY_I_NO_GROWTH","I lacks coercive growth.")

    if dC == 0.0 and dI == 0.0:
        disc = aC*aI - beta*beta
        if aC <= 0.0 or aI <= 0.0:
            return CoercivityResult("FAIL","COERCIVITY_QUAD_NONPOS","Quadratic-only needs aC>0 and aI>0.")
        if disc <= 0.0:
            return CoercivityResult("FAIL","COERCIVITY_QUAD_INDEFINITE","Need aC*aI - beta^2 > 0.")
        if disc < 1e-6:
            return CoercivityResult("WARN","COERCIVITY_QUAD_NEAR_SINGULAR","Discriminant small; near loss of boundedness.")
        return CoercivityResult("PASS","COERCIVITY_OK_QUADRATIC","Quadratic-only sufficient condition holds.")

    tiny = []
    if 0.0 < dC < 1e-6: tiny.append("deltaC")
    if 0.0 < dI < 1e-6: tiny.append("deltaI")
    if tiny:
        return CoercivityResult("WARN","COERCIVITY_DELTA_TINY",f"{', '.join(tiny)} tiny; stiffness/scaling issues likely.")
    return CoercivityResult("PASS","COERCIVITY_OK","Sufficient coercivity holds.")
