#!/usr/bin/env python3
"""
Validate Logging Compliance
===========================
Validates that topics follow the Triple-Green Output Standard.
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
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    is_valid: bool
    file_path: str
    line_number: int
    issue_type: str
    message: str
    severity: str  # ERROR, WARNING, INFO


class LoggingComplianceValidator:
    """Validates logging compliance in Python files."""

    def __init__(self):
        self.issues: List[ValidationResult] = []

    def validate_file(self, file_path: Path) -> List[ValidationResult]:
        """Validate a single Python file."""
        self.issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            # Check for UETMetricLogger usage
            self._check_uet_metric_logger_usage(tree, file_path, content)

            # Check for UETPathManager usage
            self._check_uet_path_manager_usage(tree, file_path, content)

        except Exception as e:
            self.issues.append(ValidationResult(
                is_valid=False,
                file_path=str(file_path),
                line_number=0,
                issue_type="PARSING_ERROR",
                message=f"Could not parse file: {e}",
                severity="ERROR"
            ))

        return self.issues

    def _check_uet_metric_logger_usage(self, tree: ast.AST, file_path: Path, content: str):
        """Check UETMetricLogger usage patterns."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check if it's a UETMetricLogger call
                if isinstance(node.func, ast.Name) and node.func.id == "UETMetricLogger":
                    self._validate_logger_call(node, file_path)

    def _check_uet_path_manager_usage(self, tree: ast.AST, file_path: Path, content: str):
        """Check UETPathManager usage patterns."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check if it's a UETPathManager.get_result_dir call
                if (isinstance(node.func, ast.Attribute) and
                    isinstance(node.func.value, ast.Name) and
                    node.func.value.id == "UETPathManager" and
                    node.func.attr == "get_result_dir"):
                    self._validate_path_manager_call(node, file_path)

    def _validate_logger_call(self, node: ast.Call, file_path: Path):
        """Validate a UETMetricLogger call."""
        line_number = node.lineno if hasattr(node, 'lineno') else 0

        # Extract keyword arguments
        kwargs = {}
        for kw in node.keywords:
            if isinstance(kw.value, ast.Constant):
                kwargs[kw.arg] = kw.value.value
            elif hasattr(ast, 'Str') and isinstance(kw.value, ast.Str):
                kwargs[kw.arg] = kw.value.s

        # Check for category parameter
        if "category" not in kwargs:
            self.issues.append(ValidationResult(
                is_valid=False,
                file_path=str(file_path),
                line_number=line_number,
                issue_type="MISSING_CATEGORY",
                message="UETMetricLogger call missing 'category' parameter. "
                        "Use category='showcase', 'figures', or 'log'",
                severity="ERROR"
            ))
        else:
            category = kwargs["category"]
            valid_categories = ["showcase", "figures", "log"]
            if category not in valid_categories:
                self.issues.append(ValidationResult(
                    is_valid=False,
                    file_path=str(file_path),
                    line_number=line_number,
                    issue_type="INVALID_CATEGORY",
                    message=f"Invalid category '{category}'. "
                            f"Valid categories: {', '.join(valid_categories)}",
                    severity="ERROR"
                ))

        # Check for topic_id parameter
        if "topic_id" not in kwargs:
            # Check if using output_dir (legacy pattern)
            if "output_dir" in kwargs:
                self.issues.append(ValidationResult(
                    is_valid=False,
                    file_path=str(file_path),
                    line_number=line_number,
                    issue_type="LEGACY_PATTERN",
                    message="Using 'output_dir' directly is deprecated. "
                            "Use 'topic_id' and 'category' parameters instead",
                    severity="WARNING"
                ))
            else:
                self.issues.append(ValidationResult(
                    is_valid=False,
                    file_path=str(file_path),
                    line_number=line_number,
                    issue_type="MISSING_TOPIC_ID",
                    message="UETMetricLogger call missing 'topic_id' parameter "
                            "(or 'output_dir' for legacy code)",
                    severity="WARNING"
                ))

    def _validate_path_manager_call(self, node: ast.Call, file_path: Path):
        """Validate a UETPathManager.get_result_dir call."""
        line_number = node.lineno if hasattr(node, 'lineno') else 0

        # Extract keyword arguments
        kwargs = {}
        for kw in node.keywords:
            if isinstance(kw.value, ast.Constant):
                kwargs[kw.arg] = kw.value.value
            elif hasattr(ast, 'Str') and isinstance(kw.value, ast.Str):
                kwargs[kw.arg] = kw.value.s

        # Check for category parameter
        if "category" not in kwargs:
            self.issues.append(ValidationResult(
                is_valid=False,
                file_path=str(file_path),
                line_number=line_number,
                issue_type="MISSING_CATEGORY",
                message="UETPathManager.get_result_dir() missing 'category' parameter. "
                        "Use category='showcase', 'figures', or 'log'",
                severity="ERROR"
            ))

    def validate_directory(self, dir_path: Path) -> List[ValidationResult]:
        """Validate all Python files in a directory."""
        all_issues = []

        py_files = list(dir_path.rglob("*.py"))

        for py_file in py_files:
            # Skip __pycache__ and test files
            if "__pycache__" in str(py_file) or "test_" in py_file.name:
                continue

            issues = self.validate_file(py_file)
            all_issues.extend(issues)

        return all_issues

    def print_issues(self, issues: List[ValidationResult]):
        """Print validation issues."""
        if not issues:
            print("No issues found!")
            return

        # Group by severity
        errors = [i for i in issues if i.severity == "ERROR"]
        warnings = [i for i in issues if i.severity == "WARNING"]
        infos = [i for i in issues if i.severity == "INFO"]

        print(f"\n{'='*80}")
        print(f"VALIDATION RESULTS")
        print(f"{'='*80}")
        print(f"Total Issues: {len(issues)}")
        print(f"  Errors: {len(errors)}")
        print(f"  Warnings: {len(warnings)}")
        print(f"  Info: {len(infos)}")

        if errors:
            print(f"\n{'='*80}")
            print("ERRORS")
            print(f"{'='*80}")
            for issue in errors:
                print(f"\n{issue.file_path}:{issue.line_number}")
                print(f"  [{issue.issue_type}] {issue.message}")

        if warnings:
            print(f"\n{'='*80}")
            print("WARNINGS")
            print(f"{'='*80}")
            for issue in warnings:
                print(f"\n{issue.file_path}:{issue.line_number}")
                print(f"  [{issue.issue_type}] {issue.message}")

        if infos:
            print(f"\n{'='*80}")
            print("INFO")
            print(f"{'='*80}")
            for issue in infos:
                print(f"\n{issue.file_path}:{issue.line_number}")
                print(f"  [{issue.issue_type}] {issue.message}")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Validate specific file or directory
        path = Path(sys.argv[1])
        validator = LoggingComplianceValidator()

        if path.is_file():
            issues = validator.validate_file(path)
        elif path.is_dir():
            issues = validator.validate_directory(path)
        else:
            print(f"Error: {path} is not a valid file or directory")
            sys.exit(1)

        validator.print_issues(issues)
        sys.exit(1 if any(i.severity == "ERROR" for i in issues) else 0)
    else:
        # Validate all topics
        print("Validating all topics...")
        topics_root = _UET_REPO_ROOT / "docs" / "topics"
        validator = LoggingComplianceValidator()

        all_issues = []
        topics = sorted([t for t in topics_root.iterdir()
                        if t.is_dir() and t.name.startswith("0.")])

        for topic_path in topics:
            print(f"Validating: {topic_path.name}")
            issues = validator.validate_directory(topic_path)
            all_issues.extend(issues)

        validator.print_issues(all_issues)

        if any(i.severity == "ERROR" for i in all_issues):
            print("\nValidation FAILED")
            sys.exit(1)
        else:
            print("\nValidation PASSED")
            sys.exit(0)


if __name__ == "__main__":
    main()
