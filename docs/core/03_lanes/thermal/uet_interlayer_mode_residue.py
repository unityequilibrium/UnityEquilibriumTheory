"""Mass-metric interlayer diagnostics; no UET state identification or fitting."""

import numpy as np


def shear_basis(masses, layers, normal, tangent):
    masses = np.asarray(masses, dtype=float)
    layers = np.asarray(layers)
    normal, tangent = np.asarray(normal, dtype=float), np.asarray(tangent, dtype=float)
    if masses.ndim != 1 or layers.shape != masses.shape or not np.isfinite(masses).all() or np.min(masses) <= 0:
        raise ValueError('positive finite masses and one layer label per atom required')
    if set(layers.tolist()) != {0, 1} or normal.shape != (3,) or tangent.shape != (3,):
        raise ValueError('two layers and 3D directions required')
    if not np.isfinite([normal, tangent]).all() or np.linalg.norm(normal) == 0:
        raise ValueError('finite nonzero normal required')
    n = normal/np.linalg.norm(normal)
    t = tangent-n*np.dot(n, tangent)
    if np.linalg.norm(t) <= 1e-12*np.linalg.norm(tangent):
        raise ValueError('independent tangent required')
    t /= np.linalg.norm(t)
    axes = np.column_stack([t, np.cross(n, t)])
    ma, mb = (float(np.sum(masses[layers == label])) for label in (0, 1))
    mu = ma*mb/(ma+mb)
    weights = np.where(layers == 0, np.sqrt(masses)/ma, -np.sqrt(masses)/mb)
    basis = (np.sqrt(mu)*weights[:, None, None]*axes[None, :, :]).reshape((-1, 2))
    return basis, mu


def cell_phase(q, positions):
    q, positions = np.asarray(q, dtype=float), np.asarray(positions, dtype=float)
    if q.shape != (3,) or positions.ndim != 2 or positions.shape[1] != 3:
        raise ValueError('fractional q and atom positions required')
    if not np.isfinite(q).all() or not np.isfinite(positions).all():
        raise ValueError('finite phase inputs required')
    return np.repeat(np.exp(2j*np.pi*(positions@q)), 3)


def pair_character(eigenvectors, basis, phase=None):
    vectors, basis = np.asarray(eigenvectors, dtype=complex), np.asarray(basis, dtype=complex)
    if vectors.ndim != 2 or vectors.shape[0] != vectors.shape[1] or basis.shape != (len(vectors), 2):
        raise ValueError('square eigensystem and two-column basis required')
    if not np.isfinite(vectors).all() or not np.isfinite(basis).all():
        raise ValueError('finite vectors required')
    if not np.allclose(vectors.conj().T@vectors, np.eye(len(vectors)), atol=1e-10, rtol=0):
        raise ValueError('orthonormal mass-weighted eigenvectors required')
    if not np.allclose(basis.conj().T@basis, np.eye(2), atol=1e-10, rtol=0):
        raise ValueError('orthonormal shear basis required')
    if phase is not None:
        phase = np.asarray(phase, dtype=complex)
        if phase.shape != (len(vectors),) or not np.isfinite(phase).all() or not np.allclose(abs(phase), 1., atol=1e-12, rtol=0):
            raise ValueError('unit intracell phase required')
        vectors = phase[:, None]*vectors
    overlap = basis.conj().T@vectors
    scores = np.sum(abs(overlap)**2, axis=0)
    selected = np.sort(np.argsort(scores)[-2:])
    pair = vectors[:, selected]
    weight = basis.conj().T@pair@pair.conj().T@basis
    return dict(indices=selected, mode_scores=scores, weight_matrix=weight,
                principal_weights=np.linalg.eigvalsh(weight), pair_vectors=pair)


def projected_resolvent(omega_squared, basis, reduced_mass, laplace_s):
    matrix = np.asarray(omega_squared, dtype=complex)
    basis = np.asarray(basis, dtype=complex)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or basis.shape != (len(matrix), 2):
        raise ValueError('matrix/basis shape mismatch')
    if not np.isfinite(matrix).all() or not np.isfinite(basis).all() or not np.isfinite([reduced_mass, laplace_s]).all() or reduced_mass <= 0:
        raise ValueError('finite inputs and positive reduced mass required')
    if np.max(abs(matrix-matrix.conj().T)) > 1e-12*max(float(np.max(abs(matrix))), 1.):
        raise ValueError('Hermitian dynamical matrix required')
    return basis.conj().T@np.linalg.solve(matrix+laplace_s**2*np.eye(len(matrix)), basis)/reduced_mass
