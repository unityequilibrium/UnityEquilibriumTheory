"""Regression checks for the root-level Core migration boundary."""

from __future__ import annotations

import subprocess
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
