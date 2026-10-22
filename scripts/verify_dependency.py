"""Verify selected fixture rows against an exact restored upstream ledger commit."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'fixtures/ledger-v1'


def verify(upstream):
    meta = json.loads((FIXTURE / 'provenance.json').read_text())
    commit = subprocess.check_output(['git', '-C', str(upstream), 'rev-parse', 'HEAD'], text=True).strip()
    if commit != meta['upstream_commit']:
        raise ValueError('upstream commit differs from reviewed pin')
    for name, expected in meta['files'].items():
        raw = (upstream / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected['upstream_sha256']:
            raise ValueError(f'upstream hash differs: {name}')
        rows = list(csv.DictReader(raw.decode().splitlines()))
        selected = [r for r in rows if r['period_end'] in meta['selection_period_ends']]
        with (FIXTURE / name).open() as f:
            if selected != list(csv.DictReader(f)):
                raise ValueError(f'selected rows differ: {name}')
    print('Pinned commit, upstream artifact hashes and selected rows match.')


if __name__ == '__main__':
    verify(Path(sys.argv[1]))
