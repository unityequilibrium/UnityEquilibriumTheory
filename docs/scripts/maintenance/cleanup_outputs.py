"""Preview ignored Python caches; --apply removes them. Research outputs are retained."""

import argparse
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    tracked = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    paths = []
    tracked_set = set(tracked)
    for directory, children, _ in os.walk(ROOT):
        base = Path(directory)
        children[:] = [name for name in children
                       if name not in {'.git', '.venv', 'raw', '1_raw', 'For Work', 'tmp', '.uet-run-reports'}
                       and (base / name).resolve() == base / name]
        if '__pycache__' in children:
            children.remove('__pycache__')
            cache = base / '__pycache__'
            paths.extend(p for p in cache.glob('*.pyc') if p.is_file() and p.resolve() == p
                         and p.relative_to(ROOT).as_posix() not in tracked_set)
    if paths:
        query = b'\0'.join(os.fsencode(p.relative_to(ROOT).as_posix()) for p in paths) + b'\0'
        check = subprocess.run(['git', '-c', 'core.fsmonitor=false', 'check-ignore', '-z', '--stdin'],
                               input=query, capture_output=True, cwd=ROOT)
        if check.returncode not in (0, 1):
            raise RuntimeError(os.fsdecode(check.stderr))
        ignored = set(check.stdout.split(b'\0'))
        paths = [p for p in paths if os.fsencode(p.relative_to(ROOT).as_posix()) in ignored]
    if args.apply:
        for path in paths:
            path.unlink()
        for directory in {p.parent for p in paths}:
            if not any(directory.iterdir()):
                directory.rmdir()
    print(json.dumps({'applied': args.apply, 'caches': [str(p.relative_to(ROOT)) for p in paths], 'research_results_deleted': False}))


if __name__ == '__main__':
    main()
