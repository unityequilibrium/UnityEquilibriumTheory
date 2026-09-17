#!/usr/bin/env python3
"""
Analyze Log Distribution Across All Topics

Scans all research topics and generates a comprehensive report on log distribution,
identifying topics with excessive logs, no logs, and potential broken log systems.
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
import csv
from datetime import datetime
from collections import defaultdict


def count_items(path):
    """Count all files and directories in a path recursively."""
    if not path.exists():
        return 0
    return sum(1 for _ in path.rglob("*") if _.is_file())


def analyze_topic(topic_path):
    """Analyze a single topic's log structure."""
    topic_name = topic_path.name
    log_dir = topic_path / "Result" / "_Logs"
    result_dir = topic_path / "Result"

    # Count log files
    log_file_count = count_items(log_dir) if log_dir.exists() else 0
    result_file_count = count_items(result_dir) if result_dir.exists() else 0

    # Check for empty timestamp folders
    empty_timestamp_folders = 0
    timestamp_folders = []

    if log_dir.exists():
        for item in log_dir.iterdir():
            if item.is_dir() and item.name.isdigit():
                # Check if folder is empty
                if not any(item.iterdir()):
                    empty_timestamp_folders += 1
                    timestamp_folders.append(item.name)

    # Check for special folders
    special_folders = []
    if log_dir.exists():
        for item in log_dir.iterdir():
            if item.is_dir() and item.name.startswith(("0", "1", "2", "3", "4")) and not item.name.isdigit():
                special_folders.append(item.name)

    return {
        "topic": topic_name,
        "has_log_folder": log_dir.exists(),
        "log_file_count": log_file_count,
        "result_file_count": result_file_count,
        "empty_timestamp_folders": empty_timestamp_folders,
        "special_folders": special_folders,
        "log_folder_path": str(log_dir) if log_dir.exists() else "N/A"
    }


def categorize_topic(log_count):
    """Categorize topic based on log count."""
    if log_count == 0:
        return "NO_LOGS"
    elif log_count < 10:
        return "MINIMAL"
    elif log_count < 100:
        return "LOW"
    elif log_count < 500:
        return "MODERATE"
    elif log_count < 1000:
        return "HIGH"
    else:
        return "EXCESSIVE"


def main():
    """Main analysis function."""
    topics_root = _UET_REPO_ROOT / "docs" / "topics"

    print("=" * 80)
    print("LOG DISTRIBUTION ANALYSIS")
    print("=" * 80)
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Topics Root: {topics_root.absolute()}")
    print()

    # Analyze all topics
    results = []
    for topic in topics_root.iterdir():
        if not topic.is_dir() or not topic.name.startswith("0."):
            continue

        result = analyze_topic(topic)
        result["category"] = categorize_topic(result["log_file_count"])
        results.append(result)

    # Sort by log count (descending)
    results.sort(key=lambda x: x["log_file_count"], reverse=True)

    # Print summary
    print("\nSUMMARY STATISTICS")
    print("-" * 80)
    print(f"Total Topics Analyzed: {len(results)}")

    category_counts = defaultdict(int)
    for r in results:
        category_counts[r["category"]] += 1

    print("\nLog Count Distribution:")
    for category in ["EXCESSIVE", "HIGH", "MODERATE", "LOW", "MINIMAL", "NO_LOGS"]:
        count = category_counts.get(category, 0)
        print(f"  {category:15s}: {count:3d} topics")

    # Print detailed report
    print("\nDETAILED REPORT")
    print("-" * 80)
    print(f"{'Topic':<40} {'Category':<10} {'Logs':<8} {'Result':<8} {'Empty Folders':<15}")
    print("-" * 80)

    for r in results:
        print(f"{r['topic']:<40} {r['category']:<10} {r['log_file_count']:<8} {r['result_file_count']:<8} {r['empty_timestamp_folders']:<15}")

    # Print topics needing attention
    print("\nTOPICS NEEDING ATTENTION")
    print("-" * 80)

    print("\n1. EXCESSIVE LOGS (High Priority for Cleanup):")
    excessive = [r for r in results if r["category"] == "EXCESSIVE"]
    if excessive:
        for r in excessive:
            print(f"   - {r['topic']}: {r['log_file_count']} log files")
    else:
        print("   None")

    print("\n2. NO LOGS (Possible Broken Log Systems):")
    no_logs = [r for r in results if r["category"] == "NO_LOGS"]
    if no_logs:
        for r in no_logs:
            print(f"   - {r['topic']}: No log folder or empty")
    else:
        print("   None")

    print("\n3. MINIMAL LOGS (Investigation Needed):")
    minimal = [r for r in results if r["category"] == "MINIMAL"]
    if minimal:
        for r in minimal:
            print(f"   - {r['topic']}: {r['log_file_count']} log files")
    else:
        print("   None")

    print("\n4. EMPTY TIMESTAMP FOLDERS (Indicates Broken Logging):")
    broken_logging = [r for r in results if r["empty_timestamp_folders"] > 0]
    if broken_logging:
        for r in broken_logging:
            print(f"   - {r['topic']}: {r['empty_timestamp_folders']} empty folders")
    else:
        print("   None")

    # Save to CSV
    csv_path = _UET_REPO_ROOT / "docs" / "scripts" / "maintenance" / "log_analysis_report.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Topic", "Category", "LogFileCount", "ResultFileCount",
            "EmptyTimestampFolders", "HasLogFolder", "LogFolderPath"
        ])
        for r in results:
            writer.writerow([
                r["topic"], r["category"], r["log_file_count"],
                r["result_file_count"], r["empty_timestamp_folders"],
                r["has_log_folder"], r["log_folder_path"]
            ])

    print(f"\nCSV Report saved to: {csv_path}")

    # Save to JSON
    json_path = _UET_REPO_ROOT / "docs" / "scripts" / "maintenance" / "log_analysis_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"JSON Report saved to: {json_path}")
    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()
