"""Legacy profile-threshold wrapper; not a physical simulation."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from topics._profile_thresholds import profile_cli, run_profile_check

topic_path = Path(__file__).resolve().parents[2]


def run_simulation(*, output_dir=None):
    return run_profile_check(topic_path, "empirical_automation_profile.json", output_dir=output_dir)


if __name__ == "__main__":
    raise SystemExit(profile_cli(run_simulation))
