"""Bind four pre-standard Topic 10 research waves without rewriting their results."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOPIC = "docs/topics/0.10_Fluid_Dynamics_Chaos/"
OUT = ROOT / TOPIC / "calculation_contracts"
PLAN = TOPIC + "Data/03_Research/fluid_thermal_joint_research_plan.json"
REGISTRY = "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_o2_gapless_functional_addendum.json"
WAVES = [
    dict(name="gapless_functional", commit="088c8b204dd2dff9f84a15ba1a3ca80b5c0468fb",
         code="Research_Fluid_Core_O2_Gapless_Functional.py", doc="CORE_O2_GAPLESS_FUNCTIONAL_CANDIDATE.md",
         configs=["fluid_core_o2_gapless_functional_contract.json"], result="fluid_core_o2_gapless_functional_audit.json",
         question="Under the declared modified O(2) Hartree-Fock functional, which static algebra and Goldstone identities hold?",
         model="Symmetric coincident tadpole matrix and source-normalized modified gapless Hartree-Fock polynomial; no interacting thermal state is solved.",
         domain="Conditional static O(2) source algebra and declared synthetic controls; natural source units; no material or SI inference.",
         next="Establish finite-density integral-state renormalization and an external source vertex before any physical promotion."),
    dict(name="stationary_source_response", commit="9597fb70057020b6dd63317b7197b4d039b1de72",
         code="Research_Fluid_Core_O2_Stationary_Source_Response.py", doc="CORE_O2_STATIONARY_SOURCE_RESPONSE.md",
         configs=["fluid_core_o2_stationary_source_response_contract.json", "fluid_core_o2_stationary_source_response_registry.json"],
         result="fluid_core_o2_stationary_source_response.json",
         question="Which implicit stationary derivatives and external source-response obligations follow within the declared approximation?",
         model="Conditional stationary source derivatives with distinct internal propagators and external response; no full dynamic vertex is computed.",
         domain="Static source/response identities and specified synthetic controls, subject to the declared invertibility and approximation assumptions.",
         next="Derive and review the external dynamical source vertex and the regulated integral state before physical use."),
    dict(name="material_frame_eos", commit="aab5d2696908b13ae2b13d48c1170056916170d0",
         code="Research_Fluid_Material_Frame_EOS_Handoff.py", doc="MATERIAL_FRAME_EOS_HANDOFF_CONTRACT.md",
         configs=["fluid_material_frame_eos_handoff_contract.json", "fluid_material_frame_eos_handoff_registry.json"],
         result="fluid_material_frame_eos_handoff.json",
         question="What conditional frame and fixed-pressure thermodynamic relations are needed for a material heat/EOS handoff?",
         model="Declared linear frame shift and stationary pressure derivatives with explicit source and covariance prerequisites.",
         domain="Conditional algebraic frame/EOS handoff and synthetic counterexamples; no material values, covariance or SI calibration.",
         next="Obtain a justified material-frame map, physical state, SI scales and independent protocol before comparing heat or EOS."),
    dict(name="matrix_tadpole", commit="3860817e2980dedf86bac2a2c3c25a806ad67ead",
         code="Research_Fluid_Core_O2_Matrix_Tadpole.py", doc="CORE_O2_MATRIX_TADPOLE_CONTRACT.md",
         configs=["fluid_core_o2_matrix_tadpole_contract.json", "fluid_core_o2_matrix_tadpole_registry.json"],
         result="fluid_core_o2_matrix_tadpole.json",
         question="What matrix pole, residue, IR/UV subtraction and auxiliary-state prerequisites follow at finite density?",
         model="Rest-frame stable-domain matrix integrands, declared modified stationary auxiliary functional, and locked synthetic integrand controls.",
         domain="Conditional matrix/IR/UV/source prerequisites only; no thermal integral state, full renormalization or material result.",
         next="Complete the same-functional counterterm/source, regulator and approximation contract before admitting integral-state numerics."),
]


def git(*args: str) -> bytes:
    return subprocess.run(["git", "-c", "core.fsmonitor=false", *args], cwd=ROOT,
                          check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def digest(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def make_contract(wave: dict) -> dict:
    code = TOPIC + "Code/03_Research/" + wave["code"]
    doc = TOPIC + wave["doc"]
    configs = [TOPIC + "Data/03_Research/" + name for name in wave["configs"]]
    result = TOPIC + "Result/artifacts/" + wave["result"]
    historic = [(result, "result")]
    if wave["name"] == "gapless_functional":
        historic.append((REGISTRY, "registry_addendum"))
    identities = []
    for path, role in [(code, "code"), (doc, "evidence"), (PLAN, "config"),
                       *[(p, "config") for p in configs], *[(p, "evidence") for p, _ in historic]]:
        identities.append(dict(path=path, kind="working_file", role=role, sha256=digest((ROOT / path).read_bytes())))
    result_data = json.loads((ROOT / result).read_text(encoding="utf-8"))
    inputs = result_data.get("input_hashes")
    if not isinstance(inputs, dict) or not inputs:
        raise ValueError(f"Historical result has no recorded input hashes: {result}")
    seen = {item["path"] for item in identities}
    for raw_path, expected in sorted(inputs.items()):
        path = raw_path.replace("\\", "/")
        target = (ROOT / path).resolve()
        if not target.is_relative_to(ROOT.resolve()) or not target.is_file():
            raise ValueError(f"Historical input unavailable or outside the repository: {path}")
        raw = target.read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError(f"Historical input hash mismatch: {path}")
        if path not in seen:
            identities.append(dict(path=path, kind="working_file", role="code" if path.endswith(".py") else "input", sha256=digest(raw)))
            seen.add(path)
    for path, _ in historic:
        original = git("show", f"{wave['commit']}:{path}")
        if digest(original) != digest((ROOT / path).read_bytes()):
            raise ValueError(f"Historical artifact differs from its originating commit: {path}")
        identities.append(dict(path=path, kind="git_blob", role="evidence", commit=wave["commit"], sha256=digest(original)))
    evidence = [code, doc, *configs, result]
    groups = [
        ("system_state", "MODELED", "The declared formal state and assumptions are limited to the source model."),
        ("drive_environment", "MODELED", "Only the stated stationary or fixed-control setup is assessed."),
        ("propagation", "NOT_APPLICABLE", "No physical signal transmission is measured in this formal calculation."),
        ("frame_time", "MODELED", "Only the frame and time conventions in the named source calculation apply."),
        ("detector", "NOT_APPLICABLE", "No physical detector or measurement outcome is claimed."),
        ("processing", "MODELED", "Algebra and controls use the named frozen input and implementation."),
        ("numerics", "MODELED", "Numerical controls and tolerances are the ones recorded in the original source contract."),
    ]
    components = [dict(id=group, group=group, disposition=disposition, reason=reason,
                       evidence=[code, doc] if disposition == "MODELED" else []) for group, disposition, reason in groups]
    components.append(dict(id="physical_correspondence", group="system_state", disposition="UNKNOWN",
                           reason="Material correspondence and the physical state are not admitted by this formal wave.",
                           evidence=[doc], owner="theory author and relevant domain reviewer", next_action=wave["next"]))
    return dict(schema_version="uet-calculation-contract-v1", contract_id="T10_HISTORICAL_" + wave["name"].upper(),
        profile="FORMAL", review=dict(status="INCOMPLETE", reviewer="agent:historical-lineage-reconciliation",
            rationale="Historical source identity and stated scope only; no independent scientific review or physical acceptance."),
        question=wave["question"], output=dict(quantity="Conditional algebraic identities and recorded synthetic controls",
            unit="natural source units or dimensionless residuals as defined per expression", domain=wave["domain"],
            accuracy="Exact symbolic checks and the original source-contract numerical tolerances; no empirical uncertainty.", claim_intent="DIAGNOSTIC"),
        model=dict(formula_ids=[wave["doc"]], assumptions=wave["model"], approximation=wave["model"],
            initial_boundary="Stationary or fixed controls only as stated in the cited source; no general dynamical initial-value claim.",
            drive_environment="Declared fixed or stationary model controls; no physical bath or material protocol is inferred.",
            parameters="Original source-contract synthetic controls; physical scales and material covariance remain unassigned."),
        data_policy=dict(uses_observations=False, calibration_ids=[], comparison_ids=[], independent_validation=False,
            holdout_policy="No observational fit or independent experimental validation is claimed."),
        observation=dict(source_state=wave["model"], generated_trace="No physical dissipation trace is inferred.",
            carrier="No physical signal transport is modeled.", observer_state="No detector is modeled.",
            readout="Symbolic identities and fixed synthetic controls only.", backaction="No measurement is claimed; real detector backaction is not assumed zero.",
            frame="Only the frame explicitly stated by the source calculation.", time_convention="Stationary or fixed-control scope as stated; no general dynamics inferred.",
            product_level="Historical formal/diagnostic artifact; not a material measurement.", corrections=[]),
        components=components, error_budget=dict(unit="natural source units or dimensionless residuals as defined per expression",
            numerical="Use original synthetic-control tolerances and exact symbolic identities.", approximation=wave["model"],
            measurement="No physical measurement is analyzed.", systematic="Physical correspondence and full method error are not established.",
            omissions="Unmodeled physical state, material mapping and empirical uncertainty remain open.",
            dependence="No independence of unknown physical errors is assumed.", acceptance="Historical diagnostic only; no physical acceptance threshold.", omission_limit=None),
        identities=identities, entrypoints=[code], evidence=evidence,
        claim_boundary="Conditional formal source algebra and synthetic controls only; all original physical and claim-promotion gates remain unchanged.",
        next_action=wave["next"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        OUT.mkdir(parents=True, exist_ok=True)
    for wave in WAVES:
        path = OUT / ("historical_" + wave["name"] + ".json")
        rendered = json.dumps(make_contract(wave), indent=2, ensure_ascii=False) + "\n"
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != rendered:
                raise SystemExit(f"Historical contract differs: {path}")
        else:
            path.write_text(rendered, encoding="utf-8", newline="\n")
        print(path.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
