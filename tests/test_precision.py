"""Binding constraints at repeating Decimal quotients."""
from decimal import Decimal as D
import unittest
from router.core import recommend


class PrecisionTests(unittest.TestCase):
    def scenario(self, fee, annual, budget, target):
        return {'fee_fraction': D(fee), 'btc_usd': D(1), 'target_net_usd': D(target),
                'annual_dividend_budget_usd': D(budget), 'limits_usd': {'STRK': D(10000)},
                'yields': {'STRK': D(annual)}}

    def result(self, scenario):
        return recommend(scenario, {'STRK': {'capacity_usd': D(10000), 'sources': []}})

    def test_budget_does_not_round_above_bound(self):
        result = self.result(self.scenario('0', '.14', '2', '10000'))
        self.assertLessEqual(result['allocations'][0]['annual_dividend_usd'], D(2))
        self.assertGreaterEqual(result['dividend_budget_remaining_usd'], 0)

    def test_sub_attodollar_residual_is_filled_but_reported(self):
        result = self.result(self.scenario('.1', '.3', '1000', '1'))
        self.assertEqual(result['status'], 'filled')
        self.assertLessEqual(result['unfilled_net_usd'], D('1e-18'))
        self.assertLessEqual(result['allocations'][0]['net_usd'], D(1))
