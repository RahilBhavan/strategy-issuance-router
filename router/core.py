"""Pure one-year financing-cost proxy and deterministic greedy allocation."""
from decimal import Decimal as D


def recommend(scenario, capacities):
    fee = scenario['fee_fraction']
    btc = scenario['btc_usd']
    target = scenario['target_net_usd']
    budget = scenario['annual_dividend_budget_usd']
    choices, missing, disabled = [], [], []
    for ticker, cap in sorted(capacities.items()):
        if ticker not in scenario['limits_usd']:
            disabled.append(ticker)
            continue
        if ticker == 'MSTR':
            mnav = scenario.get('mnav')
            if mnav is None:
                missing.append('MSTR.mnav')
                continue
            cost, annual = D(1) / mnav, D(0)
        else:
            annual = scenario['yields'].get(ticker)
            if annual is None:
                missing.append(f'{ticker}.annual_cash_yield')
                continue
            cost = annual
        choices.append((cost / (1-fee), ticker, cost, annual,
                        min(cap['capacity_usd'], scenario['limits_usd'][ticker])))
    allocations, remaining = [], target
    for score, ticker, cost, annual, limit in sorted(choices):
        if remaining <= 0:
            break
        gross = min(limit, remaining / (1-fee))
        if annual:
            gross = min(gross, budget / annual)
        if gross <= 0:
            continue
        net = gross * (1-fee)
        dividend = gross * annual
        allocations.append({'ticker': ticker, 'gross_usd': gross, 'net_usd': net,
                            'annual_dividend_usd': dividend, 'cost_proxy_usd': gross * cost,
                            'btc_acquired_scenario': net / btc,
                            'btc_cost_proxy': gross * cost / btc,
                            'cost_per_net_dollar': score,
                            'capacity_evidence': capacities[ticker]['sources']})
        remaining = max(D(0), remaining - net)
        budget -= dividend
    return {'objective': 'minimize one-year cost proxy per net dollar; deterministic ticker ties',
            'allocations': allocations, 'unfilled_net_usd': remaining,
            'missing_market_inputs': missing,
            'missing_capacity': sorted(set(scenario['limits_usd']) - set(capacities)), 'disabled_without_limit': disabled,
            'dividend_budget_remaining_usd': budget,
            'status': 'incomplete_inputs' if missing or set(scenario['limits_usd']) - set(capacities) else 'filled' if remaining == 0 else 'constrained'}
