"""Independent fixed-Phi spectrum witnesses and scoped downstream review inventory.

All numeric inputs are synthetic. The inventory reads Python source only; it
does not open experimental payloads or imply that every importer is incorrect.
Run as a module from the repository root.
"""

from __future__ import annotations

import ast
import hashlib
import json
from math import exp, pi, sqrt
from pathlib import Path

import numpy as np
from scipy.integrate import quad

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    o2_equilibrium_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
    condensed_quasiparticle_energies,
    finite_temperature_o2_quasiparticle_contract,
    finite_temperature_o2_state,
    quasiparticle_pressure,
)
from docs.core.uet_o2_formal_transverse_response import (
    formal_transverse_quasiparticle_response,
)

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_fixed_phi_spectrum_repair_audit.json"
EOS_PATH = "docs/core/uet_o2_finite_temperature_quasiparticle_eos.py"
STATIC_PATH = "docs/core/uet_o2_formal_transverse_response.py"
AUDIT_PATH = "docs/scripts/audit/audit_topic13_fixed_phi_spectrum_repair.py"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def config(z=1.0, mass_sq=None, quartic=1.0):
    return FiniteTemperatureO2QuasiparticleConfig(
        eos=O2FiniteDensityEOSConfig(matter=CovariantMatterConfig(
            matter_kinetic=z,
            matter_mass_sq=z if mass_sq is None else mass_sq,
            matter_quartic=quartic,
            response_coupling=0.0,
        )),
        quadrature_order=192,
    )


def fixed_phi_witnesses() -> dict:
    """Check independent action eigenvalues, EOS sound, and normal enthalpy."""
    spectra, sound, normal, rescaling = [], [], [], []
    mu = sqrt(3.0)
    for z in (0.25, 1.0, 4.0):
        cfg = config(z)
        q = z * mu**2 - z
        for k in (0.0, 1e-8, 1e-4, 0.1, 1.0, 5.0):
            # Real linearized action generator, not the implemented root formula.
            generator = np.array([
                [0., 0., 1., 0.], [0., 0., 0., 1.],
                [-k*k-2*q/z, 0., 0., -2*mu],
                [0., -k*k, 2*mu, 0.],
            ])
            eigenvalues = np.linalg.eigvals(generator)
            expected = np.sort(eigenvalues.imag**2)
            upper, lower = condensed_quasiparticle_energies(k, mu, 0., cfg)
            actual = np.array([lower**2, lower**2, upper**2, upper**2])
            spectra.append({
                "Z": z, "k": k,
                "max_squared_frequency_error": float(np.max(abs(actual-expected))),
                "pass": bool(
                    np.max(abs(eigenvalues.real)) < 1e-10
                    and np.allclose(actual, expected, rtol=1e-10, atol=1e-11)
                ),
            })
        eos_sound = o2_equilibrium_state(mu, 0., cfg.eos).sound_speed_sq
        for k in (1e-5, 1e-8, 1e-10):
            lower = condensed_quasiparticle_energies(k, mu, 0., cfg)[1]
            sound.append({
                "Z": z, "k": k, "mode_c_squared": (lower/k)**2,
                "eos_c_squared": eos_sound,
                "pass": bool(lower > 0. and np.isclose(
                    (lower/k)**2, eos_sound, rtol=1e-8, atol=0.
                )),
            })

        t, normal_mu = .25, .2
        state = finite_temperature_o2_state(t, normal_mu, 0., cfg)
        response = formal_transverse_quasiparticle_response(t, normal_mu, 0., cfg)

        def integrand(k):
            energy = sqrt(k*k+1.)
            value = 0.
            for sign in (-1., 1.):
                weight = exp(-(energy+sign*normal_mu)/t)
                value += weight/(1.-weight)**2/t
            return k**4*value/(6*pi*pi)

        independent, error = quad(integrand, 0., np.inf, epsabs=1e-13)
        chi = response.normal_momentum_susceptibility
        enthalpy = state.energy_density + state.pressure
        normal.append({
            "Z": z, "static_chi": chi, "independent_integral": independent,
            "quadrature_error_estimate": error, "eos_enthalpy": enthalpy,
            "enthalpy_relative_error": abs(chi/enthalpy-1),
            "pass": bool(
                error < 1e-11
                and np.isclose(chi, independent, rtol=1e-9, atol=1e-13)
                and np.isclose(chi, enthalpy, rtol=2e-6, atol=0.)
            ),
        })

    for t, chemical_potential in ((.25, .2), (.15, mu)):
        original, canonical = config(4., 4., 1.), config(1., 1., 1./16)
        pressures = [quasiparticle_pressure(t, chemical_potential, 0., cfg)
                     for cfg in (original, canonical)]
        responses = [formal_transverse_quasiparticle_response(
            t, chemical_potential, 0., cfg
        ) for cfg in (original, canonical)]
        chi = [row.normal_momentum_susceptibility for row in responses]
        rescaling.append({
            "T": t, "mu": chemical_potential, "pressure_pair": pressures,
            "chi_pair": chi,
            "pass": bool(
                np.isclose(*pressures, rtol=1e-11, atol=0.)
                and np.isclose(*chi, rtol=1e-10, atol=0.)
                and np.isclose(
                    responses[0].condensate_phase_stiffness,
                    responses[1].condensate_phase_stiffness,
                    rtol=1e-12, atol=0.,
                )
            ),
        })
    gap = condensed_quasiparticle_energies(0., mu, 0., config())[0]**2
    return {
        "checks": {
            "independent_action_spectrum": all(row["pass"] for row in spectra),
            "small_momentum_sound_without_clipping": all(row["pass"] for row in sound),
            "normal_integral_and_enthalpy": all(row["pass"] for row in normal),
            "canonical_field_covariance": all(row["pass"] for row in rescaling),
            "corrected_gap_squared": bool(np.isclose(gap, 16., rtol=1e-12)),
        },
        "spectrum_rows": spectra,
        "sound_rows": sound,
        "normal_response_rows": normal,
        "rescaling_rows": rescaling,
        "gap_witness": {
            "Z": 1., "m_eff_squared": 1., "mu_squared": 3.,
            "old_gap_squared": 20., "corrected_gap_squared": gap,
            "old_sound_squared": .4, "corrected_sound_squared": .25,
            "old_formula_role": "DEFECT_WITNESS_ONLY_NOT_AN_ACCEPTED_BASELINE",
        },
    }


def consumer_inventory(root: Path = ROOT) -> dict:
    """Static import reachability only, including imports inside functions."""
    paths = sorted(set(
        (root / "docs/core").glob("*.py")
    ) | set((root / "docs/scripts/audit").glob("*.py")))
    modules, imports, errors = {}, {}, []
    for path in paths:
        relative = path.relative_to(root)
        name = ".".join(relative.with_suffix("").parts)
        modules[name] = relative.as_posix()
        try:
            tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        except (SyntaxError, UnicodeError) as error:
            errors.append({"path": relative.as_posix(), "error": str(error)})
            continue
        dependencies = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                dependencies.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    package = name.split(".")[:-node.level]
                    base = ".".join(package + ([node.module] if node.module else []))
                else:
                    base = node.module or ""
                dependencies.add(base)
                dependencies.update(base+"."+alias.name for alias in node.names)
        imports[name] = dependencies

    seeds = {EOS_PATH[:-3].replace("/", "."), STATIC_PATH[:-3].replace("/", ".")}
    affected = set(seeds)
    while True:
        grown = affected | {name for name, deps in imports.items() if deps & affected}
        if grown == affected:
            break
        affected = grown
    rows = [
        {
            "path": modules[name],
            "relationship": "DIRECT" if imports[name] & seeds else "TRANSITIVE",
            "affected_imports": sorted(imports[name] & affected),
            "disposition": "REVIEW_REQUIRED_NOT_AUTOMATIC_NUMERIC_FAILURE",
        }
        for name in sorted(affected-seeds) if name in imports
    ]
    return {
        "method": "STATIC_PYTHON_IMPORT_REACHABILITY",
        "scope": ["docs/core/*.py", "docs/scripts/audit/*.py"],
        "does_not_cover": "dynamic imports, copied formulas, non-Python artifact dependency edges",
        "experimental_payloads_read": False,
        "parse_errors": errors,
        "scanned_python_file_count": len(paths),
        "review_required": rows,
        "source_snapshot_sha256": {
            modules[name]: digest(root / modules[name]) for name in sorted(affected)
            if name in modules
        },
    }


def main() -> int:
    witnesses = fixed_phi_witnesses()
    inventory = consumer_inventory()
    passed = all(witnesses["checks"].values()) and not inventory["parse_errors"]
    primary = ROOT / "docs/core/artifacts/t13_uet_o2_finite_temperature_quasiparticle_eos_audit.json"
    primary_data = json.loads(primary.read_text(encoding="utf-8"))
    fresh = (
        primary_data.get("contract", {}).get("spectrum_revision") == "FIXED_PHI_CANONICAL_V2"
        and primary_data.get("source_hashes", {}).get(EOS_PATH) == digest(ROOT / EOS_PATH)
        and primary_data.get("source_hashes", {}).get(STATIC_PATH) == digest(ROOT / STATIC_PATH)
        and primary_data.get("source_hashes", {}).get(AUDIT_PATH) == digest(ROOT / AUDIT_PATH)
        and primary_data.get("status") == "PASS_ACTION_DERIVED_TREE_CONDENSATE_THERMAL_QUASIPARTICLE_EOS"
        and bool(primary_data.get("checks"))
        and all(primary_data["checks"].values())
    )
    passed = passed and fresh
    contract = finite_temperature_o2_quasiparticle_contract()
    source_paths = [
        EOS_PATH, STATIC_PATH, AUDIT_PATH,
        "docs/core/uet_covariant_matter.py",
        "docs/core/uet_o2_finite_density_eos.py",
        "docs/core/test/test_topic13_fixed_phi_spectrum_regression.py",
    ]
    artifact = {
        "schema_version": "t13-fixed-phi-spectrum-repair-v1",
        "major_result_id": "T13_FIXED_PHI_EOS_STATIC_RESPONSE_REPAIR",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
        "verification_status": "PASS_SCOPED_IMPLEMENTATION_REPAIR" if passed else "BLOCKED_REPAIR",
        "what_is_closed": [
            "Fixed-Phi action spectrum and small-k EOS sound agreement on the declared grid.",
            "Canonical field covariance of pressure and static momentum response.",
            "Normal ideal-gas static response matches independent integral and enthalpy.",
        ] if passed else [],
        "equation_or_mapping": contract["equations"],
        "units": contract["unit_contract"],
        "derivation_class": "EXISTING_ACTION_IMPLEMENTATION_REPAIR_NOT_NEW_EQUATION",
        "observable": "natural-unit mode energies, pressure and static momentum susceptibility",
        "data_role": "SYNTHETIC_REGRESSION_NOT_MATERIAL_CALIBRATION",
        "evidence_artifacts": [{"path": primary.relative_to(ROOT).as_posix(), "sha256": digest(primary)}],
        "source_hashes": {path: digest(ROOT / path) for path in source_paths},
        "baseline": {
            "git_revision": "5946ce9c3",
            "eos_git_blob": "dee3df6f34b36e784cf5b998eae4693268384fd2",
            "eos_sha256": "7a3b97bce24ac89593b6031adc65db8f18d33780565afcad016fd9b97cefe41e",
            "primary_artifact_sha256": "6a8e9124d8574fa534c6377646f01e5324715477ff0595bcf04657ad9919538b",
            "disposition": "SUPERSEDED_FOR_FIXED_PHI_SPECTRUM; preserved in git, not deleted",
        },
        "witnesses": witnesses,
        "primary_artifact_fresh": fresh,
        "downstream_review": inventory,
        "impact_boundary": {
            "condensed": "Recompute spectrum-dependent values; old positivity-only PASS is insufficient.",
            "normal_Z_not_one": "Recompute EOS and static response with canonical mass and unscaled mu.",
            "normal_Z_one": "Dispersion unchanged; thermal-log precision changed. Do not discard physical anchors by association.",
            "live_Phi": "Separate three-mode calculation; not replaced by this two-mode repair.",
            "global_acceptance": "Not regenerated; bounded He4 composition is not evidence of full thermodynamic closure.",
        },
        "known_unrepaired_copied_formula": {
            "path": "docs/core/uet_o2_kinetic_collision_kubo.py",
            "symbol": "_normal_state_inputs",
            "source_sha256": digest(ROOT / "docs/core/uet_o2_kinetic_collision_kubo.py"),
            "finding": "Normal kinetic setup still uses sqrt(Z)*abs(mu); audit its mass and vertex normalization before general-Z transport use.",
            "disposition": "OPEN_GENERAL_Z_KINETIC_NORMALIZATION_REVIEW",
        },
        "open_blockers": [
            "downstream_spectrum_dependent_artifact_refresh_and_formula_review",
            "full_current_condensate_material_matching",
            "full_thermal_transport_SK_KMS_and_physical_mapping",
            "full_acceptance_scope_repair",
        ],
        "dependency_unlocked": [],
        "full_core_unlock": False,
        "claim_promotion": False,
        "parameter_fitting_performed": False,
        "xie_2026_accessed": False,
        "input_access_boundary": "Synthetic points, Python code, import-time package/release metadata and the named EOS audit JSON; no experimental payload.",
        "controlling_blocker": "downstream_spectrum_and_copied_kinetic_normalization_review",
        "next_action": "Audit general-Z kinetic mass, chemical potential and vertex normalization; refresh only impacted results and repair full-acceptance scope.",
        "claim_boundary": "Fixed-Phi implementation repair only; not live-Phi closure, SI conductivity, full two-fluid transport, Full Topic 13 or external validation.",
    }
    artifact["report"] = {
        "MAJOR_RESULT_CLOSURE": artifact["closure_level"],
        "WHAT_IS_ACTUALLY_CLOSED": artifact["what_is_closed"],
        "WHAT_REMAINS_OPEN": artifact["open_blockers"],
        "DEPENDENCY_UNLOCKED": artifact["dependency_unlocked"],
        "STATUS": artifact["verification_status"],
        "WHAT_CHANGED": "Corrected fixed-Phi spectrum and static response; preserved old EOS identity and inventoried downstream importers.",
        "EQUATION_OR_MAPPING": artifact["equation_or_mapping"],
        "VERIFICATION": witnesses["checks"],
        "CONTROLLING_BLOCKER": artifact["controlling_blocker"],
        "NEXT_ACTION": artifact["next_action"],
        "CLAIM_BOUNDARY": artifact["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps({
        "status": artifact["verification_status"],
        "checks": witnesses["checks"], "primary_fresh": fresh,
        "consumer_review_count": len(inventory["review_required"]),
        "parse_errors": inventory["parse_errors"], "full_core_unlock": False,
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
