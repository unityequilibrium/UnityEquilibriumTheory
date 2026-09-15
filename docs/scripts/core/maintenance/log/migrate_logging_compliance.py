#!/usr/bin/env python3
"""
Migrate Logging Compliance
===========================
Automatically fixes UETMetricLogger calls to follow the Triple-Green Output Standard.
"""

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

import ast
import re
from pathlib import Path
from typing import Dict, List, Tuple


class LoggingComplianceMigrator:
    """Migrates code to follow logging compliance standards."""

    def __init__(self):
        self.fixed_files = []
        self.skipped_files = []

    def migrate_file(self, file_path: Path, dry_run: bool = False) -> bool:
        """Migrate a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            content = self._fix_uet_metric_logger_calls(content)
            content = self._fix_uet_path_manager_calls(content)

            if content != original_content:
                if dry_run:
                    print(f"Would fix: {file_path}")
                    return True
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ Fixed: {file_path}")
                    self.fixed_files.append(str(file_path))
                    return True
            else:
                self.skipped_files.append(str(file_path))
                return False

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return False

    def _fix_uet_metric_logger_calls(self, content: str) -> str:
        """Fix UETMetricLogger calls to include category parameter."""
        # Pattern 1: UETMetricLogger("name", topic_id="X") -> add category="log"
        pattern1 = r'(UETMetricLogger\s*\(\s*"[^"]+"\s*,\s*topic_id\s*=\s*"([^"]+)"\s*\))'
        replacement1 = r'\1, category="log"'
        content = re.sub(pattern1, replacement1, content)

        # Pattern 2: UETMetricLogger("name", output_dir=...) -> convert to topic_id + category
        # This is more complex, need to handle it differently
        pattern2 = r'(UETMetricLogger\s*\(\s*"[^"]+"\s*,\s*output_dir\s*=\s*([^)]+)\))'
        matches = list(re.finditer(pattern2, content))

        for match in reversed(matches):  # Reverse to avoid offset issues
            full_match = match.group(0)
            output_dir_expr = match.group(2)

            # Try to extract topic_id from the output_dir
            # Look for patterns like: UETPathManager.get_result_dir("0.1", ...)
            topic_id_match = re.search(r'get_result_dir\s*\(\s*"(\d+\.\d+)"', output_dir_expr)
            if topic_id_match:
                topic_id = topic_id_match.group(1)
                # Extract simulation name
                sim_name_match = re.search(r'UETMetricLogger\s*\(\s*"([^"]+)"', full_match)
                sim_name = sim_name_match.group(1) if sim_name_match else "Simulation"
                # Replace with topic_id + category
                replacement = f'UETMetricLogger("{sim_name}", topic_id="{topic_id}", category="log")'
                content = content[:match.start()] + replacement + content[match.end():]

        return content

    def _fix_uet_path_manager_calls(self, content: str) -> str:
        """Fix UETPathManager.get_result_dir calls to include category parameter."""
        # Pattern: UETPathManager.get_result_dir("X", "Y", ...) -> add category="log"
        pattern = r'(UETPathManager\.get_result_dir\s*\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*pillar\s*=\s*"([^"]+)"\s*\))'
        replacement = r'\1, category="log"'
        content = re.sub(pattern, replacement, content)

        return content

    def migrate_directory(self, dir_path: Path, dry_run: bool = False):
        """Migrate all Python files in a directory."""
        py_files = list(dir_path.rglob("*.py"))

        # Skip __pycache__ and test files
        py_files = [f for f in py_files if "__pycache__" not in str(f) and "test_" not in f.name]

        print(f"Found {len(py_files)} Python files to check")

        fixed_count = 0
        for py_file in py_files:
            if self.migrate_file(py_file, dry_run):
                fixed_count += 1

        print(f"\n{'='*80}")
        print(f"Migration Summary")
        print(f"{'='*80}")
        print(f"Total files checked: {len(py_files)}")
        print(f"Files fixed: {fixed_count}")
        print(f"Files skipped: {len(self.skipped_files)}")

        if not dry_run and self.fixed_files:
            print(f"\nFixed files:")
            for f in self.fixed_files:
                print(f"  - {f}")


def main():
    """Main entry point."""
    import sys

    if len(sys.argv) > 1:
        # Migrate specific file or directory
        path = Path(sys.argv[1])
        migrator = LoggingComplianceMigrator()

        if path.is_file():
            migrator.migrate_file(path)
        elif path.is_dir():
            migrator.migrate_directory(path)
        else:
            print(f"Error: {path} is not a valid file or directory")
            sys.exit(1)
    else:
        # Migrate all topics
        print("Migrating all topics...")
        print("This will fix UETMetricLogger calls to include category parameter")
        print()

        response = input("Continue? [yes/NO]: ")
        if response.lower() not in ['yes', 'y']:
            print("Cancelled")
            sys.exit(0)

        topics_root = _UET_REPO_ROOT / "docs" / "topics"
        migrator = LoggingComplianceMigrator()

        topics = sorted([t for t in topics_root.iterdir()
                        if t.is_dir() and t.name.startswith("0.")])

        for topic_path in topics:
            print(f"\nMigrating: {topic_path.name}")
            migrator.migrate_directory(topic_path)

        print("\n✅ Migration complete!")


if __name__ == "__main__":
    main()
