import sys
import os
from pathlib import Path

TOPICS = Path(r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.9.0\docs\topics")


def find_all_tests():
    tests = []
    seen_paths = set()
    grid_folders = ["01_Engine", "02_Proof", "03_Research", "04_Competitor"]

    for topic_dir in TOPICS.iterdir():
        if not topic_dir.is_dir() or not topic_dir.name.startswith("0."):
            continue
        code_dir = topic_dir / "Code"
        if code_dir.exists():
            for grid_folder in grid_folders:
                folder = code_dir / grid_folder
                if folder.exists():
                    for py_file in folder.glob("*.py"):
                        if py_file.name.startswith("__"):
                            continue
                        if py_file not in seen_paths:
                            seen_paths.add(py_file)
                            tests.append({"path": py_file, "solution": topic_dir.name})

    for extra_file in TOPICS.rglob("*.py"):
        if extra_file in seen_paths or extra_file.name.startswith("__"):
            continue
        is_valid = (
            extra_file.name.startswith("Engine_")
            or extra_file.name.startswith("Proof_")
            or extra_file.name.startswith("Research_")
            or extra_file.name.startswith("Competitor_")
        )
        if is_valid:
            solution = extra_file.relative_to(TOPICS).parts[0]
            tests.append({"path": extra_file, "solution": solution})
    return tests


targets = [
    "Research_Quantum_Mechanics",
    "Research_Quantum_Tunneling",
    "Research_Cosmological_Constant",
    "Research_Oscillation_4D",
]

for t in find_all_tests():
    if any(target in t["path"].name for target in targets):
        print(f"{t['solution']} | {t['path']}")
