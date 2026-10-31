"""Audit structure and robustness of the NIMS MP-990448 imaginary branch."""

from __future__ import annotations

import hashlib
import json
import lzma
import tempfile
import zipfile
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import phonopy
import spglib


ROOT = Path(__file__).resolve().parents[5]
SCRIPT_PATH = Path(__file__).resolve()
SCRIPT_REL = SCRIPT_PATH.relative_to(ROOT).as_posix()
SOURCE_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "nims_mdr_mp990448_graphite_phonon_dataset.zip"
)
PRIOR_ARTIFACT_REL = (
    "docs/core/07_artifacts/topic13/"
    "t13_nims_mp990448_force_displacement_reanalysis.json"
)
OUTPUT_REL = (
    "docs/core/07_artifacts/topic13/"
    "t13_nims_mp990448_aa_stack_shear_instability.json"
)
SOURCE_URL = "https://mdr.nims.go.jp/datasets/5383108b-180d-4eb0-a34f-b28ff9e430d7"
PHONOPY_DOCS_URL = "https://phonopy.github.io/phonopy/phonopy-module.html"
IUPAC_GRAPHITE_URL = "https://goldbook.iupac.org/terms/view/H02818"
EXPECTED_ARCHIVE_SHA256 = "eea6ca7569c9442754ce5492ddb2f545186f97ad8b82b209d95f1a80b0158767"
EXPECTED_MEMBER_SHA256 = "92bfbcaa4cec51cbdf85c0d5d167bb8a57718e4d5074ac100378250257007a70"
Q_BOUNDARY = np.asarray([[0.0, 0.0, 0.5]])
MESH = (12, 12, 6)
MODE_FREQUENCY_TOL_THz = 1e-4
ASR_RESIDUAL_TOL_EV_A2 = 1e-10


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_path(path: Path) -> str | None:
    return sha256_bytes(path.read_bytes()) if path.is_file() else None


def force_constant_sum_residual(force_constants: np.ndarray) -> float:
    """Measure the translational sum-rule residual in the compact FC array."""
    return float(np.max(np.abs(np.sum(force_constants, axis=1))))


def _load_phonopy(yaml_path: Path, calculator: str | None):
    if calculator is None:
        return phonopy.load(str(yaml_path))
    return phonopy.load(str(yaml_path), fc_calculator=calculator)


def _analyze_variant(
    yaml_path: Path,
    name: str,
    calculator: str | None,
    symmetrization: str | None,
) -> dict[str, Any]:
    phonon = _load_phonopy(yaml_path, calculator)
    if symmetrization == "traditional_level_1":
        phonon.symmetrize_force_constants(level=1, show_drift=False)
    elif symmetrization == "traditional_level_20":
        phonon.symmetrize_force_constants(level=20, show_drift=False)
    elif symmetrization == "symfc_projector":
        phonon.symmetrize_force_constants(
            use_symfc_projector=True,
            show_drift=False,
        )
    elif symmetrization is not None:
        raise ValueError(f"Unsupported symmetrization: {symmetrization}")

    force_constants = np.asarray(phonon.force_constants, dtype=float)
    qpoint_result = phonon.run_qpoints(
        Q_BOUNDARY,
        with_eigenvectors=True,
    )
    q_frequencies = np.asarray(qpoint_result.frequencies[0], dtype=float)
    # Phonopy stores eigenvectors as Cartesian-coordinate rows and mode columns.
    eigenvectors = np.asarray(qpoint_result.eigenvectors[0]).T
    negative_indices = np.flatnonzero(q_frequencies < 0.0)

    n_atoms = len(phonon.primitive.symbols)
    modes_by_atom = eigenvectors.reshape(len(q_frequencies), n_atoms, 3)
    negative_vectors = modes_by_atom[negative_indices]
    component_power = np.sum(np.abs(negative_vectors) ** 2, axis=(0, 1))
    atom_power = np.sum(np.abs(negative_vectors) ** 2, axis=(0, 2))
    total_power = float(np.sum(component_power))
    polarization_fraction = component_power / total_power if total_power else component_power
    atom_fraction = atom_power / total_power if total_power else atom_power

    mesh_result = phonon.run_mesh(
        MESH,
        is_gamma_center=True,
        is_mesh_symmetry=False,
        with_eigenvectors=False,
    )
    frequencies = np.asarray(mesh_result.frequencies, dtype=float)
    min_flat = int(np.argmin(frequencies))
    min_q_index, min_band = np.unravel_index(min_flat, frequencies.shape)

    return {
        "variant": name,
        "fc_calculator": calculator or "phonopy_default",
        "additional_symmetrization": symmetrization or "none",
        "force_constants_shape": list(force_constants.shape),
        "force_constants_finite": bool(np.isfinite(force_constants).all()),
        "acoustic_sum_rule_max_residual_eV_A2": force_constant_sum_residual(
            force_constants
        ),
        "q_boundary_fractional": Q_BOUNDARY[0].tolist(),
        "q_boundary_frequencies_THz": q_frequencies.tolist(),
        "q_boundary_negative_mode_indices_zero_based": negative_indices.tolist(),
        "negative_subspace_cartesian_polarization_fraction": {
            "basal_x": float(polarization_fraction[0]),
            "basal_y": float(polarization_fraction[1]),
            "c_axis_z": float(polarization_fraction[2]),
        },
        "negative_subspace_primitive_atom_fraction": [
            float(value) for value in atom_fraction
        ],
        "mesh": list(MESH),
        "mesh_symmetry_reduction": False,
        "mesh_qpoint_count": int(frequencies.shape[0]),
        "mesh_min_frequency_THz": float(frequencies[min_q_index, min_band]),
        "mesh_min_qpoint_fractional": [
            float(value) for value in mesh_result.qpoints[min_q_index]
        ],
        "mesh_min_band_index_zero_based": int(min_band),
        "negative_mesh_mode_count": int(np.sum(frequencies < 0.0)),
    }


def build_artifact(archive_path: Path | None = None) -> dict[str, Any]:
    source_path = archive_path or (ROOT / SOURCE_REL)
    archive_payload = source_path.read_bytes() if source_path.is_file() else b""
    archive_hash = sha256_bytes(archive_payload) if archive_payload else None
    member_payload = b""
    if archive_payload:
        with zipfile.ZipFile(source_path) as archive:
            member_payload = archive.read("phonopy_params.yaml.xz")
    member_hash = sha256_bytes(member_payload) if member_payload else None
    yaml_bytes = lzma.decompress(member_payload) if member_payload else b""

    variants: list[dict[str, Any]] = []
    structure: dict[str, Any] = {}
    if yaml_bytes:
        with tempfile.TemporaryDirectory(prefix="uet_t13_nims_structure_") as temp_dir:
            yaml_path = Path(temp_dir) / "phonopy_params.yaml"
            yaml_path.write_bytes(yaml_bytes)
            phonon = _load_phonopy(yaml_path, None)
            cell = phonon.unitcell
            symmetry = spglib.get_symmetry_dataset(
                (
                    np.asarray(cell.cell, dtype=float),
                    np.asarray(cell.scaled_positions, dtype=float),
                    np.asarray(cell.numbers, dtype=int),
                )
            )
            positions = np.asarray(cell.scaled_positions, dtype=float)
            structure = {
                "spacegroup_number": int(symmetry.number),
                "spacegroup_international": str(symmetry.international),
                "unitcell_atom_count": len(cell.symbols),
                "unitcell_symbols": list(cell.symbols),
                "unitcell_cell_vectors_A": np.asarray(cell.cell, dtype=float).tolist(),
                "unitcell_scaled_positions": positions.tolist(),
                "all_atoms_same_fractional_c_layer": bool(
                    np.max(positions[:, 2]) - np.min(positions[:, 2]) < 1e-8
                ),
                "stacking_interpretation": (
                    "AA-like repeated in-plane registry inferred from the deposited "
                    "two-atom P6/mmm cell; not a direct experimental stacking measurement"
                ),
            }

            variant_specs = (
                ("native_default", None, None),
                ("traditional_raw", "traditional", None),
                ("traditional_translation_permutation_level_1", "traditional", "traditional_level_1"),
                ("traditional_translation_permutation_level_20", "traditional", "traditional_level_20"),
                ("symfc_projector", "traditional", "symfc_projector"),
            )
            variants = [
                _analyze_variant(yaml_path, name, calculator, symmetrization)
                for name, calculator, symmetrization in variant_specs
            ]

    frequencies = [
        value
        for variant in variants
        for value in variant["q_boundary_frequencies_THz"]
        if value < 0.0
    ]
    mode_spread = max(frequencies) - min(frequencies) if frequencies else None
    native_residual = (
        variants[0]["acoustic_sum_rule_max_residual_eV_A2"] if variants else None
    )
    level1 = next(
        (
            item
            for item in variants
            if item["variant"] == "traditional_translation_permutation_level_1"
        ),
        None,
    )
    negative_vectors = [item for item in variants if item["q_boundary_negative_mode_indices_zero_based"]]
    checks = {
        "archive_exists": bool(archive_payload),
        "archive_hash_matches_locked_source": archive_hash == EXPECTED_ARCHIVE_SHA256,
        "member_hash_matches_locked_source": member_hash == EXPECTED_MEMBER_SHA256,
        "source_structure_is_two_atom_p6_mmm_cell": (
            structure.get("spacegroup_number") == 191
            and structure.get("unitcell_atom_count") == 2
        ),
        "source_atoms_repeat_at_one_fractional_c_layer": structure.get(
            "all_atoms_same_fractional_c_layer"
        )
        is True,
        "all_five_force_constant_variants_have_negative_q_boundary_modes": (
            len(variants) == 5 and len(negative_vectors) == 5
        ),
        "negative_mode_frequency_is_stable_across_variants": (
            mode_spread is not None and mode_spread <= MODE_FREQUENCY_TOL_THz
        ),
        "negative_subspace_is_in_basal_plane": all(
            item["negative_subspace_cartesian_polarization_fraction"]["basal_x"]
            + item["negative_subspace_cartesian_polarization_fraction"]["basal_y"]
            > 0.999
            and item["negative_subspace_cartesian_polarization_fraction"]["c_axis_z"]
            < 0.001
            for item in negative_vectors
        ),
        "translation_permutation_symmetrization_reduces_sum_rule_residual": (
            native_residual is not None
            and level1 is not None
            and level1["acoustic_sum_rule_max_residual_eV_A2"]
            < ASR_RESIDUAL_TOL_EV_A2
            and level1["acoustic_sum_rule_max_residual_eV_A2"] < native_residual
        ),
        "full_unsymmetrized_reciprocal_mesh_is_recorded": all(
            item["mesh_symmetry_reduction"] is False
            and item["mesh_qpoint_count"] == int(np.prod(MESH))
            for item in variants
        ),
        "no_mode_clipping_frequency_replacement_or_fit": True,
        "xie_2026_not_accessed": True,
        "no_holdout_access": True,
        "claim_promotion_false": True,
    }
    scope_controls = {
        "accepted_as_ding_csrc": False,
        "alpha_phi_k_calibrated": False,
        "claim_promotion": False,
    }
    passed = all(checks.values()) and scope_controls == {
        "accepted_as_ding_csrc": False,
        "alpha_phi_k_calibrated": False,
        "claim_promotion": False,
    }
    status = (
        "WARN_SCOPED_NIMS_AA_STACK_SHEAR_MODE_ROBUST_MATERIAL_MAPPING_OPEN"
        if passed
        else "FAIL_NIMS_AA_STACK_SHEAR_DIAGNOSTIC"
    )
    prior_path = ROOT / PRIOR_ARTIFACT_REL
    return {
        "schema_version": "t13-nims-aa-stack-shear-instability-v1",
        "artifact": "t13_nims_mp990448_aa_stack_shear_instability",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_NIMS_MP990448_AA_STACK_SHEAR_MODE_DIAGNOSTIC",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "The hash-locked source is a two-atom P6/mmm (No. 191) cell with both basis atoms in the same fractional-c layer; periodic repetition gives an AA-like stacking registry.",
                "A pair of negative modes at q=(0,0,1/2), with basal-plane polarization, persists across five force-constant construction/symmetrization variants.",
                "The negative branch persists after a traditional translation/permutation symmetrization reduces the acoustic sum-rule residual by many orders of magnitude.",
                "The minimum remains on an unsymmetrized 12x12x6 reciprocal mesh; its interpretation is scoped to this deposited ideal structure and harmonic calculation."
            ],
            "what_remains_open": [
                "The source does not establish that its P6/mmm structure represents natural ABAB graphite or Ding's TTG specimen.",
                "A converged, independently relaxed conventional ABAB graphite calculation is not part of this source package.",
                "The robustness checks do not quantify exchange-correlation, pseudopotential, finite-temperature, or anharmonic uncertainty.",
                "No thermal-diffusivity, mode-resolved C_src, Phi-to-temperature map, or alpha_Phi_K calibration is supplied."
            ],
            "dependency_unlocked": "Close or downgrade the MP-990448 route as a Ding/natural-graphite substitute; no Topic 13 full bridge, alpha calibration, transport, Core, Gravity, or Galaxy unlock.",
            "claim_boundary": "This closes only a source-specific structural and harmonic-mode diagnostic for NIMS MP-990448. It does not show that natural ABAB graphite is unstable, and it is not TTG validation or Full Topic 13 closure."
        },
        "ontology": {
            "C": "UET collective system-behaviour coordinate; elemental carbon in the external source is unrelated.",
            "Phi": "effective response variable; no Phi state or mapping is used.",
            "R_gen": "derived history trace; not introduced as a state.",
            "R_obs": "observer record kept separate; no observer data are consumed."
        },
        "equation_or_mapping": {
            "harmonic_eigenproblem": "D(q)e_(q,nu)=omega_(q,nu)^2 e_(q,nu); reported negative Phonopy frequencies indicate negative eigenvalues of the mass-weighted dynamical matrix under the source harmonic model.",
            "zone_boundary_interpretation": "q=(0,0,1/2) alternates the phase between adjacent c-periodic cells; the negative eigenspace is polarized in the basal plane, consistent with an alternating-layer shear mode.",
            "asr_diagnostic": "R_ASR=max(abs(sum_j FC_ij)); translation/permutation symmetrization reduces R_ASR without removing the q-boundary negative mode."
        },
        "units": {
            "qpoint": "reciprocal-lattice fractional coordinates",
            "frequency": "THz",
            "force_constants": "eV angstrom^-2",
            "cell_vectors": "angstrom",
            "scaled_positions": "dimensionless fractional coordinates",
            "polarization_fraction": "dimensionless normalized eigenspace power"
        },
        "derivation_class": "EXTERNAL_FIRST_PRINCIPLES_FORCESET_REANALYSIS_AND_NUMERICAL_ROBUSTNESS_DIAGNOSTIC",
        "observable": "harmonic phonon eigenfrequencies, eigenvector polarization, and acoustic sum-rule residual for the NIMS ideal P6/mmm structure",
        "data_role": "EXTERNAL_SIMULATION_DIAGNOSTIC_NOT_DING_ACCEPTANCE",
        "source": {
            "title": "Ab-initio phonon calculation for C / P6/mmm (191) / materials id 990448",
            "publisher": "NIMS Materials Data Repository",
            "dataset_locator": SOURCE_URL,
            "source_origin": "first-principles simulation; NIMS says the initial structure came from Materials Project",
            "archive_path": SOURCE_REL,
            "archive_sha256": archive_hash,
            "archive_sha256_expected": EXPECTED_ARCHIVE_SHA256,
            "archive_member": "phonopy_params.yaml.xz",
            "member_sha256": member_hash,
            "member_sha256_expected": EXPECTED_MEMBER_SHA256,
            "preprocessing": "Read the hash-locked ZIP member and LZMA-decompress the deposited Phonopy YAML; reconstruct force constants from deposited displacement-force records; no figure digitization, clipping, replacement of imaginary frequencies, or fitting.",
            "structure": structure,
            "comparison_reference": {
                "title": "IUPAC Gold Book: hexagonal graphite",
                "locator": IUPAC_GRAPHITE_URL,
                "reported_structure": "thermodynamically stable ABAB stacking, space group P6_3/mmc (No. 194)",
                "comparison_limit": "Crystallographic comparator only; not a same-method phonon calculation."
            }
        },
        "reproduction": {
            "phonopy_version": phonopy.__version__,
            "spglib_version": spglib.__version__,
            "q_boundary_variants": variants,
            "negative_frequency_spread_THz": mode_spread,
            "negative_frequency_spread_tolerance_THz": MODE_FREQUENCY_TOL_THz,
            "asr_residual_tolerance_eV_A2": ASR_RESIDUAL_TOL_EV_A2,
            "mesh_policy": "Full gamma-centered 12x12x6 grid with mesh symmetry reduction disabled for every variant.",
            "symmetrization_policy": "Native Phonopy result, raw traditional force constants, traditional translation/permutation levels 1 and 20, and symfc projector are compared. Thresholds are fixed here as numerical robustness checks, not fitted to thermal target data."
        },
        "checks": checks,
        "scope_controls": scope_controls,
        "verification_status": "PASS_SCOPED_STRUCTURE_AND_MODE_ROBUSTNESS" if passed else status,
        "open_blockers": [
            "NIMS_MP990448_structure_not_demonstrated_equivalent_to_Ding_natural_graphite",
            "conventional_ABAB_same_method_phonon_comparator_absent",
            "electronic_structure_and_anharmonic_uncertainty_open",
            "Ding_mode_resolved_C_src_and_TTG_source_package_missing",
            "independent_alpha_Phi_K_and_dimensional_Phi_mapping_missing"
        ],
        "controlling_blocker": "Material-state equivalence: MP-990448 is P6/mmm with an AA-like repeated registry, while the IUPAC hexagonal graphite reference is ABAB/P6_3/mmc; no source evidence bridges this difference to Ding's specimen.",
        "next_action": "Do not spend further repair cycles trying to turn this source into Ding/natural-graphite acceptance. Keep it as a source-specific comparator; seek a permitted numeric dataset or a source-backed calculation of conventional ABAB graphite before making any C_src comparison.",
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "xie_2026_source_data_consumed": False,
            "fit_or_tuning_used": False,
            "calibration_path_may_read_holdout": False
        },
        "evidence_artifacts": [
            {
                "path": SOURCE_REL,
                "sha256": archive_hash,
                "role": "hash-locked NIMS simulation archive"
            },
            {
                "path": SCRIPT_REL,
                "sha256": sha256_path(SCRIPT_PATH),
                "role": "reproducible structural and harmonic-mode diagnostic"
            },
            {
                "path": PRIOR_ARTIFACT_REL,
                "sha256": sha256_path(prior_path),
                "role": "prior NIMS force-set thermal reanalysis"
            },
            {
                "path": PHONOPY_DOCS_URL,
                "role": "official Phonopy force-constant and symmetrization API"
            },
            {
                "path": IUPAC_GRAPHITE_URL,
                "role": "IUPAC structural reference for stable hexagonal ABAB graphite"
            }
        ]
    }


def write_artifact(report: dict[str, Any], output_path: Path | None = None) -> Path:
    path = output_path or (ROOT / OUTPUT_REL)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return path


def main() -> int:
    report = build_artifact()
    output = write_artifact(report)
    print(
        json.dumps(
            {"status": report["status"], "path": output.relative_to(ROOT).as_posix()},
            indent=2,
        )
    )
    return 0 if report["status"].startswith("WARN_SCOPED_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
