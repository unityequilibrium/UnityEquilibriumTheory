"""Regression checks for the root-level Core migration boundary."""

from __future__ import annotations

import subprocess
import re
import sys
from pathlib import Path

from core.core_paths import canonical_existing_path, canonical_path_for


ROOT = Path(__file__).resolve().parents[2]


def test_historical_core_and_topic_locators_resolve_without_rewriting_them() -> None:
    old_core = "docs/core/02_equations/covariant/uet_covariant_response.py"
    old_topic = "docs/topics/0.10_Fluid_Dynamics_Chaos/CORE_O2_GOLDSTONE_CURRENT_BOUND.md"

    assert canonical_path_for(old_core) == "core/02_equations/covariant/uet_covariant_response.py"
    assert canonical_path_for(old_topic) == "topics/0.10_Fluid_Dynamics_Chaos/CORE_O2_GOLDSTONE_CURRENT_BOUND.md"
    assert canonical_existing_path(ROOT / old_core) == ROOT / canonical_path_for(old_core)
    assert canonical_existing_path(ROOT / old_topic) == ROOT / canonical_path_for(old_topic)
    assert canonical_existing_path(ROOT / old_core).is_file()
    assert canonical_existing_path(ROOT / old_topic).is_file()
    # The caller's original identity remains a historical locator; resolution is a read-path view.
    assert old_core.startswith("docs/core/")
    assert old_topic.startswith("docs/topics/")


def test_legacy_and_current_core_import_orders_share_one_module_object() -> None:
    snippets = (
        "import core, docs.core; assert core is docs.core; "
        "import core.uet_parameters, docs.core.uet_parameters; "
        "assert core.uet_parameters is docs.core.uet_parameters",
        "import docs.core, core; assert core is docs.core; "
        "import docs.core.uet_parameters, core.uet_parameters; "
        "assert core.uet_parameters is docs.core.uet_parameters",
    )
    for snippet in snippets:
        completed = subprocess.run(
            [sys.executable, "-c", snippet], cwd=ROOT, capture_output=True, text=True,
        )
        assert completed.returncode == 0, completed.stdout + completed.stderr


def test_numbered_packages_share_implementation_in_both_import_orders() -> None:
    for old_first in (True, False):
        names = ["docs.core.03_lanes.carrier_observer.photon_observer_baseline",
                 "core.03_lanes.carrier_observer.photon_observer_baseline"]
        if not old_first:
            names.reverse()
        snippet = (
            "import importlib; "
            f"a=importlib.import_module({names[0]!r}); "
            f"b=importlib.import_module({names[1]!r}); "
            "assert a is b; assert a.PhotonBaselineConfig is b.PhotonBaselineConfig; "
            "a._layout_test_state=object(); assert b._layout_test_state is a._layout_test_state"
        )
        completed = subprocess.run([sys.executable, "-c", snippet], cwd=ROOT,
                                   capture_output=True, text=True)
        assert completed.returncode == 0, completed.stdout + completed.stderr


def test_absent_raw_source_locator_can_be_mapped_without_fabricating_presence(tmp_path) -> None:
    legacy = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/missing_fixture.pdf"
    current = canonical_path_for(legacy)
    assert current == legacy.removeprefix("docs/")
    assert not (tmp_path / current).exists()
    assert legacy.startswith("docs/topics/")


def test_moved_raw_and_core_standard_paths_keep_checkout_protections() -> None:
    paths = [
        "topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/qh15_materialscloud/README.txt",
        "topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/qh15_materialscloud/raw_data/fixture.csv",
        "topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/qh15_materialscloud/fig1_temp_inversion/fig1_temp_inversion.nb",
        "core/AGENTS.md", "core/THEORY_CARD.md", "core/theory_card.json",
        "core/UPDATE_LOG.md", "core/05_tests/physics/fixture.py",
    ]
    completed = subprocess.run(["git", "check-attr", "-z", "text", "eol", "--", *paths],
                               cwd=ROOT, capture_output=True, check=True)
    fields = completed.stdout.decode("utf-8").rstrip("\0").split("\0")
    attrs = {(fields[i], fields[i + 1]): fields[i + 2] for i in range(0, len(fields), 3)}
    for path in paths[:3]:
        assert attrs[path, "text"] == "unset"
    for path in paths[3:]:
        assert attrs[path, "text"] == "set"
        assert attrs[path, "eol"] == "lf"


def test_ci_research_detection_includes_checkout_and_ignore_rules() -> None:
    workflow = (ROOT / ".github/workflows/pr-validation.yml").read_text(encoding="utf-8")
    match = re.search(r"set_output research '([^']+)'", workflow)
    assert match is not None
    pattern = re.compile(match.group(1))
    for path in (".gitattributes", ".gitignore", "core/02_equations/example.py", "topics/0.13_Thermodynamic_Bridge/Code/example.py"):
        assert pattern.search(path), path
