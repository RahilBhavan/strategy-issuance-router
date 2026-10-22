"""Shared-assumption alternatives, hand calculations and CLI contract."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal as D
from router import io
from router.financing import compare_financing
from router.__main__ import evaluate

ROOT = Path(__file__).resolve().parents[1]


class FinancingTests(unittest.TestCase):
    def setUp(self):
        self.s = {'fee_fraction': D('.1'), 'btc_usd': D(10), 'target_net_usd': D(90),
                  'annual_dividend_budget_usd': D(10), 'mnav': D(2),
                  'limits_usd': {'MSTR': D(200), 'STRK': D(200)},
                  'yields': {'STRK': D('.1')}, 'common_share_price_usd': D(10),
                  'common_shares_outstanding': D(90)}
        self.caps = {t: {'capacity_usd': D(200), 'sources': [{'filed': '2026-10-05'}]}
                     for t in self.s['limits_usd']}

    def policies(self):
        return {a['policy']: a for a in compare_financing(self.s, self.caps)['alternatives']}

    def test_hand_calculated_cost_and_dilution(self):
        policies = self.policies()
        common = policies['common_only']['metrics']
        preferred = policies['preferred_only']['metrics']
        self.assertEqual(common['gross_issued_usd'], 100)
        self.assertEqual(common['funded_net_usd'], 90)
        self.assertEqual(common['fees_usd'], 10)
        self.assertEqual(common['common_nav_claim_proxy_usd'], 50)
        self.assertEqual(common['annual_preferred_cash_expense_usd'], 0)
        self.assertEqual(common['new_common_shares'], 10)
        self.assertEqual(common['new_common_ownership_fraction'], D('.1'))
        self.assertEqual(preferred['new_common_ownership_fraction'], 0)
        self.assertEqual(preferred['annual_preferred_cash_expense_usd'], 10)
        self.assertEqual(preferred['common_nav_claim_proxy_usd'], 0)
        self.assertEqual(policies['common_only']['proxy_excess_over_router_usd'], 40)
        self.assertEqual(preferred['constraints'][0]['capacity_remaining_usd'], 100)
        self.assertEqual(preferred['constraints'][0]['capacity_evidence'], self.caps['STRK']['sources'])

    def test_partial_fill_has_no_savings_claim(self):
        self.s['limits_usd']['MSTR'] = D(50)
        common = self.policies()['common_only']
        self.assertEqual(common['result']['unfilled_net_usd'], 45)
        self.assertFalse(common['full_target_comparable_with_router'])
        self.assertIsNone(common['proxy_excess_over_router_usd'])
        self.assertEqual(common['metrics']['constraints'][0]['user_limit_remaining_usd'], 0)

    def test_shared_budget_capacity_and_user_limits(self):
        self.s['annual_dividend_budget_usd'] = D(2)
        self.caps['MSTR']['capacity_usd'] = D(40)
        before = copy.deepcopy((self.s, self.caps))
        policies = self.policies()
        self.assertEqual(policies['router']['metrics']['funded_net_usd'], 54)
        self.assertEqual(policies['router']['result']['dividend_budget_remaining_usd'], 0)
        self.assertEqual(policies['common_only']['metrics']['funded_net_usd'], 36)
        self.assertEqual(policies['preferred_only']['metrics']['funded_net_usd'], 18)
        self.assertEqual((self.s, self.caps), before)
        for a in policies.values():
            for c in a['metrics']['constraints']:
                self.assertGreaterEqual(c['user_limit_remaining_usd'], 0)
                self.assertGreaterEqual(c['capacity_remaining_usd'], 0)

    def test_missing_inputs_are_scoped_and_not_comparable(self):
        del self.s['mnav']
        policies = self.policies()
        self.assertEqual(policies['router']['result']['status'], 'incomplete_inputs')
        self.assertEqual(policies['preferred_only']['result']['status'], 'filled')
        self.assertFalse(policies['preferred_only']['full_target_comparable_with_router'])
        del self.caps['STRK']
        single = self.policies()['STRK_only']
        self.assertEqual(single['result']['missing_capacity'], ['STRK'])
        self.assertIsNone(single['metrics']['constraints'][0]['capacity_remaining_usd'])

    def test_absent_dilution_inputs_are_null_not_estimated(self):
        del self.s['common_share_price_usd'], self.s['common_shares_outstanding']
        for a in self.policies().values():
            self.assertIsNone(a['metrics']['new_common_shares'])
            self.assertIsNone(a['metrics']['new_common_ownership_fraction'])

    def test_no_enabled_preferred_and_zero_funding(self):
        self.s['limits_usd'] = {'MSTR': D(0)}
        preferred = self.policies()['preferred_only']
        self.assertEqual(preferred['result']['status'], 'constrained')
        self.assertEqual(preferred['metrics']['funded_net_usd'], 0)
        self.assertIsNone(preferred['metrics']['proxy_per_funded_net_dollar'])
        self.assertFalse(preferred['full_target_comparable_with_router'])

    def test_no_lookahead_in_all_alternatives(self):
        s = io.scenario(ROOT / 'examples/synthetic.json')
        weeks, inst = io.read_ledger(ROOT / 'fixtures/ledger-v1')
        before = evaluate(s, weeks, inst, compare=True)['financing_comparison']
        for row in inst:
            if row['filed'] > s['decision_date']:
                row['amount_usd'] = '999999999999'
                row['available_usd'] = '0'
        self.assertEqual(before, evaluate(s, weeks, inst, compare=True)['financing_comparison'])

    def test_dilution_boundary_requires_positive_pair(self):
        original = json.loads((ROOT / 'examples/synthetic.json').read_text())
        scratch = Path.home() / 'scratch/strategy-issuance-router'
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as temp:
            path = Path(temp) / 'scenario.json'
            for price, shares in ((10, None), (None, 90), (0, 90), (10, -1), (True, 90), ('NaN', 90)):
                data = original.copy()
                if price is not None:
                    data['common_share_price_usd'] = price
                if shares is not None:
                    data['common_shares_outstanding'] = shares
                path.write_text(json.dumps(data))
                with self.subTest(price=price, shares=shares), self.assertRaises(ValueError):
                    io.scenario(path)
            path.write_text(json.dumps(original | {'common_share_price_usd': '10',
                                                  'common_shares_outstanding': '90'}))
            self.assertEqual(io.scenario(path)['common_share_price_usd'], D(10))

    def test_comparison_cli_is_deterministic_and_preserves_recommendation(self):
        cmd = [sys.executable, '-m', 'router', '--scenario', 'examples/synthetic.json', '--compare-financing']
        first = subprocess.check_output(cmd, cwd=ROOT)
        self.assertEqual(first, subprocess.check_output(cmd, cwd=ROOT))
        output = json.loads(first)
        self.assertEqual(output['recommendation'], json.loads((ROOT / 'examples/result.json').read_text())['recommendation'])
        policies = {a['policy']: a for a in output['financing_comparison']['alternatives']}
        self.assertEqual(len(policies), 7)
        for name, funded in (('router', '25000000'), ('common_only', '24875000'),
                             ('preferred_only', '21890000')):
            self.assertEqual(D(policies[name]['metrics']['funded_net_usd']), D(funded))
        self.assertTrue(all(a['proxy_excess_over_router_usd'] is None
                            for name, a in policies.items() if name != 'router'))
