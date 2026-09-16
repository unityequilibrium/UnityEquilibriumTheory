import sys
import os

print(f"CWD: {os.getcwd()}")
print(f"sys.path: {sys.path}")

try:
    print("Attempting to import docs.scripts.core.runners.uet_matrix_engine...")
    import docs.scripts.core.runners.uet_matrix_engine

    print("✅ Success: uet_matrix_engine imported.")
except Exception as e:
    print(f"❌ Failed: {e}")

try:
    print("Attempting to import docs.scripts.core.runners.uet_base_solver...")
    from docs.scripts.core.runners.uet_base_solver import UETBaseSolver

    print("✅ Success: UETBaseSolver imported.")
except Exception as e:
    print(f"❌ Failed: {e}")
