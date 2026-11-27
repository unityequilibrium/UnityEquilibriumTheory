import json
import runpy
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from docs.scripts.core.runners.uet_glass_box import UETLedger, UETMetricLogger, UETPathManager
from docs.scripts.maintenance import cleanup_outputs
from docs.scripts.maintenance.log import reset_topic_logs


def test_result_routes(tmp_path, monkeypatch):
    topic = tmp_path / "topics/0.4_Superconductivity_Superfluids"
    topic.mkdir(parents=True)
    monkeypatch.setattr(UETPathManager, "_ROOT", tmp_path)
    before = set(tmp_path.rglob("*"))
    with pytest.raises(ValueError):
        UETPathManager.get_result_dir("0.400", "example")
    assert set(tmp_path.rglob("*")) == before
    for cwd in (tmp_path, topic, tmp_path.parent):
        monkeypatch.chdir(cwd)
        def write_run(_):
            logger = UETMetricLogger("sample", topic_id="0.4")
            logger.set_metadata({"fixture": 1})
            return Path(logger.save_report())
        with ThreadPoolExecutor(2) as pool:
            runs = list(pool.map(write_run, range(2)))
        assert runs[0] != runs[1]
        for run in runs:
            assert run.parent == topic / "Result/_Logs"
            assert json.loads((run / "summary.json").read_text())["metadata"]["fixture"] == 1
    generic = UETMetricLogger("generic")
    generic.save_report()
    assert UETLedger().rebuild()["run_id"].tolist() == [generic.run_id]
    external = tmp_path / "chosen"
    assert UETMetricLogger("explicit", output_dir=external).run_dir == external
    legacy = UETMetricLogger("explicit", output_dir="docs/topics/0.4_Superconductivity_Superfluids/Result/_Logs/fixture")
    assert legacy.run_dir == topic / "Result/_Logs/fixture"
    assert not (tmp_path / "docs").exists()
    for kind, folder in (("figures", "02_Figures"), ("showcase", "01_Showcase")):
        assert UETPathManager.get_result_dir("0.4", "example", category=kind) == topic / "Result" / folder


def test_reviewed_cleanup(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text("__pycache__/\n_Logs/\n")
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    (cache / "cached.pyc").touch()
    (cache / "important.json").touch()
    monkeypatch.setattr(cleanup_outputs, "ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["cleanup"])
    cleanup_outputs.main()
    assert (cache / "cached.pyc").exists()
    monkeypatch.setattr(sys, "argv", ["cleanup", "--apply"])
    cleanup_outputs.main()
    assert list(cache.iterdir()) == [cache / "important.json"]

    topics = tmp_path / "topics"
    logs = topics / "0.4_Fixture/Result/_Logs"
    monkeypatch.setattr(reset_topic_logs, "ROOT", tmp_path)
    monkeypatch.setattr(reset_topic_logs, "TOPICS", topics)
    reviewed = set()
    for name in ["123_selected", "124_retained", "125_tracked", "126_unknown"]:
        folder = logs / name
        folder.mkdir(parents=True)
        (folder / "summary.json").write_text(json.dumps(dict(run_id=name, simulation="fixture")))
        if name != "124_retained":
            reviewed.add(folder.relative_to(tmp_path).as_posix())
    (logs / "126_unknown/evidence.json").touch()
    subprocess.run(["git", "add", "-f", "topics/0.4_Fixture/Result/_Logs/125_tracked/summary.json"], cwd=tmp_path, check=True)
    preview = reset_topic_logs.LogResetter()
    preview.reset_topic("0.4")
    report = preview.generate_report()
    assert report["deleted_count"] == 0
    assert len(report["preview_items"]) == 2
    assert len(list(logs.iterdir())) == 4
    reset_topic_logs.LogResetter(dry_run=False, reviewed_runs=reviewed).reset_topic("0.4", force=True)
    assert sorted(p.name for p in logs.iterdir()) == ["124_retained", "125_tracked", "126_unknown"]
