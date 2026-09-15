#!/usr/bin/env python3
"""
Diagnose Log Systems

Check which topics have working log generation, identify broken log systems,
and generate a comprehensive health report.
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

from pathlib import Path
import json
from datetime import datetime
from collections import defaultdict


def check_log_system_health(topic_path):
    """Check the health of a topic's log system."""
    topic_name = topic_path.name
    log_dir = topic_path / "Result" / "_Logs"
    result_dir = topic_path / "Result"
    code_dir = topic_path / "Code"

    health_status = {
        "topic": topic_name,
        "has_code_folder": code_dir.exists(),
        "has_result_folder": result_dir.exists(),
        "has_log_folder": log_dir.exists(),
        "log_folder_exists": False,
        "has_logs": False,
        "log_count": 0,
        "has_timestamp_folders": False,
        "timestamp_folder_count": 0,
        "has_empty_timestamp_folders": False,
        "empty_timestamp_count": 0,
        "has_special_folders": False,
        "special_folder_names": [],
        "health_status": "UNKNOWN",
        "issues": [],
        "recommendations": []
    }

    # Check if log folder exists
    if log_dir.exists():
        health_status["log_folder_exists"] = True

        # Count log files
        log_files = list(log_dir.rglob("*"))
        health_status["log_count"] = sum(1 for f in log_files if f.is_file())
        health_status["has_logs"] = health_status["log_count"] > 0

        # Check for timestamp folders
        timestamp_folders = []
        empty_timestamp_folders = []
        for item in log_dir.iterdir():
            if item.is_dir() and item.name.isdigit():
                timestamp_folders.append(item.name)
                if not any(item.iterdir()):
                    empty_timestamp_folders.append(item.name)

        health_status["has_timestamp_folders"] = len(timestamp_folders) > 0
        health_status["timestamp_folder_count"] = len(timestamp_folders)
        health_status["has_empty_timestamp_folders"] = len(empty_timestamp_folders) > 0
        health_status["empty_timestamp_count"] = len(empty_timestamp_folders)

        # Check for special folders
        special_folders = []
        for item in log_dir.iterdir():
            if item.is_dir() and item.name.startswith(("0", "1", "2", "3", "4")) and not item.name.isdigit():
                special_folders.append(item.name)

        health_status["has_special_folders"] = len(special_folders) > 0
        health_status["special_folder_names"] = special_folders

    # Determine health status
    issues = []
    recommendations = []

    if not health_status["has_code_folder"]:
        issues.append("No Code folder found")
        recommendations.append("Verify topic structure")

    if not health_status["has_result_folder"]:
        issues.append("No Result folder found")
        recommendations.append("Run topic tests to generate results")

    if not health_status["has_log_folder"]:
        issues.append("No _Logs folder in Result")
        recommendations.append("Run topic tests to generate logs")
        health_status["health_status"] = "BROKEN"
    elif not health_status["has_logs"]:
        issues.append("Log folder exists but no log files")
        recommendations.append("Run topic tests to generate logs")
        health_status["health_status"] = "BROKEN"
    elif health_status["has_empty_timestamp_folders"]:
        issues.append(f"{health_status['empty_timestamp_count']} empty timestamp folders")
        recommendations.append("Investigate broken log generation")
        health_status["health_status"] = "DEGRADED"
    elif health_status["log_count"] > 1000:
        issues.append(f"Excessive log count: {health_status['log_count']}")
        recommendations.append("Consider log cleanup")
        health_status["health_status"] = "WARNING"
    else:
        health_status["health_status"] = "HEALTHY"

    health_status["issues"] = issues
    health_status["recommendations"] = recommendations

    return health_status


def generate_health_report(topics_root):
    """Generate a comprehensive health report for all topics."""
    print("=" * 80)
    print("LOG SYSTEM HEALTH DIAGNOSTIC")
    print("=" * 80)
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Topics Root: {topics_root.absolute()}")
    print()

    # Analyze all topics
    results = []
    for topic in topics_root.iterdir():
        if not topic.is_dir() or not topic.name.startswith("0."):
            continue

        health = check_log_system_health(topic)
        results.append(health)

    # Categorize results
    status_counts = defaultdict(int)
    for r in results:
        status_counts[r["health_status"]] += 1

    # Print summary
    print("SUMMARY")
    print("-" * 80)
    print(f"Total Topics Analyzed: {len(results)}")
    print()
    print("Health Status Distribution:")
    for status in ["HEALTHY", "DEGRADED", "WARNING", "BROKEN", "UNKNOWN"]:
        count = status_counts.get(status, 0)
        percentage = (count / len(results) * 100) if results else 0
        print(f"  {status:15s}: {count:3d} topics ({percentage:5.1f}%)")

    # Print detailed report
    print("\nDETAILED HEALTH REPORT")
    print("-" * 80)
    print(f"{'Topic':<40} {'Status':<10} {'Logs':<8} {'Timestamps':<12} {'Empty':<8} {'Issues'}")
    print("-" * 80)

    for r in sorted(results, key=lambda x: x["topic"]):
        issues_str = "; ".join(r["issues"][:2]) if r["issues"] else ""
        if len(r["issues"]) > 2:
            issues_str += "..."
        print(f"{r['topic']:<40} {r['health_status']:<10} {r['log_count']:<8} {r['timestamp_folder_count']:<12} {r['empty_timestamp_count']:<8} {issues_str[:50]}")

    # Print issues by category
    print("\nISSUES BY CATEGORY")
    print("-" * 80)

    print("\n1. BROKEN LOG SYSTEMS (Critical Issues):")
    broken = [r for r in results if r["health_status"] == "BROKEN"]
    if broken:
        for r in broken:
            print(f"   - {r['topic']}:")
            for issue in r["issues"]:
                print(f"       * {issue}")
            for rec in r["recommendations"]:
                print(f"       → {rec}")
    else:
        print("   None")

    print("\n2. DEGRADED LOG SYSTEMS (Empty Timestamp Folders):")
    degraded = [r for r in results if r["health_status"] == "DEGRADED"]
    if degraded:
        for r in degraded:
            print(f"   - {r['topic']}: {r['empty_timestamp_count']} empty folders")
            for rec in r["recommendations"]:
                print(f"       → {rec}")
    else:
        print("   None")

    print("\n3. WARNING (Excessive Logs):")
    warnings = [r for r in results if r["health_status"] == "WARNING"]
    if warnings:
        for r in warnings:
            print(f"   - {r['topic']}: {r['log_count']} log files")
            for rec in r["recommendations"]:
                print(f"       → {rec}")
    else:
        print("   None")

    print("\n4. HEALTHY LOG SYSTEMS:")
    healthy = [r for r in results if r["health_status"] == "HEALTHY"]
    if healthy:
        for r in healthy:
            print(f"   - {r['topic']}: {r['log_count']} log files")
    else:
        print("   None")

    # Save report to JSON
    report_path = _UET_REPO_ROOT / "docs" / "scripts" / "maintenance" / "log_health_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nFull report saved to: {report_path}")

    # Generate summary recommendations
    print("\nSUMMARY RECOMMENDATIONS")
    print("-" * 80)

    if broken:
        print(f"\nCRITICAL: {len(broken)} topics have broken log systems")
        print("  → Run topic tests to generate logs")
        print("  → Verify log generation code is working")

    if degraded:
        print(f"\nATTENTION: {len(degraded)} topics have degraded log systems")
        print("  → Investigate why timestamp folders are empty")
        print("  → Check for errors in log generation code")

    if warnings:
        print(f"\nMAINTENANCE: {len(warnings)} topics have excessive logs")
        print("  → Run log cleanup: python reset_topic_logs.py --category EXCESSIVE --keep-recent 10")

    print("\nDiagnostic complete!")


def main():
    """Main entry point."""
    topics_root = _UET_REPO_ROOT / "docs" / "topics"
    generate_health_report(topics_root)


if __name__ == "__main__":
    main()
