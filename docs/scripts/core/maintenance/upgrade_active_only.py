
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
import re

TARGET_VERSION = "v0.9.0"
# Only target these specific paths relative to the script location
# Script is in docs/scripts/
# Root is ../../
TARGET_PATHS = [
    "docs",  # Main package
    "README.md",  # Root readme
    "setup.py",  # Root setup
]

# Explicitly ignore these
IGNORE_KEYWORDS = [
    ".venv",
    ".git",
    ".gemini",
    "search Only",
    "ทองข้อมูลดี",
    "ของดีๆ แต่เละ",
    "99_Legacy",
    "Legacy_Archive",
    "__pycache__",
]


def upgrade_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Replace v0.8.x -> v0.9.0
        new_content = re.sub(r"v0\.8\.[0-9]+", "v0.9.0", content)
        new_content = re.sub(r"Version 0\.8\.[0-9]+", "Version 0.9.0", new_content)
        new_content = re.sub(r"Version: 0\.8\.[0-9]+", "Version: 0.9.0", new_content)
        new_content = re.sub(r"\(v0\.8\.[0-9]+\)", "(v0.9.0)", new_content)

        if new_content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True
    except Exception as e:
        # Ignore encoding errors for binary files etc
        pass
    return False


def is_safe_path(path):
    for kw in IGNORE_KEYWORDS:
        if kw in path:
            return False
    return True


def main():
    script_dir = str(_UET_REPO_ROOT / "docs" / "scripts" / "core")
    root_dir = os.path.abspath(os.path.join(script_dir, "../../"))

    print(f"🛡️ Starting SAFE Upgrade to {TARGET_VERSION}")
    print(f"📂 Root: {root_dir}")

    count = 0

    for target in TARGET_PATHS:
        full_target_path = os.path.join(root_dir, target)

        if os.path.isfile(full_target_path):
            if upgrade_file(full_target_path):
                print(f"✅ Upgraded File: {target}")
                count += 1
        elif os.path.isdir(full_target_path):
            for root, dirs, files in os.walk(full_target_path):
                # Filter directories in-place to prevent walking into them
                dirs[:] = [d for d in dirs if is_safe_path(os.path.join(root, d))]

                if not is_safe_path(root):
                    continue

                for file in files:
                    if file.endswith((".md", ".py", ".txt")):
                        filepath = os.path.join(root, file)
                        if upgrade_file(filepath):
                            rel_path = os.path.relpath(filepath, root_dir)
                            print(f"✅ Upgraded: {rel_path}")
                            count += 1

    print(f"\n🎉 Safe Upgrade Complete! Modified {count} files.")


if __name__ == "__main__":
    main()
