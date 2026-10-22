"""Consistent claim-value basis, STRK conversion cost, mNAV gate and forward-looking mode."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal as D
from statistics import NormalDist
import math
from router import io
from router.core import recommend
from router.__main__ import evaluate

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'fixtures/ledger-v1'
SCRATCH = Path.home() / 'scratch/strategy-issuance-router'


def independent_strk_cost(spot, vol, years, rate, annual_yield):
    """Conversion value per gross dollar, written from the Black-Scholes formula directly."""
    n = NormalDist().cdf
    d1 = (math.log(spot / 1000) + (rate + vol ** 2 / 2) * years) / (vol * years ** 0.5)
    call = spot * n(d1) - 1000 * math.exp(-rate * years) * n(d1 - vol * years ** 0.5)
    return 0.1 * call / (8 / annual_yield)


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.s = io.scenario(ROOT / 'examples/synthetic.json')
        self.weeks, self.inst = io.read_ledger(LEDGER)
        self.caps = io.capacities(self.inst, self.s['decision_date'])

    def ranking(self, scenario=None):
        return {r['ticker']: r for r in recommend(scenario or self.s, self.caps)['ranking']}

    def cli(self, data, *args):
        SCRATCH.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=SCRATCH) as temp:
            path = Path(temp) / 'scenario.json'
            path.write_text(json.dumps(data))
            return subprocess.run([sys.executable, '-m', 'router', '--scenario', str(path), *args],
                                  cwd=ROOT, capture_output=True, text=True)

    def test_every_instrument_uses_present_value_of_claims_per_net_dollar(self):
        rank = self.ranking()
        net = 1 - 0.005
        self.assertAlmostEqual(float(rank['MSTR']['cost_per_net_dollar']), (1 / 1.2) / net, places=12)
        self.assertAlmostEqual(float(rank['STRF']['cost_per_net_dollar']), (0.10 / 0.10) / net, places=12)
        self.assertAlmostEqual(float(rank['STRC']['cost_per_net_dollar']), (0.12 / 0.10) / net, places=12)
        conversion = independent_strk_cost(200, 0.6, 10, 0.045, 0.08)
        self.assertAlmostEqual(float(rank['STRK']['claim_per_gross_dollar']['conversion_value']), conversion, places=10)
        self.assertAlmostEqual(float(rank['STRK']['cost_per_net_dollar']), (0.8 + conversion) / net, places=10)
        self.assertEqual(list(rank), ['MSTR', 'STRK', 'STRD', 'STRF', 'STRC'])

    def test_strk_without_conversion_inputs_is_missing_not_cheapest(self):
        del self.s['strk_conversion']
        out = recommend(self.s, self.caps)
        self.assertIn('STRK.strk_conversion', out['missing_market_inputs'])
        self.assertEqual(out['status'], 'incomplete_inputs')
        self.assertNotIn('STRK', [r['ticker'] for r in out['ranking']])

    def test_conversion_cost_rises_with_mstr_price_and_volatility(self):
        costs = []
        for spot, vol in ((200, '.6'), (400, '.6'), (400, '.9')):
            self.s['strk_conversion'] |= {'mstr_price_usd': D(spot), 'volatility': D(vol)}
            costs.append(self.ranking()['STRK']['cost_per_net_dollar'])
        self.assertLess(costs[0], costs[1])
        self.assertLess(costs[1], costs[2])
        self.assertGreater(costs[2], self.ranking()['STRF']['cost_per_net_dollar'])

    def test_discount_rate_above_break_even_puts_preferreds_first(self):
        out = recommend(self.s, self.caps)
        self.assertAlmostEqual(float(out['break_even_discount_rate_vs_common']['STRF']), 0.10 / (1 / 1.2), places=12)
        self.s['perpetual_discount_rate'] = D('.13')
        tickers = [r['ticker'] for r in recommend(self.s, self.caps)['allocations']]
        self.assertEqual(tickers[:3], ['STRK', 'STRD', 'STRF'])

    def test_common_below_nav_warns_by_default_and_can_be_blocked(self):
        self.s['mnav'] = D('.95')
        out = recommend(self.s, self.caps)
        self.assertEqual([(r['ticker'], r['binding_constraint']) for r in out['allocations']],
                         [('STRK', 'user_limit'), ('STRD', 'user_limit'), ('STRF', 'dividend_budget'), ('MSTR', 'target')])
        self.assertEqual(len(out['warnings']), 1)
        self.assertIn('mNAV 0.95 (below 1)', out['warnings'][0])
        self.s['common_below_nav'] = 'block'
        blocked = recommend(self.s, self.caps)
        self.assertNotIn('MSTR', [r['ticker'] for r in blocked['allocations']])
        self.assertEqual(blocked['blocked'][0]['ticker'], 'MSTR')
        self.assertEqual(blocked['warnings'], [])
        self.assertEqual(blocked['status'], 'constrained')
        data = json.loads((ROOT / 'examples/synthetic.json').read_text()) | {'mnav': 0.95}
        self.assertIn('warning: Common issued at mNAV 0.95', self.cli(data).stderr)

    def test_forward_week_without_actuals(self):
        result = subprocess.run([sys.executable, '-m', 'router', '--scenario', 'examples/forward.json'],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('note: actual comparison not available: the ledger has no week ending 2026-11-01', result.stderr)
        out = json.loads(result.stdout)
        self.assertIsNone(out['comparison'])
        self.assertEqual(out['target_period_start'], '2026-10-26')
        self.assertEqual(out['recommendation']['status'], 'filled')
        for allocation in out['recommendation']['allocations']:
            self.assertTrue(all('20261019' in e['url'] for e in allocation['capacity_evidence']))

    def test_no_actuals_flag_keeps_the_recommendation(self):
        data = json.loads((ROOT / 'examples/synthetic.json').read_text())
        skipped = json.loads(self.cli(data, '--no-actuals').stdout)
        self.assertIsNone(skipped['comparison'])
        self.assertEqual(skipped['recommendation'],
                         json.loads((ROOT / 'examples/result.json').read_text())['recommendation'])

    def test_output_amounts_are_quantized_for_display(self):
        text = (ROOT / 'examples/result.json').read_text()
        self.assertNotIn('E-', text)
        out = json.loads(text)
        self.assertEqual(out['comparison'][0]['difference_usd'], '2875000.00')
        for row in out['recommendation']['allocations']:
            self.assertRegex(row['gross_usd'], r'^\d+\.\d{2}$')
            self.assertRegex(row['claim_value_btc'], r'^\d+\.\d{8}$')
            self.assertRegex(row['cost_per_net_dollar'], r'^\d+\.\d{6}$')

    def test_new_scenario_fields_are_validated(self):
        original = json.loads((ROOT / 'examples/synthetic.json').read_text())
        bad = [{'perpetual_discount_rate': 10}, {'perpetual_discount_rate': 0}, {'common_below_nav': 'maybe'},
               {'strk_conversion': {'mstr_price_usd': 200, 'volatility': 60, 'horizon_years': 10, 'risk_free_rate': 0.045}},
               {'strk_conversion': {'mstr_price_usd': 200, 'volatility': 0.6}}]
        SCRATCH.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=SCRATCH) as temp:
            path = Path(temp) / 'scenario.json'
            for patch in bad:
                path.write_text(json.dumps(original | patch))
                with self.subTest(patch=patch), self.assertRaises(ValueError):
                    io.scenario(path)

    def test_render_check_reports_success(self):
        result = subprocess.run([sys.executable, 'scripts/render_result.py', '--check'],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('ok: figures/result.svg matches examples/result.json', result.stdout)

    def test_actuals_never_change_any_ranking_field(self):
        before = evaluate(self.s, self.weeks, self.inst)['recommendation']
        changed = copy.deepcopy(self.inst)
        for row in changed:
            if row['period_end'] == self.s['period_end']:
                row['amount_usd'] = '1'
        self.assertEqual(before, evaluate(self.s, self.weeks, changed)['recommendation'])


if __name__ == '__main__':
    unittest.main()
