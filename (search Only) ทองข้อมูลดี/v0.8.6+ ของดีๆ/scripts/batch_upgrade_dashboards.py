"""
Batch upgrade script to generate static dashboards for all existing runs.
"""
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from uet_core.export import export_static_dashboard

def batch_upgrade(runs_root):
    root_path = Path(runs_root)
    count = 0
    
    print(f"Scanning {root_path} for runs...")
    
    # 2. Look for ANY folder with config.json or summary.json
    found_dirs = set()
    for pattern in ["config.json", "summary.json"]:
        for path in root_path.rglob(pattern):
            found_dirs.add(path.parent)
            
    for run_dir in found_dirs:
        print(f"Upgrading: {run_dir}")
        try:
            export_static_dashboard(str(run_dir))
            count += 1
        except Exception as e:
            print(f"Failed to upgrade {run_dir}: {e}")
            
    print(f"\n[Done] Upgraded {count} runs with static dashboards.")

if __name__ == "__main__":
    runs_dir = Path(__file__).parent.parent / "runs"
    batch_upgrade(runs_dir)
