# run_preset.py – helper to run a preset JSON through the UET harness and record metrics

"""Execute a preset configuration file.

Usage:
    python scripts/run_preset.py --preset <preset_name>

The script loads the JSON file from the `presets/` directory, builds the full
configuration dictionary expected by `run_case`, injects the `run_dir` so that the
solver can record metrics, and then executes the simulation.
"""

import argparse
import json
from pathlib import Path
import sys

from uet_core.parser import parse_case_params
from uet_core.solver import run_case, StrictSettings
from uet_core.logging import init_run_folder, write_meta, write_timeseries, write_summary
from uet_core.validation import run_gates
from uet_core.feedback import analyze_run


def load_preset(preset_name: str) -> dict:
    preset_path = Path(__file__).parent.parent / "presets" / f"{preset_name}.json"
    if not preset_path.is_file():
        raise FileNotFoundError(f"Preset '{preset_name}' not found at {preset_path}")
    with open(preset_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_config(preset: dict, case_id: str) -> dict:
    # Build params string for the parser
    eq_params = preset["equations"]["params"]
    model = preset["world"]["model"]
    
    if model == "C_only":
        # Expects: kappa=X, M=Y, V=quartic(...)
        params_str = f"kappa={eq_params.get('kappa', 1)}, M={eq_params.get('M', 1)}, V={eq_params['potential']}"
    else: # C_I
        # Expects: kC=X, kI=Y, MC=Z, MI=W, beta=B, VC=quartic(...), VI=quartic(...)
        # We handle both single 'potential' (shared) or separate 'potentialC'/'potentialI'
        pC = eq_params.get("potentialC", eq_params.get("potential"))
        pI = eq_params.get("potentialI", eq_params.get("potential"))
        params_str = (
            f"kC={eq_params.get('kC', 1)}, kI={eq_params.get('kI', 1)}, "
            f"MC={eq_params.get('MC', 1)}, MI={eq_params.get('MI', 1)}, "
            f"beta={eq_params.get('beta', 0.5)}, "
            f"VC={pC}, VI={pI}"
        )

    # Basic scaffold – mirrors the CLI construction in scripts/run_case.py
    cfg = {
        "case_id": case_id,
        "model": model,
        "units": {"mode": "dimensionless"},
        "domain": {"dim": 2, "L": preset["world"]["domain"], "bc": "periodic"},
        "grid": {"N": preset["world"]["grid"], "dtype": "float64"},
        "time": {
            "dt": preset["run"]["dt"] if "dt" in preset["run"] else 5e-4,
            "T": preset["run"].get("T", 0.2),
            "max_steps": preset["run"].get("steps", 200000),
            "tol_abs": 1e-10,
            "tol_rel": 1e-10,
            "backtrack": {"enabled": True, "factor": 0.5, "max_backtracks": 20},
        },
        "integrator": {"name": "semiimplicit", "mode": "strict"},
        "rng": {"seed": preset["run"].get("seed", 0), "algorithm": "numpy_pc64"},
        "params": parse_case_params(model, params_str),
    }
    return cfg


def main():
    parser = argparse.ArgumentParser(description="Run a preset through the UET harness")
    parser.add_argument("--preset", required=True, help="Name of the preset JSON (without .json)")
    parser.add_argument("--case_id", default="preset_run", help="Identifier for this run")
    parser.add_argument("--out", default="runs", help="Root output directory")
    args = parser.parse_args()

    try:
        preset = load_preset(args.preset)
    except Exception as e:
        print(f"Error loading preset: {e}")
        sys.exit(1)

    config = build_config(preset, args.case_id)

    # Initialise run folder (creates runs/<model>/<case_id>/<run_id>)
    out_root = Path(args.out)
    run_dir, run_id, cfg_hash = init_run_folder(out_root, config["model"], config["case_id"], config)
    config["run_dir"] = str(run_dir)  # make available to solver for metric recording
    config["run_id"] = run_id
    config["config_hash"] = cfg_hash

    meta = write_meta(run_dir, code_hash="uet_harness_v0.1")
    config["code_hash"] = meta["code_hash"]

    rng = __import__("numpy").random.default_rng(config["rng"]["seed"])

    t0 = __import__("time").time()
    summary, rows = run_case(config, rng, strict=StrictSettings())
    summary["fail_code"] = summary.get("status", "FAIL")
    summary["runtime_s"] = __import__("time").time() - t0
    summary["run_id"] = run_id
    summary["config_hash"] = cfg_hash
    summary["code_hash"] = meta["code_hash"]

    write_timeseries(run_dir, rows)
    write_summary(run_dir, summary)

    # Run validation gates automatically
    print("\nRunning Validation Gates...")
    run_gates(run_dir)

    # 5. Feedback Analysis
    from uet_core.feedback import analyze_run
    analyze_run(run_dir)
    
    # 6. Generate Static Report (Server-free Dashboard)
    from uet_core.export import export_static_dashboard
    export_static_dashboard(run_dir)

    # 7. Update Unified Studio Hub
    from uet_core.index_gen import generate_studio_hub
    print("Updating UET Studio Hub...")
    generate_studio_hub()
    
    print(f"\n[Done] All checks passed. Results in {run_dir}")


if __name__ == "__main__":
    main()
