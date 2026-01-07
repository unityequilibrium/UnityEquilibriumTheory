"""
Standalone script to generate a static dashboard for an existing run.
Usage:
    python scripts/make_static_report.py <run_dir>
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from uet_core.export import export_static_dashboard

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/make_static_report.py <run_dir>")
        sys.exit(1)
        
    run_dir = sys.argv[1]
    if not os.path.isdir(run_dir):
        print(f"Error: Directory not found: {run_dir}")
        sys.exit(1)
        
    print(f"Generating static dashboard for: {run_dir}")
    export_static_dashboard(run_dir)
    print("Done!")

if __name__ == "__main__":
    main()
