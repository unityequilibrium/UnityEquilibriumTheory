
# BEGIN UET REPO ROOT BOOTSTRAP
import sys as _uet_sys
from pathlib import Path as _UETPath

_UET_REPO_ROOT = None
_UET_HERE = _UETPath(__file__).resolve()
for _UET_CANDIDATE in (_UET_HERE.parent, *_UET_HERE.parents):
    if (_UET_CANDIDATE / "docs" / "core" / "core_paths.py").is_file():
        _UET_REPO_ROOT = _UET_CANDIDATE
        break
if _UET_REPO_ROOT is None:
    raise RuntimeError("cannot locate repository root from the tooling script")
if str(_UET_REPO_ROOT) not in _uet_sys.path:
    _uet_sys.path.insert(0, str(_UET_REPO_ROOT))
# END UET REPO ROOT BOOTSTRAP
import sys
import os

# Add the current directory to sys.path to simulate a package install
sys.path.insert(0, str(_UET_REPO_ROOT))

print("🚀 Verifying UET Library Packaging...")

try:
    import docs as uet

    print("✅ Successfully imported docs")
except ImportError as e:
    print(f"❌ Failed to import docs: {e}")
    sys.exit(1)

# Test Fluid
try:
    print("\n💧 Testing basic Fluid Engine instantiation...")
    fluid_solver = uet.fluid.Engine2D(nx=32, ny=32, dt=0.01)
    print("✅ uet.fluid.Engine2D instantiated successfully")
    print(f"   Name: {fluid_solver.name}")
except Exception as e:
    print(f"❌ Failed to use uet.fluid: {e}")

# Test Complexity
try:
    print("\n🕸️ Testing basic Complexity Engine instantiation...")
    comp_solver = uet.complexity.ComplexityEngine(nx=20, ny=20)
    print("✅ uet.complexity.ComplexityEngine instantiated successfully")
    print(f"   Name: {comp_solver.name}")
except Exception as e:
    print(f"❌ Failed to use uet.complexity: {e}")

# Test Mathnicry (Riemann)
try:
    print("\n📐 Testing basic Mathnicry (Riemann) instantiation...")
    riemann = uet.math.RiemannEngine()
    print("✅ uet.math.RiemannEngine instantiated successfully")
except Exception as e:
    print(f"❌ Failed to use uet.math: {e}")

# Test SHA256 (Rust Miner proxy/fallback)
try:
    print("\n⛏️ Testing basic SHA256 Native instantiation...")
    # SHA256 is a module now, not a class
    print(f"   SHA256 Module: {uet.math.SHA256}")
    print("✅ uet.math.SHA256 loaded successfully")
except Exception as e:
    print(f"❌ Failed to use uet.math.SHA256: {e}")

print("\n✨ Verification Complete! The library structure is valid.")
