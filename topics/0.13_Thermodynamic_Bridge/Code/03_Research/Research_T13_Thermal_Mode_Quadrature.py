"""Batched exact tree-mode quadrature, retaining the same pole/vertex contract.

The acoustic root uses the declared Schur curvature fixed point, not the
ill-conditioned small eigenvalue of a companion matrix. Heavy tree poles
use the same companion and symplectic normalization as the scalar verifier.
"""

import numpy as np

import Research_T13_Thermal_Virtual_Response as VIRT


def tree_modes_batch(momenta, state, action):
    momenta = np.asarray(momenta, dtype=float)
    if momenta.ndim != 1 or len(momenta) == 0 or not np.all(np.isfinite(momenta)) or np.any(momenta <= 0):
        raise ValueError("nonempty positive finite momentum array required")
    VIRT.TH.validate(float(momenta[0]), 0., state, action, 2)
    cf = VIRT.INT.dispersion_coefficients(state, action)
    c, a0, v = cf["c"], cf["A0"], state["V_curvature"]
    kp, g, mu, s = action["epsilon"]*action["response_kinetic"], action["gamma"], state["mu"], state["s"]
    squared, curvature = momenta**2, np.full_like(momenta, 2*c*cf["eta"])
    for _ in range(64):
        ratio = c*c+squared*curvature
        ell = squared*(1-ratio)
        hh = 1+g*g*s*kp/(v*(v+kp*ell))
        updated = 4*mu*mu*(1-ratio)*hh/((a0+ell*hh+4*mu*mu)*(a0+4*mu*mu))
        converged = np.all(abs(updated-curvature) <= 2e-15*np.maximum(abs(updated), 1e-30))
        curvature = updated
        if converged:
            break
    else:
        raise ValueError("batched tree curvature did not converge")
    ratio = c*c+squared*curvature
    if np.any(ratio < c*c) or np.any(ratio >= 1):
        raise ValueError("tree root outside admitted convex branch")
    energy = c*momenta+momenta**3*curvature/(np.sqrt(ratio)+c)
    ell, w = squared-energy**2, v+kp*(squared-energy**2)
    hh = 1+g*g*s*kp/(v*w)
    den = a0+ell*hh
    aa, bb = 2*mu*energy/den, g*np.sqrt(s)*(2*mu*energy/den)/w
    norm = 1+4*mu*mu/den+aa**2+kp*bb**2
    acoustic = np.stack([-1j*aa, np.ones_like(aa), -1j*bb], axis=-1)/np.sqrt(norm[:, None])
    kinetic, linear, v0 = VIRT.matrices(0., state, action)
    count = len(momenta)
    companion = np.zeros((count, 6, 6), dtype=complex)
    companion[:, :3, 3:] = np.eye(3)
    companion[:, 3:, :3] = np.linalg.solve(kinetic, v0)+squared[:, None, None]*np.eye(3)
    companion[:, 3:, 3:] = np.linalg.solve(kinetic, linear)
    eigenvalues = np.linalg.eigvals(companion)
    if np.max(abs(eigenvalues.imag)) > 1e-9:
        raise ValueError("stable real tree poles required")
    ordered = np.sort(eigenvalues.real, axis=-1)
    if np.any(ordered[:, 2] >= 0) or np.any(ordered[:, 3] <= 0):
        raise ValueError("three positive and three negative tree poles required")
    heavy = ordered[:, 4:]
    kernels = v0+squared[:, None, None, None]*kinetic-heavy[:, :, None, None]**2*kinetic+heavy[:, :, None, None]*linear
    values, vectors = np.linalg.eigh(kernels)
    null = np.argmin(abs(values), axis=-1)
    units = np.take_along_axis(vectors, null[:, :, None, None], axis=-1)[..., 0]
    derivative = -2*heavy[:, :, None, None]*kinetic+linear
    norm = -np.einsum("nki,nkij,nkj->nk", units.conjugate(), derivative, units).real
    if np.any(norm <= 0):
        raise ValueError("positive symplectic pole norm required")
    units *= np.sqrt(2*heavy/norm)[:, :, None]
    return np.concatenate([energy[:, None], heavy], axis=1), np.concatenate([acoustic[:, None, :], units], axis=1)


def bose_array(energies, temperature):
    energies = np.asarray(energies)
    if temperature <= 0 or not np.isfinite(temperature) or np.any(energies <= 0) or not np.all(np.isfinite(energies)):
        raise ValueError("positive energies and finite positive T required")
    y = energies/temperature
    return np.exp(-y)/(-np.expm1(-y))


def static_channels_batch(p, momenta_r, vertex, temperature, state, action, modes_p):
    energies_r, units_r = tree_modes_batch(momenta_r, state, action)
    result = {key: np.zeros(len(momenta_r)) for key in ("pair", "intrabranch_population", "mixed_number")}
    population_r = bose_array(energies_r[:, 0], temperature)
    for i, (ep, up) in enumerate(modes_p):
        npop = VIRT.TH.bose(ep/temperature) if i == 0 else 0.
        for j in range(3):
            if i != 0 and j != 0:
                continue
            er, ur = energies_r[:, j], units_r[:, j]
            rpop = population_r if j == 0 else 0.
            pair = abs(np.einsum("a,ab,nb->n", up, vertex, ur))**2
            number = abs(np.einsum("a,ab,nb->n", up.conjugate(), vertex, ur))**2
            result["pair"] += (npop+rpop)*pair/(4*ep*er*(ep+er))
            if i == j == 0:
                width = abs(er-ep)/temperature
                factor = np.ones_like(width)
                np.divide(-np.expm1(-width), width, out=factor, where=width != 0)
                divided = bose_array(np.minimum(er, ep), temperature)*(1+bose_array(np.maximum(er, ep), temperature))*factor/temperature
                result["intrabranch_population"] += divided*number/(4*ep*er)
            else:
                if np.any(er == ep):
                    raise ValueError("unadmitted acoustic-heavy degeneracy")
                result["mixed_number"] += (npop-rpop)*number/(4*ep*er*(er-ep))
    return result
