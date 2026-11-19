"""Compatibility entrypoint for the canonical topic log reset command."""
import runpy
from pathlib import Path

_source = Path(__file__).resolve().parents[3] / "maintenance" / "log" / "reset_topic_logs.py"
_module = runpy.run_path(str(_source))
LogResetter = _module["LogResetter"]
main = _module["main"]

if __name__ == "__main__":
    main()
