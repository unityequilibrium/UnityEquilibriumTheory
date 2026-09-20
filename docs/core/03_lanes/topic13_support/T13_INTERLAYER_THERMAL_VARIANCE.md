# Local interlayer harmonic thermal variance

MAJOR_RESULT_CLOSURE: PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: A source-locked all-mode calculation of the local relative-layer mass-centroid covariance is implemented and tested; a five-mesh sequence is available.
WHAT_REMAINS_OPEN: Brillouin-zone convergence, spectral attribution, source stability outside sampled points, anharmonic corrections and physical UET mapping.
DEPENDENCY_UNLOCKED: None; full_core_unlock=false.
STATUS: INTERNAL_SOURCE_MODEL_RESULT_NOT_CONVERGED.
WHAT_CHANGED: Harmonic variance runner, four tests, source-hashed artifact and this interpretation; no production dynamics or acceptance threshold changed.
EQUATION_OR_MAPPING: Cov(s)=sum_q O_q diag[hbar*coth(hbar*omega/(2*k_B*T))/(2*mu*omega)] O_q^dagger/Nq, with O_q=B^dagger phase(q)e_q. The zero-temperature limit is taken explicitly.
VERIFICATION: Four tests PASS on this pass: zero-temperature/classical limits, unstable-frequency rejection, degenerate-basis invariance/mass scaling and classical matrix-inverse identity. Existing five-mesh artifact hashes match. Foundation audit PASS with foundation status BLOCKED. The scientific mesh run was completed previously, not rerun for this documentation pass.
CONTROLLING_BLOCKER: unresolved_thermal_covariance_mesh_convergence_and_mode_to_observable_mapping.
NEXT_ACTION: Attribute covariance by frequency/projector before extending the mesh. Check low-frequency contributions, coordinate phase convention and degeneracy-invariant grouping; do not identify acoustic or shear branches by sorted index alone.
CLAIM_BOUNDARY: Harmonic source-model equilibrium fluctuations, not measured pump amplitude, UET Phi, independent alpha, or Full Topic13 closure. No source/holdout acquisition or calibration in this pass.

## What the mesh sequence says

All twelve modes contribute at each shifted mesh point; Gamma is not sampled. Nonpositive eigenvalues invalidate the entire mesh covariance, rather than emitting a positive-mode subset. No unstable points occurred on the sampled grids; this is not global stability proof.

| Temperature K | RMS change, mesh 8 to 12 | Covariance trace change |
| --- | --- | --- |
| 0 | 0.7003% | 1.4056% |
| 100 | 1.8163% | 3.6656% |
| 200 | 3.1726% | 6.4459% |
| 300 | 4.0438% | 8.2511% |

At 300 K the radial RMS increases from 0.0747881 to 0.0778124 angstrom. These differences are diagnostics, not error bars or a newly chosen acceptance threshold. No continuum extrapolation is justified by this sequence alone.

The stronger temperature dependence motivates inspecting low-frequency contributions because the classical oscillator variance scales as inverse frequency squared. This is a hypothesis for the next diagnostic, not an attribution already measured. The finite-mesh minimum eigenvalue decreasing also does not alone imply instability.

## Mapping boundary

This observable is a local relative-layer centroid fluctuation averaged over all wavevectors and modes. It is not a coherent uniform slip or a Gamma-only shear amplitude. Consequently it must not be inserted directly into the earlier Popov first-Fourier force ratio. That comparison additionally requires compatible geometry, state, coordinate normalization and anharmonic model. Finite-grid covariance anisotropy is not itself a measured cubic anisotropy coefficient.

Evidence: `artifacts/t13_interlayer_thermal_variance_audit.json`. Source and implementation hashes are recorded there. No physical dependency or existing Topic13 closure record is promoted.
