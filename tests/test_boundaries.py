"""CSV contract and offline snapshot integrity regressions."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from router import io

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'fixtures/ledger-v1'


class BoundaryTests(unittest.TestCase):
    def test_snapshot_hashes_and_rows(self):
        meta = json.loads((FIXTURE / 'provenance.json').read_text())
        for name, expected in meta['files'].items():
            raw = (FIXTURE / name).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), expected['sha256'])
            self.assertEqual(len(list(csv.DictReader(raw.decode().splitlines()))), expected['rows'])
        raw = (FIXTURE / 'data/source-manifest.json').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), meta['source_manifest_sha256'])

    def test_bad_week_instrument_join_rejected(self):
        scratch = Path.home() / 'scratch/strategy-issuance-router'
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as temp:
            data = Path(temp) / 'data'; data.mkdir()
            for name in ('weekly.csv', 'instrument_weekly.csv'):
                text = (FIXTURE / 'data' / name).read_text()
                if name == 'instrument_weekly.csv':
                    text = text.replace('2026-10-12', '2026-10-13')
                (data / name).write_text(text)
            with self.assertRaisesRegex(ValueError, 'join'):
                io.read_ledger(temp)

    def test_cli_decimal_range_failure_is_diagnostic(self):
        scratch = Path.home() / 'scratch/strategy-issuance-router'
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as temp:
            data = json.loads((ROOT / 'examples/synthetic.json').read_text())
            data['btc_usd'] = '1e-999999999'
            path = Path(temp) / 'bad.json'; path.write_text(json.dumps(data))
            result = subprocess.run([sys.executable, '-m', 'router', '--scenario', str(path)],
                                    cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, '')
            self.assertNotIn('Traceback', result.stderr)
            self.assertIn('error:', result.stderr)
