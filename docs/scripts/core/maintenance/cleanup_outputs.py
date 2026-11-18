"""Compatibility entrypoint for the shared cache cleanup command."""

import runpy
from pathlib import Path

if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).resolve().parents[2] / 'maintenance' / 'cleanup_outputs.py'), run_name='__main__')
