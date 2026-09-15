
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
from pathlib import Path


def audit_data_sources():
    print("🔍 UET DATA INTEGRITY AUDIT")
    print("===========================")

    root_dir = _UET_REPO_ROOT / "docs" / "topics"
    data_files = []

    # 1. Walk through all topic directories
    for topic_dir in root_dir.iterdir():
        if topic_dir.is_dir() and (
            topic_dir.name[0].isdigit() or topic_dir.name.startswith("0.")
        ):
            data_dir = topic_dir / "Data"
            if data_dir.exists():
                for r, d, f in os.walk(data_dir):
                    for file in f:
                        if file.endswith(".py") or file.endswith(".pyc"):
                            continue
                        full_path = Path(r) / file
                        size_kb = full_path.stat().st_size / 1024
                        data_files.append(
                            {
                                "topic": topic_dir.name,
                                "file": file,
                                "size_kb": size_kb,
                                "path": str(full_path),
                            }
                        )

    # 2. Analyze Findings
    print(f"\nFound {len(data_files)} data files across topics.\n")

    # Group by Topic
    files_by_topic = {}
    for item in data_files:
        t = item["topic"]
        if t not in files_by_topic:
            files_by_topic[t] = []
        files_by_topic[t].append(item)

    for topic in sorted(files_by_topic.keys()):
        print(f"📂 {topic}")
        files = files_by_topic[topic]
        real_data_count = 0
        mock_data_count = 0

        for f in files:
            # Heuristic for "Real Data"
            is_real = f["size_kb"] > 10.0 or f["file"].endswith(
                (".csv", ".fits", ".mrt", ".json")
            )
            marker = "✅" if is_real else "⚠️"
            if is_real:
                real_data_count += 1
            else:
                mock_data_count += 1

            print(f"  {marker} {f['file']:<40} | {f['size_kb']:>6.1f} KB")

        if real_data_count == 0 and len(files) > 0:
            print("  🚨 WARNING: No significant data files found!")
        print("")

    # 3. Recommendations
    print("\n📋 AUDIT SUMMARY")
    print("----------------")
    print("Topics with potentially insufficient data:")
    for topic in sorted(files_by_topic.keys()):
        files = files_by_topic[topic]
        if all(f["size_kb"] < 5.0 for f in files):
            print(f"  - {topic} (All files < 5KB)")


if __name__ == "__main__":
    audit_data_sources()
