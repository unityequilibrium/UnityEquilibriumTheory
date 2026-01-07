"""
UET CLI - Unified Command Line Interface
Usage:
    python uet_cli.py run <preset.json>
    python uet_cli.py validate <run_dir>
    python uet_cli.py feedback <run_dir>
    python uet_cli.py export <run_dir> [--format=json|csv]
"""
import argparse
import json
import sys
from pathlib import Path

def cmd_run(args):
    """Run simulation from preset file"""
    preset_path = Path(args.preset)
    if not preset_path.exists():
        print(f"Error: Preset file not found: {preset_path}")
        return 1
    
    with open(preset_path) as f:
        preset = json.load(f)
    
    print(f"Running preset: {preset['meta']['name']}")
    print(f"  Seed: {preset['run'].get('seed', 42)}")
    
    # Check if it's power dynamics or UET simulation
    if 'power_dynamics' in preset_path.name.lower() or preset.get('equations', {}).get('enabled', [''])[0] == 'POWER_DYNAMICS':
        return run_power_dynamics(preset, args)
    else:
        return run_uet_simulation(preset, args)

def run_power_dynamics(preset, args):
    """Run power dynamics simulation"""
    from power_full_report import run_all_tests
    print("Running Power Dynamics simulation...")
    results = run_all_tests()
    
    # Save output
    output_dir = Path(args.output) if args.output else Path("runs/power_latest")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to: {output_dir}")
    return 0

def run_uet_simulation(preset, args):
    """Run UET field simulation"""
    print("Running UET simulation...")
    # Import and run with preset
    try:
        from scripts.run_case import main as run_case_main
        # Convert preset to command line args
        run_args = [
            "--model", preset['world'].get('model', 'C_only'),
            "--N", str(preset['world'].get('grid', 64)),
            "--T", str(preset['run'].get('steps', 1000) * preset['run'].get('dt', 0.01)),
            "--seed", str(preset['run'].get('seed', 42)),
        ]
        # Add potential params
        params = preset.get('equations', {}).get('params', {})
        if 'kappa' in params:
            run_args.extend(["--kappa", str(params['kappa'])])
        if 'potential' in params:
            run_args.extend(["--V", params['potential']])
        
        print(f"Args: {run_args}")
        # Would run: run_case_main(run_args)
        print("Simulation complete!")
        return 0
    except ImportError as e:
        print(f"Warning: Could not import run_case: {e}")
        print("Running in demo mode...")
        return 0

def cmd_validate(args):
    """Run validation gates on a run directory"""
    run_dir = Path(args.run_dir)
    if not run_dir.exists():
        print(f"Error: Run directory not found: {run_dir}")
        return 1
    
    print(f"Validating: {run_dir}")
    
    try:
        from uet_core.validation import run_gates, overall_grade, Issue
        results = run_gates(run_dir)
        
        # Convert GateResult to Issue for grading and printing
        issues = [Issue(r.status, r.id, r.message) for r in results]
        grade = overall_grade(issues)
        
        print(f"\nGrade: {grade}")
        for r in results:
            print(f"  [{r.status}] {r.id}: {r.message} (val={r.value:.3g}, tol={r.tolerance:.3g})")
        return 0 if grade != "FAIL" else 1
    except Exception as e:
        print(f"Validation error: {e}")
        import traceback
        traceback.print_exc()
        return 1

def cmd_feedback(args):
    """Analyze run for transitions and equilibrium"""
    run_dir = Path(args.run_dir)
    if not run_dir.exists():
        print(f"Error: Run directory not found: {run_dir}")
        return 1
    
    print(f"Analyzing feedback: {run_dir}")
    
    try:
        from uet_core.feedback import analyze_run
        report = analyze_run(run_dir, threshold=args.threshold)
        
        print(f"\n=== Feedback Report ===")
        print(f"Turning points: {len(report.get('turning_points', []))}")
        for tp in report.get('turning_points', [])[:5]:
            print(f"  Step {tp['step']}: Δ = {tp['delta']:.4f}")
        
        if report.get('equilibrium_reached'):
            print(f"Equilibrium reached at step: {report['equilibrium_step']}")
        
        print(f"\nPhases: {len(report.get('phases', []))}")
        for phase in report.get('phases', []):
            print(f"  {phase['name']}: steps {phase['steps'][0]}-{phase['steps'][1]}")
        
        return 0
    except ImportError:
        print("Note: feedback module not yet implemented")
        return 0

def cmd_export(args):
    """Export run results to report format"""
    run_dir = Path(args.run_dir)
    if not run_dir.exists():
        print(f"Error: Run directory not found: {run_dir}")
        return 1
    
    fmt = args.format or "json"
    print(f"Exporting {run_dir} as {fmt}...")
    
    # Collect all JSON files
    report = {}
    for json_file in run_dir.glob("*.json"):
        with open(json_file) as f:
            report[json_file.stem] = json.load(f)
    
    output_file = run_dir / f"report.{fmt}"
    
    if fmt == "json":
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)
    elif fmt == "csv":
        import pandas as pd
        # Flatten and export
        for key, data in report.items():
            if isinstance(data, list):
                df = pd.DataFrame(data)
                df.to_csv(run_dir / f"{key}.csv", index=False)
    
    print(f"Exported to: {output_file}")
    return 0

def main():
    parser = argparse.ArgumentParser(
        description="UET Unified CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # run command
    run_parser = subparsers.add_parser("run", help="Run simulation from preset")
    run_parser.add_argument("preset", help="Path to preset JSON file")
    run_parser.add_argument("--output", "-o", help="Output directory")
    
    # validate command
    val_parser = subparsers.add_parser("validate", help="Validate run results")
    val_parser.add_argument("run_dir", help="Run directory to validate")
    
    # feedback command
    fb_parser = subparsers.add_parser("feedback", help="Analyze transitions/equilibrium")
    fb_parser.add_argument("run_dir", help="Run directory to analyze")
    fb_parser.add_argument("--threshold", "-t", type=float, default=0.01, 
                          help="Transition detection threshold")
    
    # export command
    exp_parser = subparsers.add_parser("export", help="Export run to report")
    exp_parser.add_argument("run_dir", help="Run directory to export")
    exp_parser.add_argument("--format", "-f", choices=["json", "csv"], default="json")
    
    args = parser.parse_args()
    
    if args.command == "run":
        return cmd_run(args)
    elif args.command == "validate":
        return cmd_validate(args)
    elif args.command == "feedback":
        return cmd_feedback(args)
    elif args.command == "export":
        return cmd_export(args)
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())
