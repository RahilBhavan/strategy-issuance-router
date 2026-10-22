import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal as D
from router import io
from router.core import recommend
from router.__main__ import evaluate

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'fixtures/ledger-v1'


class RouterTests(unittest.TestCase):
    def setUp(self):
        self.s = io.scenario(ROOT / 'examples/synthetic.json')
        self.weeks, self.inst = io.read_ledger(LEDGER)
        self.caps = io.capacities(self.inst, self.s['decision_date'])

    def test_real_capacity_excludes_later_filings(self):
        self.assertTrue(self.caps)
        for cap in self.caps.values():
            for r in cap['sources']:
                self.assertLessEqual(r['filed'], '2026-10-09')
                self.assertNotIn('20261019', r['url'])

    def test_real_actual_comparison(self):
        out = evaluate(self.s, self.weeks, self.inst)
        actual = {r['ticker']: r['actual_net_usd'] for r in out['comparison']}
        self.assertEqual(actual['MSTR'], D(22000000))
        self.assertEqual(actual['STRC'], 0)
        self.assertEqual(out['target_actual_filed'], '2026-10-19')

    def test_future_actual_changes_do_not_change_recommendation(self):
        before = evaluate(self.s, self.weeks, self.inst)['recommendation']
        changed = copy.deepcopy(self.inst)
        for r in changed:
            if r['filed'] > self.s['decision_date']:
                r['amount_usd'] = '999999999999'
                r['available_usd'] = '0'
        self.assertEqual(before, evaluate(self.s, self.weeks, changed)['recommendation'])

    def test_budget_limits_target_and_capacity(self):
        out = recommend(self.s, self.caps)
        allocations = out['allocations']
        self.assertEqual(sum(r['net_usd'] for r in allocations), self.s['target_net_usd'])
        self.assertLessEqual(sum(r['annual_dividend_usd'] for r in allocations), D(2000000))
        for r in allocations:
            self.assertLessEqual(r['gross_usd'], self.caps[r['ticker']]['capacity_usd'])
            self.assertLessEqual(r['gross_usd'], self.s['limits_usd'][r['ticker']])
        self.assertEqual([(r['ticker'], r['binding_constraint']) for r in allocations],
                         [('MSTR', 'user_limit'), ('STRK', 'target')])

    def test_zero_budget_allows_only_common(self):
        self.s['annual_dividend_budget_usd'] = D(0)
        out = recommend(self.s, self.caps)
        self.assertEqual([r['ticker'] for r in out['allocations']], ['MSTR'])
        self.assertGreater(out['unfilled_net_usd'], 0)

    def test_missing_yield_is_exposed(self):
        del self.s['yields']['STRK']
        out = recommend(self.s, self.caps)
        self.assertEqual(out['status'], 'incomplete_inputs')
        self.assertIn('STRK.annual_cash_yield', out['missing_market_inputs'])
        self.assertNotIn('STRK', [r['ticker'] for r in out['allocations']])

    def test_common_missing_mnav(self):
        del self.s['mnav']
        self.assertIn('MSTR.mnav', recommend(self.s, self.caps)['missing_market_inputs'])

    def test_no_lookahead_for_decision_inside_week(self):
        self.s['decision_date'] = '2026-10-12'
        with self.assertRaisesRegex(ValueError, 'strictly before'):
            evaluate(self.s, self.weeks, self.inst)

    def test_forward_week_decision_inside_assumed_week_refused(self):
        self.s['period_end'] = '2026-10-25'
        self.s['decision_date'] = self.s['market_as_of'] = '2026-10-19'
        with self.assertRaisesRegex(ValueError, r'strictly before the target period starts \(2026-10-19\)'):
            evaluate(self.s, self.weeks, self.inst)

    def test_negative_nonfinite_and_boolean_numbers(self):
        for value in ('NaN', 'Infinity', '-1', True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                io.number(value, 'test')

    def test_invalid_scenario_boundary(self):
        original = json.loads((ROOT / 'examples/synthetic.json').read_text())
        scratch = Path.home() / 'scratch/strategy-issuance-router'
        scratch.mkdir(parents=True, exist_ok=True)
        for patch in ({'market_as_of': '2026-10-19'}, {'fee_fraction': 1}, {'btc_usd': 0},
                      {'yields': {'STRC': 12}}, {'limits_usd': {'UNKNOWN': 1}}, {'decision_date': '2026-02-30'}):
            with self.subTest(patch=patch), tempfile.TemporaryDirectory(dir=scratch) as temp:
                p = Path(temp) / 'input.json'; p.write_text(json.dumps(original | patch))
                with self.assertRaises(ValueError):
                    io.scenario(p)

    def test_reproducible_cli(self):
        cmd = [sys.executable, '-m', 'router', '--scenario', 'examples/synthetic.json']
        a = subprocess.check_output(cmd, cwd=ROOT)
        self.assertEqual(a, subprocess.check_output(cmd, cwd=ROOT))
        self.assertEqual(a, (ROOT / 'examples/result.json').read_bytes())

    def test_duplicate_ledger_rejected(self):
        scratch = Path.home() / 'scratch/strategy-issuance-router'
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as temp:
            data = Path(temp) / 'data'; data.mkdir()
            for name in ('weekly.csv', 'instrument_weekly.csv'):
                source = (LEDGER / 'data' / name).read_text()
                if name.startswith('instrument'):
                    source += source.splitlines()[1]+'\n'
                (data / name).write_text(source)
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                io.read_ledger(temp)

    def test_btc_price_changes_units_not_allocation(self):
        before = recommend(self.s, self.caps)
        self.s['btc_usd'] *= 2
        after = recommend(self.s, self.caps)
        for a, b in zip(before['allocations'], after['allocations']):
            self.assertEqual(a['net_usd'], b['net_usd'])
            self.assertAlmostEqual(a['btc_acquired_scenario'] / 2, b['btc_acquired_scenario'])

    def test_missing_capacity_explicit(self):
        out = recommend(self.s, {})
        self.assertEqual(out['status'], 'incomplete_inputs')
        self.assertEqual(out['missing_capacity'], sorted(self.s['limits_usd']))
        self.assertEqual(out['allocations'], [])

    def test_missing_actual_is_null_not_zero(self):
        inst = [r for r in self.inst if r['period_end'] != self.s['period_end']]
        out = evaluate(self.s, self.weeks, inst)
        self.assertTrue(out['comparison'])
        self.assertTrue(all(r['actual_net_usd'] is None for r in out['comparison']))

    def test_zero_capacity_keeps_target_unfilled(self):
        caps = copy.deepcopy(self.caps)
        for cap in caps.values():
            cap['capacity_usd'] = D(0)
        out = recommend(self.s, caps)
        self.assertEqual(out['allocations'], [])
        self.assertEqual(out['unfilled_net_usd'], self.s['target_net_usd'])

    def test_invalid_week_chronology_rejected(self):
        scratch = Path.home() / 'scratch/strategy-issuance-router'
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as temp:
            data = Path(temp) / 'data'; data.mkdir()
            for name in ('weekly.csv', 'instrument_weekly.csv'):
                text = (LEDGER / 'data' / name).read_text()
                if name == 'weekly.csv':
                    text = text.replace('2026-10-12', '2099-01-01')
                (data / name).write_text(text)
            with self.assertRaisesRegex(ValueError, 'chronology'):
                io.read_ledger(temp)

    def test_json_decimal_precision_preserved(self):
        original = (ROOT / 'examples/synthetic.json').read_text()
        scratch = Path.home() / 'scratch/strategy-issuance-router'
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as temp:
            path = Path(temp) / 'scenario.json'
            path.write_text(original.replace('25000000,', '9007199254740993.01,', 1))
            self.assertEqual(io.scenario(path)['target_net_usd'], D('9007199254740993.01'))
