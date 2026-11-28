import sys
import os

# Setup Path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print(f"Project Root: {project_root}")
print(f"Sys Path: {sys.path[:3]}")

try:
    print("Attempting to import docs...")
    import docs

    print(f"Success: {docs}")

    print("Attempting to import docs.core...")
    import docs.core

    print(f"Success: {docs.core}")

    print("Attempting to import docs.core.uet_parameters...")
    import docs.core.uet_parameters as p

    print(f"Success module: {p}")
    print(f"Has UETParameters? {'UETParameters' in dir(p)}")

    from docs.core.uet_parameters import UETParameters

    print(f"Success class: {UETParameters}")

except Exception as e:
    print(f"FAIL: {e}")
    import traceback

    traceback.print_exc()
