"""Run mass-averaged isotope sensitivity for the Calorine C_src candidate.

This is a state-sensitivity diagnostic. It reuses mass-independent force
constants, changes only the primitive carbon mass, and never fits a target or
maps the result to Phi. Defect, morphology, and isotope-scattering effects are
not silently folded into this harmonic mass-only lane.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import h5py
import numpy as np
from ase.io import read
from phono3py import Phono3py
from phono3py.file_IO import read_fc2_from_hdf5, read_fc3_from_hdf5
from phonopy.interface.calculator import read_crystal_structure


EV_TO_J = 1.602176634e-19
ANGSTROM3_TO_M3 = 1.0e-30
ROOT = Path(__file__).resolve().parents[3]
DEFAULT_FORCE_DIR = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/reproduction/t13_calorine_pbte/force_constants_dim_4x4x2"
DEFAULT_OUTPUT_DIR = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/reproduction/t13_calorine_pbte/isotope_mass_sensitivity"
NIST_LOCATOR = "https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ascii=ascii&ele=C"


def parse_triplet(value: str) -> tuple[int, int, int]:
    parts = tuple(int(item.strip()) for item in value.split(","))
    if len(parts) != 3 or any(item <= 0 for item in parts):
        raise argparse.ArgumentTypeError("expected three positive integers, e.g. 10,10,5")
    return parts


def parse_temperatures(value: str) -> tuple[float, ...]:
    values = tuple(float(item.strip()) for item in value.split(","))
    if not values or any(item <= 0 for item in values):
        raise argparse.ArgumentTypeError("expected positive Kelvin values")
    return values


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path, locator: str | None = None) -> dict[str, object]:
    return {
        "path": path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
        "size_bytes": path.stat().st_size,
        "sha256": sha256(path),
        "locator": locator,
    }


def isotope_states() -> dict[str, dict[str, object]]:
    c12 = 12.0000000
    c13 = 13.00335483507
    natural_fraction = 0.0107
    lower_fraction = 0.0107 - 0.0008
    upper_fraction = 0.0107 + 0.0008

    def state(name: str, fraction_13c: float, role: str) -> dict[str, object]:
        mass = (1.0 - fraction_13c) * c12 + fraction_13c * c13
        return {
            "name": name,
            "fraction_12C": 1.0 - fraction_13c,
            "fraction_13C": fraction_13c,
            "mass_amu": mass,
            "role": role,
        }

    return {
        "natural_reference": state("natural_reference", natural_fraction, "NIST representative natural-composition reference"),
        "natural_lower_13C": state("natural_lower_13C", lower_fraction, "NIST composition lower bound"),
        "natural_upper_13C": state("natural_upper_13C", upper_fraction, "NIST composition upper bound"),
        "pure_12C_stress": state("pure_12C_stress", 0.0, "isotopic stress bound; not Ding specimen state"),
        "pure_13C_stress": state("pure_13C_stress", 1.0, "isotopic stress bound; not Ding specimen state"),
    }


def make_phono3py(poscar: Path, dim: tuple[int, int, int], mass_amu: float) -> Phono3py:
    unitcell, _ = read_crystal_structure(str(poscar), interface_mode="vasp")
    ph3 = Phono3py(unitcell, supercell_matrix=dim, primitive_matrix="P")
    ph3.masses = [mass_amu] * len(ph3.primitive.masses)
    return ph3


def run_state(
    force_dir: Path,
    output_dir: Path,
    state: dict[str, object],
    dim: tuple[int, int, int],
    mesh: tuple[int, int, int],
    temperatures: tuple[float, ...],
) -> dict[str, object]:
    poscar = force_dir / "POSCAR"
    fc2 = force_dir / "fc2.hdf5"
    fc3 = force_dir / "fc3.hdf5"
    state_dir = output_dir / str(state["name"])
    state_dir.mkdir(parents=True, exist_ok=True)
    ph3 = make_phono3py(poscar, dim, float(state["mass_amu"]))
    ph3.fc2 = read_fc2_from_hdf5(fc2)
    ph3.fc3 = read_fc3_from_hdf5(fc3)
    ph3.mesh_numbers = list(mesh)
    current = Path.cwd()
    os.chdir(state_dir)
    try:
        ph3.init_phph_interaction()
        ph3.run_thermal_conductivity(
            temperatures=list(temperatures),
            is_LBTE=False,
            write_kappa=True,
        )
    finally:
        os.chdir(current)
    kappa_path = state_dir / f"kappa-m{mesh[0]}{mesh[1]}{mesh[2]}.hdf5"
    poscar_atoms = read(poscar, format="vasp")
    volume_a3 = float(poscar_atoms.get_volume())
    with h5py.File(kappa_path, "r") as handle:
        stored_temperatures = np.asarray(handle["temperature"][:], dtype=float)
        mode_cv = np.asarray(handle["heat_capacity"][:], dtype=float)
        weights = np.asarray(handle["weight"][:], dtype=float)
        frequencies = np.asarray(handle["frequency"][:], dtype=float)
        stored_mesh = tuple(int(item) for item in handle["mesh"][:])
    if stored_mesh != mesh:
        raise ValueError(f"HDF5 mesh {stored_mesh} differs from requested {mesh}")
    if not np.allclose(stored_temperatures, np.asarray(temperatures, dtype=float)):
        raise ValueError("HDF5 temperatures differ from requested values")
    weighted_mode_cv = np.einsum("g,tgb->t", weights, mode_cv) / float(weights.sum())
    c_src = weighted_mode_cv * EV_TO_J / (volume_a3 * ANGSTROM3_TO_M3)
    summary = {
        "schema_version": "t13-calorine-isotope-mass-state-run-v1",
        "state": state,
        "run": {
            "dim": list(dim),
            "mesh": list(mesh),
            "temperatures_K": list(temperatures),
            "transport_solver": "RTA control; isotope scattering disabled",
            "force_constants_mass_independent_reused": True,
            "target_curve_used": False,
            "fit_performed": False,
            "alpha_Phi_K_fit_performed": False,
            "holdout_accessed": False,
        },
        "unit_contract": {
            "mass": "amu",
            "mode_heat_capacity_input": "eV K^-1 per mode per primitive cell",
            "output": "J m^-3 K^-1",
            "aggregation": "C_src = sum_q w_q sum_mu c_qmu / (sum_q w_q V_primitive)",
        },
        "geometry": {
            "primitive_volume_A3": volume_a3,
            "q_weight_sum": float(weights.sum()),
            "frequency_range_THz": [float(np.nanmin(frequencies)), float(np.nanmax(frequencies))],
        },
        "c_src_rows": [
            {"temperature_K": float(temp), "C_src_J_m^-3_K^-1": float(value)}
            for temp, value in zip(stored_temperatures, c_src, strict=True)
        ],
        "force_constants": {
            "poscar": record(poscar),
            "fc2": record(fc2),
            "fc3": record(fc3),
        },
        "output_artifact": record(kappa_path),
        "claim_boundary": "Mass-averaged harmonic isotope sensitivity only; no isotope-disorder scattering, vacancy, morphology, Ding-equivalence, Phi map, alpha_Phi_K, or external-validation claim.",
    }
    summary_path = state_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return summary

def build_uncertainty_audit(isotope_audit: dict[str, object], isotope_audit_path: Path) -> tuple[Path, dict[str, object]]:
    reproduction_path = ROOT / "docs/core/07_artifacts/topic13/t13_calorine_zenodo_nep_bte_reproduction_audit.json"
    if not reproduction_path.is_file():
        raise FileNotFoundError(f"missing Calorine reproduction audit: {reproduction_path}")
    reproduction = json.loads(reproduction_path.read_text(encoding="utf-8-sig"))
    state_max = {
        str(item["state"]["name"]): max(
            float(row["relative_change_to_natural_reference"]) for row in item["rows"]
        )
        for item in isotope_audit["sensitivity"]
    }
    composition_envelope = max(state_max["natural_lower_13C"], state_max["natural_upper_13C"])
    stress_envelope = max(state_max["pure_12C_stress"], state_max["pure_13C_stress"])
    artifact = {
        "schema_version": "t13-calorine-state-uncertainty-decomposition-audit-v1",
        "artifact": "t13_calorine_state_uncertainty_decomposition_audit",
        "status": "PASS_SCOPED_CALORINE_STATE_UNCERTAINTY_DECOMPOSITION",
        "major_result": {
            "major_result_id": "T13_CALORINE_STATE_UNCERTAINTY_DECOMPOSITION",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": [
                "q-mesh numerical envelope is separated from material-state sensitivity",
                "NIST natural-carbon composition bounds are propagated through the mass-only C_src lane",
                "pure-isotope runs are retained as stress bounds, not Ding specimen uncertainty",
                "no fit, target tuning, alpha_Phi_K calibration, or holdout access is used",
            ],
            "equation_or_mapping": {
                "mesh": "epsilon_mesh = max_T |C_src(mesh_hi,T)-C_src(mesh_prev,T)| / |C_src(mesh_hi,T)|",
                "composition": "epsilon_isotope = max_T,state |C_src(state,T)-C_src(natural,T)| / |C_src(natural,T)|",
                "boundary": "epsilon_source_grade is not inferred from mesh plus mass-only sensitivity",
            },
            "units": {"C_src": "J m^-3 K^-1", "temperature": "K", "envelopes": "dimensionless"},
            "derivation_class": "numerical convergence plus external isotope-state sensitivity; no UET derivation",
            "observable": "Calorine candidate C_src uncertainty decomposition",
            "data_role": "STATE_SENSITIVITY_NOT_CALIBRATION",
            "evidence_artifacts": [
                {"path": isotope_audit_path.relative_to(ROOT).as_posix()},
                {"path": reproduction_path.relative_to(ROOT).as_posix()},
            ],
            "verification_status": "PASS_SCOPED_CALORINE_STATE_UNCERTAINTY_DECOMPOSITION",
            "open_blockers": [
                "material_regime_mapping_to_TTG_not_closed",
                "calorine_route_source_grade_model_and_state_uncertainty_missing",
            ],
            "dependency_unlocked": "uncertainty decomposition lane only; no Ding C_src, alpha_Phi_K, transport, Core, Gravity, or Galaxy unlock",
            "claim_boundary": "Numerical and mass-only sensitivity decomposition only; not source-grade uncertainty, Ding equivalence, Phi mapping, alpha_Phi_K, or TTG prediction.",
        },
        "source": {
            "nist_locator": NIST_LOCATOR,
            "representative_fraction_13C": {"value": 0.0107, "uncertainty": 0.0008},
            "source_role": "external isotope-composition reference, not a Ding specimen measurement",
        },
        "components": {
            "mesh_numerical_envelope": {
                "value": reproduction["reproduction"]["convergence"]["latest_pair"]["max_relative_change"],
                "scope": "8x8x4 to 10x10x5 at fixed 4x4x2 force constants and RTA",
                "source_grade": False,
            },
            "natural_composition_mass_envelope": {
                "value": composition_envelope,
                "per_state_max": {
                    "natural_lower_13C": state_max["natural_lower_13C"],
                    "natural_upper_13C": state_max["natural_upper_13C"],
                },
                "source_grade": False,
            },
            "pure_isotope_stress_envelope": {
                "value": stress_envelope,
                "per_state_max": {
                    "pure_12C_stress": state_max["pure_12C_stress"],
                    "pure_13C_stress": state_max["pure_13C_stress"],
                },
                "interpretation": "stress bound only; not the Ding specimen state and not added to source uncertainty",
                "source_grade": False,
            },
        },
        "checks": {
            "mesh_audit_present": True,
            "isotope_audit_present": True,
            "source_grade_uncertainty_present": False,
            "material_state_mapping_to_ding": False,
            "target_fit_performed": False,
            "alpha_Phi_K_fit_performed": False,
            "holdout_accessed": False,
        },
        "controlling_blocker": "material_regime_mapping_to_TTG_not_closed",
        "next_controller": "Source-lock defect and morphology, or retain Calorine as a non-Ding comparator; do not turn this decomposition into source-grade uncertainty.",
        "claim_boundary": "Candidate numerical/state sensitivity decomposition only; not Ding C_src acceptance, alpha_Phi_K calibration, or Full Topic 13 closure.",
        "evidence_artifacts": [
            {
                "path": isotope_audit_path.relative_to(ROOT).as_posix(),
                "sha256": sha256(isotope_audit_path),
                "summary": {"role": "mass-only isotope sensitivity audit"},
            },
            {
                "path": reproduction_path.relative_to(ROOT).as_posix(),
                "sha256": sha256(reproduction_path),
                "summary": {"role": "q-mesh numerical convergence audit"},
            },
        ],
    }
    output_path = ROOT / "docs/core/07_artifacts/topic13/t13_calorine_state_uncertainty_decomposition_audit.json"
    output_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return output_path, artifact

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force-dir", type=Path, default=DEFAULT_FORCE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dim", type=parse_triplet, default=(4, 4, 2))
    parser.add_argument("--mesh", type=parse_triplet, default=(10, 10, 5))
    parser.add_argument("--temperatures", type=parse_temperatures, default=(200.0, 250.0, 300.0))
    args = parser.parse_args()
    force_dir = args.force_dir.resolve()
    output_dir = args.output_dir.resolve()
    for name in ("POSCAR", "fc2.hdf5", "fc3.hdf5"):
        if not (force_dir / name).is_file():
            raise FileNotFoundError(f"missing force-constant input: {force_dir / name}")
    states = isotope_states()
    runs = [run_state(force_dir, output_dir, state, args.dim, args.mesh, args.temperatures) for state in states.values()]
    by_name = {str(run["state"]["name"]): run for run in runs}
    reference_rows = by_name["natural_reference"]["c_src_rows"]
    sensitivity_rows = []
    for run in runs:
        rows = []
        for reference, current in zip(reference_rows, run["c_src_rows"], strict=True):
            reference_value = float(reference["C_src_J_m^-3_K^-1"])
            current_value = float(current["C_src_J_m^-3_K^-1"])
            rows.append(
                {
                    "temperature_K": current["temperature_K"],
                    "relative_change_to_natural_reference": abs(current_value - reference_value) / abs(reference_value),
                }
            )
        sensitivity_rows.append({"state": run["state"], "rows": rows})
    audit = {
        "schema_version": "t13-calorine-isotope-mass-sensitivity-audit-v1",
        "artifact": "t13_calorine_isotope_mass_sensitivity_audit",
        "status": "PASS_SCOPED_CALORINE_ISOTOPE_MASS_SENSITIVITY",
        "major_result": {
            "major_result_id": "T13_CALORINE_ISOTOPE_MASS_SENSITIVITY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": [
                "NIST representative carbon isotope composition and uncertainty bounds are source-located",
                "the same mass-independent force constants are rerun under natural-reference, composition-bound, and pure-isotope mass states",
                "the mass-only contribution to C_src sensitivity is reported in J m^-3 K^-1 without fitting",
            ],
            "equation_or_mapping": {
                "mass_average": "m_bar = f_12 m_12 + f_13 m_13",
                "sensitivity": "delta_C_src_state(T) = |C_src_state(T)-C_src_natural(T)| / C_src_natural(T)",
            },
            "units": {"mass": "amu", "C_src": "J m^-3 K^-1", "temperature": "K"},
            "derivation_class": "external isotope composition plus mass-only harmonic sensitivity; no UET derivation",
            "observable": "Calorine candidate C_src isotope-state sensitivity",
            "data_role": "STATE_SENSITIVITY_NOT_CALIBRATION",
            "verification_status": "PASS_SCOPED_CALORINE_ISOTOPE_MASS_SENSITIVITY",
            "open_blockers": [
                "calorine_route_defect_state_mapping_to_ding_missing",
                "calorine_route_morphology_mapping_to_ding_missing",
                "source_grade_uncertainty_not_closed_by_mass_only_sensitivity",
            ],
            "dependency_unlocked": "isotope mass sensitivity lane only; no Ding C_src, alpha_Phi_K, transport, Core, Gravity, or Galaxy unlock",
            "claim_boundary": "Mass-only harmonic isotope sensitivity does not establish Ding material equivalence or source-grade uncertainty. Defect, morphology, isotope-scattering, and TTG response mapping remain separate.",
        },
        "source": {
            "nist_locator": NIST_LOCATOR,
            "isotope_masses_amu": {"12C": 12.0000000, "13C": 13.00335483507},
            "representative_fraction_13C": {"value": 0.0107, "uncertainty": 0.0008},
            "source_note": "NIST representative composition is used for a mass-averaged sensitivity; it is not a measurement of the Ding specimen's isotope ratio.",
        },
        "force_constant_identity": {
            "poscar": record(force_dir / "POSCAR"),
            "fc2": record(force_dir / "fc2.hdf5"),
            "fc3": record(force_dir / "fc3.hdf5"),
            "reused_for_all_states": True,
        },
        "runs": runs,
        "sensitivity": sensitivity_rows,
        "interpretation": {
            "isotope_mass_state_mapped": True,
            "isotope_disorder_scattering_mapped": False,
            "defect_state_mapped": False,
            "morphology_mapped": False,
            "ding_material_equivalence": False,
            "source_grade_uncertainty_closed": False,
            "target_fit_performed": False,
            "alpha_Phi_K_fit_performed": False,
            "holdout_accessed": False,
        },
        "controlling_blocker": "material_regime_mapping_to_TTG_not_closed",
        "next_controller": "Add a source-locked defect/morphology response contract or retain the Calorine route as a non-Ding sensitivity comparator; do not convert the mass-only envelope into source-grade uncertainty.",
        "claim_boundary": "Candidate isotope mass sensitivity only; not Ding C_src acceptance, not a UET Phi map, not alpha_Phi_K calibration, not TTG prediction, and not Full Topic 13 closure.",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    audit_path = output_dir / "t13_calorine_isotope_mass_sensitivity_audit.json"
    audit_path.write_text(json.dumps(audit, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    core_projection_path = ROOT / "docs/core/07_artifacts/topic13/t13_calorine_isotope_mass_sensitivity_audit.json"
    core_projection_path.write_text(json.dumps(audit, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "audit": str(audit_path), "sensitivity": sensitivity_rows}, indent=2))
    uncertainty_path, _ = build_uncertainty_audit(audit, audit_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
