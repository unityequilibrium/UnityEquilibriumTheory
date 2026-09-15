
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
import csv
import os
import sys

sys.path.insert(0, str(_UET_REPO_ROOT))

from docs.lab.galaxies.test_175_galaxies_v4 import SPARC_GALAXIES


def recover():
    output_path = "docs/data_vault/sources/sparc_175.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "R_kpc", "v_obs", "M_disk_Msun", "R_disk_kpc", "type"])
        writer.writerows(SPARC_GALAXIES)

    print(f"Recovered {len(SPARC_GALAXIES)} records to {output_path}")


if __name__ == "__main__":
    recover()
