#!/usr/bin/env python
"""
UET Simple CLI - ใช้งานง่ายๆ!

Usage:
  python uet.py run              # รัน simulation ง่ายๆ
  python uet.py run --preset coffee   # รันด้วย preset
  python uet.py list             # ดู runs ทั้งหมด
  python uet.py show <run_name>  # ดูผลลัพธ์
  python uet.py plot <run_name>  # plot ผลลัพธ์
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Presets for easy use
PRESETS = {
    "default": {
        "model": "C_only",
        "params": "V=quartic(a=-1,delta=1,s=0),kappa=0.5",
        "T": 1.0, "N": 64, "dt": 0.01
    },
    "coffee": {
        "model": "C_I",
        "params": "VC=quartic(a=-1,delta=1,s=0),VI=quartic(a=-1,delta=1,s=0),kC=0.5,kI=0.5,beta=0.3",
        "T": 2.0, "N": 64, "dt": 0.005
    },
    "symmetric": {
        "model": "C_I",
        "params": "VC=quartic(a=-1,delta=1,s=0),VI=quartic(a=-1,delta=1,s=0),kC=1,kI=1,beta=0.5",
        "T": 2.0, "N": 64, "dt": 0.01
    },
    "strong": {
        "model": "C_I",
        "params": "VC=quartic(a=-1,delta=1,s=0),VI=quartic(a=-1,delta=1,s=0),kC=1,kI=1,beta=0.9",
        "T": 2.0, "N": 64, "dt": 0.005
    },
    "weak": {
        "model": "C_I",
        "params": "VC=quartic(a=-1,delta=1,s=0),VI=quartic(a=-1,delta=1,s=0),kC=1,kI=1,beta=0.1",
        "T": 2.0, "N": 64, "dt": 0.01
    },
}

def cmd_run(args):
    """Run a simulation"""
    preset = PRESETS.get(args.preset, PRESETS["default"])
    
    case_id = args.name or f"run_{args.preset}"
    out_dir = f"runs/{case_id}"
    
    cmd = [
        sys.executable, "scripts/run_case.py",
        "--case_id", case_id,
        "--model", preset["model"],
        "--params", preset["params"],
        "--T", str(preset["T"]),
        "--N", str(preset["N"]),
        "--dt", str(preset["dt"]),
        "--out", out_dir
    ]
    
    print(f"🚀 Running: {case_id}")
    print(f"   Preset: {args.preset}")
    print(f"   Output: {out_dir}")
    print()
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode

def cmd_list(args):
    """List all runs"""
    runs_dir = Path(__file__).parent / "runs"
    if not runs_dir.exists():
        print("❌ No runs folder found")
        return 1
    
    runs = sorted([d.name for d in runs_dir.iterdir() if d.is_dir()])
    
    print(f"📁 Found {len(runs)} runs in 'runs/':\n")
    
    for run in runs:
        summary_file = runs_dir / run / "summary.json"
        if summary_file.exists():
            with open(summary_file) as f:
                summary = json.load(f)
            status = summary.get("status", "?")
            icon = "✅" if status == "PASS" else "⚠️" if status == "WARN" else "❌"
            print(f"  {icon} {run} [{status}]")
        else:
            print(f"  📂 {run}")
    
    return 0

def cmd_show(args):
    """Show run details"""
    runs_dir = Path(__file__).parent / "runs"
    run_dir = runs_dir / args.name
    
    if not run_dir.exists():
        print(f"❌ Run not found: {args.name}")
        return 1
    
    summary_file = run_dir / "summary.json"
    if summary_file.exists():
        with open(summary_file) as f:
            summary = json.load(f)
        print(f"📊 Summary for '{args.name}':\n")
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(f"⚠️ No summary.json found in {run_dir}")
    
    return 0

def cmd_plot(args):
    """Plot run results"""
    runs_dir = Path(__file__).parent / "runs"
    run_dir = runs_dir / args.name
    
    if not run_dir.exists():
        print(f"❌ Run not found: {args.name}")
        return 1
    
    cmd = [sys.executable, "scripts/plot_run.py", str(run_dir)]
    print(f"📈 Plotting: {args.name}")
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode

def cmd_presets(args):
    """Show available presets"""
    print("🎛️ Available presets:\n")
    for name, preset in PRESETS.items():
        print(f"  📌 {name}")
        print(f"     Model: {preset['model']}")
        print(f"     T={preset['T']}, N={preset['N']}, dt={preset['dt']}")
        print()
    return 0

def main():
    parser = argparse.ArgumentParser(
        description="🧮 UET Simple CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python uet.py run                    # Run default simulation
  python uet.py run --preset coffee    # Run coffee preset
  python uet.py run --preset strong --name my_test
  python uet.py list                   # List all runs
  python uet.py show my_test           # Show run details
  python uet.py presets                # Show available presets
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # run
    run_parser = subparsers.add_parser("run", help="Run a simulation")
    run_parser.add_argument("--preset", default="default", choices=list(PRESETS.keys()),
                           help="Preset to use")
    run_parser.add_argument("--name", help="Custom name for the run")
    
    # list
    subparsers.add_parser("list", help="List all runs")
    
    # show
    show_parser = subparsers.add_parser("show", help="Show run details")
    show_parser.add_argument("name", help="Run name")
    
    # plot
    plot_parser = subparsers.add_parser("plot", help="Plot run results")
    plot_parser.add_argument("name", help="Run name")
    
    # presets
    subparsers.add_parser("presets", help="Show available presets")
    
    args = parser.parse_args()
    
    if args.command == "run":
        return cmd_run(args)
    elif args.command == "list":
        return cmd_list(args)
    elif args.command == "show":
        return cmd_show(args)
    elif args.command == "plot":
        return cmd_plot(args)
    elif args.command == "presets":
        return cmd_presets(args)
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())
