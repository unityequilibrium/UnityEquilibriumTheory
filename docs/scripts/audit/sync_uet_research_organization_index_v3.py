"""Generate the organization index after the first physical migration wave."""

from __future__ import annotations

import json
import importlib.util
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
MIGRATION = CORE / "00_governance" / "uet_core_physical_migration_manifest.json"
REGISTRY = CORE / "07_artifacts" / "gates" / "uet_research_organization_registry.json"
INDEX = CORE / "00_governance" / "CORE_RESEARCH_ORGANIZATION_INDEX.md"


def main() -> int:
    source = ROOT / "docs" / "scripts" / "audit" / "reconcile_uet_core_registry_v4.py"
    spec = importlib.util.spec_from_file_location("uet_core_registry_reconcile", source)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load canonical generator: {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    outputs = module.build()
    module.write_outputs(outputs)
    print(json.dumps({
        "status": outputs["audit"]["status"],
        "index": str(module.ORGANIZATION_INDEX_PATH.relative_to(ROOT)).replace("\\", "/"),
        "registry": str(module.canonical_organization_registry_path().relative_to(ROOT)).replace("\\", "/"),
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
