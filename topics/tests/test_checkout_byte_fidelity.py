"""Checkout fidelity only: this is not scientific/physics validation."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
CODE_PATHS = (
    "core/02_equations/matter_space/example.py",
    "core/01_contracts/example.md",
    "core/07_artifacts/gates/example.json",
    "topics/0.99_Example/Code/03_Research/example.py",
    "topics/0.99_Example/Result/artifacts/example.json",
    "topics/0.99_Example/VERIFICATION_SPEC.md",
    "topics/run_all_tests.py",
    "topics/tests/test_example.py",
    "docs/scripts/audit/example.py",
)
RAW_PATHS = (
    "docs/data/external/source/example.csv",
    "core/06_data/raw/example.txt",
    "topics/0.99_Example/Data/raw/example.csv",
    "topics/0.99_Example/Data/03_Research/example.json",
    "topics/0.99_Example/Ref/PDF_Downloads/ascii.pdf",
    "topics/0.99_Example/Result/previews/first_execution_verifier.py.txt",
)


def git(root: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-c", "core.fsmonitor=false", "-C", str(root), *args],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout


@pytest.fixture(scope="module")
def checkout_fixture(tmp_path_factory):
    root = tmp_path_factory.mktemp("checkout-byte-fidelity")
    git(root, "init", "-q")
    git(root, "config", "user.name", "Software fixture")
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "config", "core.autocrlf", "true")
    (root / ".gitattributes").write_bytes((ROOT / ".gitattributes").read_bytes())
    samples = {path: b"first line\nsecond line\n" for path in CODE_PATHS}
    samples.update({path: b"raw first\r\nraw second\r\n" for path in RAW_PATHS})
    samples["core/07_artifacts/figures/example.png"] = b"\x89PNG\r\n\x1a\n\x00raw\r\npayload"
    for path, content in samples.items():
        file = root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(content)
    git(root, "add", "--", ".")
    git(root, "commit", "-qm", "fixture only")
    destination = root / "materialized"
    destination.mkdir()
    # Materialize a fresh index into a new directory: no reset, cleanup, or
    # overwrite of user files is involved, even on Windows.
    git(root, "checkout-index", "--all", f"--prefix={destination.as_posix()}/")
    return root, destination, samples


@pytest.mark.parametrize("path", CODE_PATHS)
def test_code_and_record_checkout_matches_committed_lf_bytes(checkout_fixture, path):
    root, destination, samples = checkout_fixture
    committed = git(root, "show", f"HEAD:{path}")
    assert committed == samples[path]
    assert (destination / path).read_bytes() == committed
    assert b"\r\n" not in committed


@pytest.mark.parametrize("path", RAW_PATHS)
def test_raw_and_reference_checkout_preserves_deliberate_crlf(checkout_fixture, path):
    root, destination, samples = checkout_fixture
    committed = git(root, "show", f"HEAD:{path}")
    assert committed == samples[path]
    assert (destination / path).read_bytes() == samples[path]
    assert b"\r\n" in committed


def test_binary_artifact_is_not_text_normalized(checkout_fixture):
    root, destination, samples = checkout_fixture
    path = "core/07_artifacts/figures/example.png"
    assert git(root, "show", f"HEAD:{path}") == samples[path]
    assert (destination / path).read_bytes() == samples[path]


def test_control_without_policy_reproduces_windows_conversion(tmp_path):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "core.autocrlf", "true")
    (tmp_path / "example.py").write_bytes(b"first\nsecond\n")
    git(tmp_path, "add", "example.py")
    destination = tmp_path / "materialized"
    destination.mkdir()
    git(tmp_path, "checkout-index", "--all", f"--prefix={destination.as_posix()}/")
    assert (destination / "example.py").read_bytes() == b"first\r\nsecond\r\n"
