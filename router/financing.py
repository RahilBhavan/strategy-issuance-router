"""Pure comparisons of financing policies using one validated scenario."""
from decimal import Decimal as D
from .core import FILL_TOLERANCE_USD, recommend


def summarize(scenario, capacities, result):
    rows = result['allocations']
    total = lambda key: sum((r[key] for r in rows), D(0))
    gross, net = total('gross_usd'), total('net_usd')
    common_gross = sum((r['gross_usd'] for r in rows if r['ticker'] == 'MSTR'), D(0))
    annual = total('annual_dividend_usd')
    new_shares = (common_gross / scenario['common_share_price_usd']
                  if 'common_share_price_usd' in scenario else None)
    ownership = (new_shares / (scenario['common_shares_outstanding'] + new_shares)
                 if new_shares is not None else None)
    constraints = []
    for ticker, limit in sorted(scenario['limits_usd'].items()):
        cap = capacities.get(ticker)
        used = sum((r['gross_usd'] for r in rows if r['ticker'] == ticker), D(0))
        constraints.append({
            'ticker': ticker, 'gross_issued_usd': used, 'user_gross_limit_usd': limit,
            'user_limit_remaining_usd': limit - used,
            'disclosed_gross_capacity_usd': cap['capacity_usd'] if cap else None,
            'capacity_remaining_usd': cap['capacity_usd'] - used if cap else None,
            'capacity_evidence': cap['sources'] if cap else [],
        })
    return {
        'funded_net_usd': net, 'gross_issued_usd': gross,
        'fees_usd': total('gross_usd') * scenario['fee_fraction'],
        'common_nav_claim_usd': total('nav_claim_usd'),
        'preferred_dividend_pv_usd': total('dividend_pv_usd'),
        'strk_conversion_value_usd': total('conversion_value_usd'),
        'claim_value_usd': total('claim_value_usd'),
        'claim_value_per_funded_net_dollar': total('claim_value_usd') / net if net else None,
        'annual_preferred_cash_expense_usd': annual,
        'new_common_shares': new_shares,
        'new_common_ownership_fraction': ownership,
        'constraints': constraints,
    }


def compare_financing(scenario, capacities):
    enabled = set(scenario['limits_usd'])
    policies = [('router', enabled), ('common_only', enabled & {'MSTR'}),
                ('preferred_only', enabled - {'MSTR'})]
    policies += [(f'{ticker}_only', {ticker}) for ticker in sorted(enabled - {'MSTR'})]
    alternatives = []
    for name, tickers in policies:
        restricted = scenario | {'limits_usd': {t: scenario['limits_usd'][t] for t in sorted(tickers)}}
        result = recommend(restricted, capacities)
        alternatives.append({'policy': name, 'result': result,
                             'metrics': summarize(restricted, capacities, result)})
    router = alternatives[0]
    for alternative in alternatives:
        # Claim-value differences across partial/incomplete funding are not savings.
        comparable = all(a['result']['status'] == 'filled' and
                         a['result']['unfilled_net_usd'] <= FILL_TOLERANCE_USD
                         for a in (router, alternative))
        alternative['full_target_comparable_with_router'] = comparable
        alternative['claim_value_excess_over_router_usd'] = (
            alternative['metrics']['claim_value_usd'] - router['metrics']['claim_value_usd'] if comparable else None)
    return {
        'basis': 'Same target, cutoff, markets, fee, limits, dividend budget and disclosed capacities; only eligible tickers change.',
        'caveat': 'Claim values are present values under the scenario discount rate and STRK conversion inputs; '
                  'fees are separate and reduce funding. Claim-value excess is a model difference, not realized savings.',
        'dilution_basis': 'New common shares / post-issue common shares at assumed execution price; excludes preferred conversions. Null without price and pre-issue shares.',
        'alternatives': alternatives,
    }
