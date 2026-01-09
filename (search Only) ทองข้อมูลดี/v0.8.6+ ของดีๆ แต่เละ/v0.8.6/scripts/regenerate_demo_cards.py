#!/usr/bin/env python
"""Regenerate all demo cards with proper parameters."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from uet_min_pack.uet_core.demo_card_generator import generate_demo_card

base = Path("runs_gallery")

# All physics/GR demos that need demo cards
demos = [
    "einstein_wave", "einstein_collapse", "einstein_binary",
    "gr_realistic_wave", "gr_realistic_collapse", "gr_realistic_binary", 
    "nr_wave", "nr_collapse", "nr_binary",
    "cosmological_constant", "galaxy_rotation_dm", "landscape_comparison"
]

print("🔄 Regenerating demo cards...")

for demo in demos:
    demo_dir = base / demo
    if demo_dir.exists():
        try:
            generate_demo_card(demo_dir)
            print(f"  ✅ {demo}")
        except Exception as e:
            print(f"  ❌ {demo}: {e}")
    else:
        print(f"  ⚠️ {demo}: not found")

print("\n✅ Done! Refresh browser to see changes.")
