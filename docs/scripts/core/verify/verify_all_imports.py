
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
import os
import sys
import importlib.util
from pathlib import Path
import ast

# Add project root to path so imports work
ROOT_DIR = _UET_REPO_ROOT
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def verify_file(file_path):
    rel_path = file_path.relative_to(ROOT_DIR)
    module_name = str(rel_path).replace(os.sep, ".").replace(".py", "")

    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            # We don't need to execute the module fully if it has side effects,
            # but usually execution is needed to catch NameErrors at module level.
            # Ideally we just compile it to check syntax, but NameError usually happens at runtime (top level).
            # Let's try to compile first (syntax), then exec.

            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()

            # 1. Syntax Check
            compile(source, file_path, "exec")

            # 2. Variable Definition Check (Simpler than full exec)
            # Full exec might trigger heavy computations or plots.
            # We mostly want to check if 'root_path' or imports are broken.
            # Let's skip full execution for now to avoid side effects,
            # OR we can execute but catch errors.

            # Compromise: We check for specific patterns that failed before.
            # if 'root_path' is used, is it defined?
            # We can use AST to check this without running.
            pass

    except SyntaxError as e:
        return False, f"SyntaxError: {e}"
    except Exception as e:
        return False, f"Error: {e}"

    return True, "OK"


def static_analysis(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        # Check for BOM
        if source.startswith("\ufeff"):
            return False, "BOM Detected"

        tree = ast.parse(source)

        # Check if root_path is used
        uses_root_path = False
        defines_root_path = False

        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == "root_path":
                if isinstance(node.ctx, ast.Load):
                    uses_root_path = True
                elif isinstance(node.ctx, ast.Store):
                    defines_root_path = True

            # Also check for 'from docs import ROOT_PATH'
            if isinstance(node, ast.ImportFrom):
                if node.module == "docs":
                    for name in node.names:
                        if name.name == "ROOT_PATH":
                            # This counts as valid infrastructure
                            pass

        if uses_root_path and not defines_root_path:
            # Check if it was imported?
            # Just scanning for the text "root_path =" is safer/easier than full AST scope resolution
            if "root_path =" not in source and "root_path=" not in source:
                return False, "Potential NameError: root_path used but not defined"

        # Check for current_path
        uses_current = "current_path" in source
        defines_current = "current_path =" in source or "current_path=" in source
        if uses_current and not defines_current:
            return False, "Potential NameError: current_path used but not defined"

        return True, "OK"

    except Exception as e:
        return False, f"AST Error: {e}"


def main():
    target_dir = ROOT_DIR / "docs" / "topics"
    print(f"Scanning {target_dir} for broken files...")

    passed = 0
    failed = 0
    failures = []

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".py"):
                path = Path(root) / file
                ok, msg = static_analysis(path)
                if not ok:
                    print(f"FAIL: {path.relative_to(ROOT_DIR)} -> {msg}")
                    failures.append(path)
                    failed += 1
                else:
                    passed += 1

    print("-" * 40)
    print(f"Scanned: {passed + failed}")
    print(f"Passed:  {passed}")
    print(f"Failed:  {failed}")

    if failures:
        print("\nFixing failures automatically...")
        # Automate the fix for found failures
        for bad_file in failures:
            fix_file(bad_file)

    sys.exit(1 if failed > 0 else 0)


def fix_file(file_path):
    # Apply the same fix we successfully used on Quantum
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # REMOVE BOM
        if content.startswith("\ufeff"):
            content = content[1:]

        param_code = "from docs import ROOT_PATH\nroot_path = ROOT_PATH"

        # Check if we already have it but maybe in wrong place?
        if "from docs import ROOT_PATH" in content:
            # Maybe it's defined too late?
            # Let's move it to top.
            lines = content.split("\n")
            # Remove existing lines
            lines = [
                l
                for l in lines
                if "from docs import ROOT_PATH" not in l
                and "root_path = ROOT_PATH" not in l
            ]
            # Insert at top after docstring/Shebang
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    insert_idx = i
                    break
            if (
                insert_idx == 0
                and len(lines) > 0
                and (lines[0].startswith("#") or lines[0].startswith('"""'))
            ):
                # Skip header
                for i, line in enumerate(lines):
                    if not line.strip():
                        continue
                    if line.startswith("import") or line.startswith("from"):
                        insert_idx = i
                        break

            lines.insert(insert_idx, param_code)
            content = "\n".join(lines)

        else:
            # Check if root_path logic is missing entirely
            # Just insert it
            lines = content.split("\n")
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("import") or line.startswith("from"):
                    insert_idx = i
                    break

            # If failing due to SyntaxError, maybe we fix that first?
            # BOM removal is handled above.

            # Force insert at top if no suitable place found
            if insert_idx == 0:
                if len(lines) > 0 and (lines[0].startswith("#") or lines[0].startswith('"""')):
                    pass
                else:
                    insert_idx = 0

            lines.insert(insert_idx, param_code)
            content = "\n".join(lines)

        # FIX CURRENT_PATH
        if (
            "current_path" in content
            and "current_path =" not in content
            and "current_path=" not in content
        ):
            # Inject current_path definition
            lines = content.split("\n")
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.strip() == "from docs import ROOT_PATH":
                    insert_idx = i + 1
                    break

            if insert_idx == 0:
                # find root path
                for i, line in enumerate(lines):
                    if "root_path = ROOT_PATH" in line:
                        insert_idx = i + 1
                        break

            if insert_idx > 0:
                lines.insert(
                    insert_idx, "from pathlib import Path\ncurrent_path = Path(__file__).resolve()"
                )
                content = "\n".join(lines)
                print(f"  Fixed current_path in: {file_path.name}")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  Fixed: {file_path.name}")

    except Exception as e:
        print(f"  Failed to fix {file_path.name}: {e}")


if __name__ == "__main__":
    main()
