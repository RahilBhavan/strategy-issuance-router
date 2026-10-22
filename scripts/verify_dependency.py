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
    contract_raw = (upstream / 'data/contract.json').read_bytes()
    if hashlib.sha256(contract_raw).hexdigest() != meta['upstream_contract_sha256']:
        raise ValueError('upstream contract hash differs')
    contract = json.loads(contract_raw)
    if contract['schema_version'] != '1.0.0':
        raise ValueError('unsupported ledger schema version')
    for name, expected in meta['files'].items():
        raw = (upstream / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected['upstream_sha256']:
            raise ValueError(f'upstream hash differs: {name}')
        if contract['tables'][Path(name).stem]['sha256'] != expected['upstream_sha256']:
            raise ValueError(f'contract/table hash differs: {name}')
        rows = list(csv.DictReader(raw.decode().splitlines()))
        selected = [r for r in rows if r['period_end'] in meta['selection_period_ends']]
        with (FIXTURE / name).open() as f:
            if selected != list(csv.DictReader(f)):
                raise ValueError(f'selected rows differ: {name}')
    source_manifest = json.loads((FIXTURE / 'data/source-manifest.json').read_text())
    with (upstream / 'data/raw/manifest.csv').open() as f:
        upstream_sources = list(csv.DictReader(f))
    if any(row not in upstream_sources for row in source_manifest):
        raise ValueError('selected source manifest differs')
    print('Pinned commit, v1.0.0 contract, artifact hashes, selected rows and source manifest match.')


if __name__ == '__main__':
    verify(Path(sys.argv[1]))
