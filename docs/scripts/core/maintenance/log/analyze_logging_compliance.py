#!/usr/bin/env python3
"""
Analyze Logging Compliance Across All Topics
==============================================
Scans all research topics to check if they follow the Triple-Green Output Standard.
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
import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class TopicCompliance:
    topic_id: str
    topic_name: str
    has_uet_metric_logger: bool
    uses_category_param: bool
    uses_topic_id_param: bool
    uses_output_dir_directly: bool
    category_usage: Dict[str, int]  # showcase, figures, log, none
    total_files_scanned: int
    issues: List[str]
    warnings: List[str]


class LoggingComplianceAnalyzer:
    def __init__(self):
        self.topics_root = _UET_REPO_ROOT / "docs" / "topics"
        self.results: List[TopicCompliance] = []

    def analyze_topic(self, topic_path: Path) -> TopicCompliance:
        """Analyze a single topic for logging compliance."""
        topic_name = topic_path.name
        topic_id = topic_name.split("_")[0] if "_" in topic_name else topic_name

        compliance = TopicCompliance(
            topic_id=topic_id,
            topic_name=topic_name,
            has_uet_metric_logger=False,
            uses_category_param=False,
            uses_topic_id_param=False,
            uses_output_dir_directly=False,
            category_usage={"showcase": 0, "figures": 0, "log": 0, "none": 0},
            total_files_scanned=0,
            issues=[],
            warnings=[],
        )

        # Scan all Python files in the topic
        py_files = list(topic_path.rglob("*.py"))
        compliance.total_files_scanned = len(py_files)

        for py_file in py_files:
            self._analyze_file(py_file, compliance)

        # Check output structure
        result_dir = topic_path / "Result"
        if result_dir.exists():
            self._check_output_structure(result_dir, compliance)

        return compliance

    def _analyze_file(self, py_file: Path, compliance: TopicCompliance):
        """Analyze a single Python file."""
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check if file uses UETMetricLogger
            if "UETMetricLogger" in content:
                compliance.has_uet_metric_logger = True

                # Parse the file to check usage patterns
                try:
                    tree = ast.parse(content)
                    self._check_ast_usage(tree, py_file, compliance)
                except Exception:
                    # Fallback to regex if AST parsing fails
                    self._check_regex_usage(content, py_file, compliance)

        except Exception as e:
            compliance.warnings.append(f"Could not analyze {py_file}: {e}")

    def _check_ast_usage(self, tree: ast.AST, py_file: Path, compliance: TopicCompliance):
        """Check UETMetricLogger usage using AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check if it's a UETMetricLogger call
                if isinstance(node.func, ast.Name) and node.func.id == "UETMetricLogger":
                    self._check_logger_call(node, py_file, compliance)

    def _check_regex_usage(self, content: str, py_file: Path, compliance: TopicCompliance):
        """Check UETMetricLogger usage using regex (fallback)."""
        # Find UETMetricLogger calls
        pattern = r'UETMetricLogger\s*\([^)]*\)'
        matches = re.finditer(pattern, content)

        for match in matches:
            call_content = match.group()
            self._check_logger_call_text(call_content, py_file, compliance)

    def _check_logger_call(self, node: ast.Call, py_file: Path, compliance: TopicCompliance):
        """Check a UETMetricLogger call node."""
        # Check keyword arguments
        kwargs = {}
        for kw in node.keywords:
            if isinstance(kw.value, ast.Constant):
                kwargs[kw.arg] = kw.value.value
            elif isinstance(kw.value, ast.Str):
                kwargs[kw.arg] = kw.value.s

        self._check_logger_params(kwargs, py_file, compliance)

    def _check_logger_call_text(self, call_content: str, py_file: Path, compliance: TopicCompliance):
        """Check a UETMetricLogger call using text."""
        # Extract parameter values
        params = {}
        for match in re.finditer(r'(\w+)\s*=\s*["\']([^"\']+)["\']', call_content):
            params[match.group(1)] = match.group(2)

        self._check_logger_params(params, py_file, compliance)

    def _check_logger_params(self, params: Dict[str, str], py_file: Path, compliance: TopicCompliance):
        """Check logger parameters."""
        # Check for category parameter
        if "category" in params:
            category = params["category"]
            compliance.uses_category_param = True
            if category in compliance.category_usage:
                compliance.category_usage[category] += 1
            else:
                compliance.category_usage["none"] += 1
                compliance.warnings.append(
                    f"{py_file.name}: Unknown category '{category}'"
                )
        else:
            compliance.category_usage["none"] += 1
            compliance.warnings.append(
                f"{py_file.name}: Missing category parameter"
            )

        # Check for topic_id parameter
        if "topic_id" in params:
            compliance.uses_topic_id_param = True

        # Check for output_dir parameter (legacy pattern)
        if "output_dir" in params:
            compliance.uses_output_dir_directly = True
            compliance.issues.append(
                f"{py_file.name}: Uses output_dir directly (should use topic_id + category)"
            )

    def _check_output_structure(self, result_dir: Path, compliance: TopicCompliance):
        """Check if output structure follows the standard."""
        required_dirs = ["01_Showcase", "02_Figures", "_Logs"]

        for dir_name in required_dirs:
            dir_path = result_dir / dir_name
            if not dir_path.exists():
                compliance.warnings.append(
                    f"Missing required directory: Result/{dir_name}"
                )
            else:
                # Check if directory is empty
                if not any(dir_path.iterdir()):
                    compliance.warnings.append(
                        f"Empty directory: Result/{dir_name}"
                    )

    def analyze_all_topics(self) -> List[TopicCompliance]:
        """Analyze all topics."""
        print("=" * 80)
        print("LOGGING COMPLIANCE ANALYSIS")
        print("=" * 80)
        print()

        topics = sorted([t for t in self.topics_root.iterdir() if t.is_dir() and t.name.startswith("0.")])

        for topic_path in topics:
            print(f"Analyzing: {topic_path.name}")
            compliance = self.analyze_topic(topic_path)
            self.results.append(compliance)

        return self.results

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive report."""
        total_topics = len(self.results)
        compliant_topics = sum(1 for r in self.results if not r.issues and not r.warnings)
        topics_with_issues = sum(1 for r in self.results if r.issues)
        topics_with_warnings = sum(1 for r in self.results if r.warnings)

        # Category compliance
        topics_using_showcase = sum(1 for r in self.results if r.category_usage["showcase"] > 0)
        topics_using_figures = sum(1 for r in self.results if r.category_usage["figures"] > 0)
        topics_using_log = sum(1 for r in self.results if r.category_usage["log"] > 0)
        topics_not_using_category = sum(1 for r in self.results if r.category_usage["none"] > 0)

        report = {
            "summary": {
                "total_topics": total_topics,
                "compliant_topics": compliant_topics,
                "topics_with_issues": topics_with_issues,
                "topics_with_warnings": topics_with_warnings,
                "compliance_rate": f"{(compliant_topics / total_topics * 100):.1f}%" if total_topics > 0 else "0%",
            },
            "category_compliance": {
                "topics_using_showcase": topics_using_showcase,
                "topics_using_figures": topics_using_figures,
                "topics_using_log": topics_using_log,
                "topics_not_using_category": topics_not_using_category,
            },
            "topics": [asdict(r) for r in self.results],
        }

        return report

    def save_csv_report(self, report: Dict[str, Any]):
        """Save CSV report."""
        csv_file = _UET_REPO_ROOT / "docs" / "scripts" / "maintenance" / "log" / "logging_compliance_report.csv"

        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Topic", "Has Logger", "Uses Category", "Uses Topic ID",
                "Uses Output Dir Directly", "Showcase Count", "Figures Count",
                "Log Count", "No Category Count", "Issues", "Warnings"
            ])

            for topic in report["topics"]:
                writer.writerow([
                    topic["topic_name"],
                    topic["has_uet_metric_logger"],
                    topic["uses_category_param"],
                    topic["uses_topic_id_param"],
                    topic["uses_output_dir_directly"],
                    topic["category_usage"]["showcase"],
                    topic["category_usage"]["figures"],
                    topic["category_usage"]["log"],
                    topic["category_usage"]["none"],
                    "; ".join(topic["issues"]),
                    "; ".join(topic["warnings"]),
                ])

        print(f"CSV Report saved to: {csv_file}")

    def save_json_report(self, report: Dict[str, Any]):
        """Save JSON report."""
        json_file = _UET_REPO_ROOT / "docs" / "scripts" / "maintenance" / "log" / "logging_compliance_report.json"

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        print(f"JSON Report saved to: {json_file}")

    def print_summary(self):
        """Print summary report."""
        report = self.generate_report()

        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total Topics: {report['summary']['total_topics']}")
        print(f"Compliant Topics: {report['summary']['compliant_topics']}")
        print(f"Topics with Issues: {report['summary']['topics_with_issues']}")
        print(f"Topics with Warnings: {report['summary']['topics_with_warnings']}")
        print(f"Compliance Rate: {report['summary']['compliance_rate']}")
        print()

        print("=" * 80)
        print("CATEGORY COMPLIANCE")
        print("=" * 80)
        print(f"Topics using 'showcase': {report['category_compliance']['topics_using_showcase']}")
        print(f"Topics using 'figures': {report['category_compliance']['topics_using_figures']}")
        print(f"Topics using 'log': {report['category_compliance']['topics_using_log']}")
        print(f"Topics NOT using category: {report['category_compliance']['topics_not_using_category']}")
        print()

        print("=" * 80)
        print("TOPICS NEEDING ATTENTION")
        print("=" * 80)

        for topic in report["topics"]:
            if topic["issues"] or topic["warnings"]:
                print(f"\n{topic['topic_name']}:")
                if topic["issues"]:
                    print("  Issues:")
                    for issue in topic["issues"]:
                        print(f"    - {issue}")
                if topic["warnings"]:
                    print("  Warnings:")
                    for warning in topic["warnings"]:
                        print(f"    - {warning}")


def main():
    """Main entry point."""
    analyzer = LoggingComplianceAnalyzer()
    analyzer.analyze_all_topics()
    analyzer.print_summary()

    report = analyzer.generate_report()
    analyzer.save_csv_report(report)
    analyzer.save_json_report(report)

    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()
