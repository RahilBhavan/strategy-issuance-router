"""Present-value claim cost per net dollar and deterministic greedy allocation.

Every instrument is priced on one basis: the present value of the claims handed to new
holders for each net dollar raised (docs/method.md).

- Common: a NAV claim of 1/mNAV per gross dollar.
- Preferred: perpetual dividends capitalized at ``perpetual_discount_rate``, so yield / rate
  per gross dollar. STRK adds the Black-Scholes value of its conversion right.
"""
from decimal import Decimal as D, localcontext, ROUND_DOWN
import math


FILL_TOLERANCE_USD = D('1e-18')
DEFAULT_PERPETUAL_DISCOUNT_RATE = D('0.10')
# STRK terms: $100 stated amount, 8% annual dividend, 0.1 MSTR share per STRK ($1,000 conversion price).
STRK_ANNUAL_DIVIDEND_USD = D(8)
STRK_SHARES_PER_PREFERRED = 0.1
STRK_CONVERSION_PRICE_USD = 1000.0
BINDING_ORDER = ('target', 'dividend_budget', 'user_limit', 'disclosed_capacity')


def bounded_quotient(numerator, denominator):
    # A rounded-up quotient can exceed a binding target or dividend budget.
    with localcontext() as context:
        context.rounding = ROUND_DOWN
        return numerator / denominator


def black_scholes_call(spot, strike, years, rate, vol):
    d1 = (math.log(spot / strike) + (rate + vol * vol / 2) * years) / (vol * math.sqrt(years))
    d2 = d1 - vol * math.sqrt(years)
    n = lambda x: 0.5 * math.erfc(-x / math.sqrt(2))
    return spot * n(d1) - strike * math.exp(-rate * years) * n(d2)


def strk_conversion_cost(inputs, annual_yield):
    """Conversion-right value per gross dollar of STRK sold.

    A European call on 0.1 MSTR share struck at $1,000 over ``horizon_years`` (a finite
    stand-in for a perpetual right). The STRK price is implied by its cash yield: $8 / yield.
    Rounded to 12 significant digits so float libm differences cannot change the ranking."""
    call = black_scholes_call(float(inputs['mstr_price_usd']), STRK_CONVERSION_PRICE_USD,
                              float(inputs['horizon_years']), float(inputs['risk_free_rate']),
                              float(inputs['volatility']))
    per_preferred = D(f'{STRK_SHARES_PER_PREFERRED * call:.12g}')
    return per_preferred * annual_yield / STRK_ANNUAL_DIVIDEND_USD


def price_instruments(scenario, capacities):
    """Cost per net dollar for every enabled instrument with complete inputs."""
    fee = scenario['fee_fraction']
    rate = scenario.get('perpetual_discount_rate', DEFAULT_PERPETUAL_DISCOUNT_RATE)
    below_nav = scenario.get('common_below_nav', 'warn')
    choices, missing, disabled, blocked = [], [], [], []
    for ticker, cap in sorted(capacities.items()):
        if ticker not in scenario['limits_usd']:
            disabled.append(ticker)
            continue
        parts = {'nav_claim': D(0), 'dividend_pv': D(0), 'conversion_value': D(0)}
        annual = D(0)
        if ticker == 'MSTR':
            mnav = scenario.get('mnav')
            if mnav is None:
                missing.append('MSTR.mnav')
                continue
            if mnav < 1 and below_nav == 'block':
                blocked.append({'ticker': 'MSTR', 'mnav': mnav,
                                'reason': 'common_below_nav is block and mNAV is below 1'})
                continue
            parts['nav_claim'] = D(1) / mnav
        else:
            annual = scenario['yields'].get(ticker)
            if annual is None:
                missing.append(f'{ticker}.annual_cash_yield')
                continue
            parts['dividend_pv'] = annual / rate
            if ticker == 'STRK':
                if 'strk_conversion' not in scenario:
                    missing.append('STRK.strk_conversion')
                    continue
                if annual == 0:
                    missing.append('STRK.positive_annual_cash_yield')
                    continue
                parts['conversion_value'] = strk_conversion_cost(scenario['strk_conversion'], annual)
        per_gross = sum(parts.values(), D(0))
        choices.append({'ticker': ticker, 'cost_per_net_dollar': per_gross / (1 - fee),
                        'claim_per_gross_dollar': parts, 'annual_yield': annual,
                        'limit_usd': scenario['limits_usd'][ticker], 'capacity_usd': cap['capacity_usd']})
    choices.sort(key=lambda c: (c['cost_per_net_dollar'], c['ticker']))
    return choices, missing, disabled, blocked


def break_even_rates(scenario, choices):
    """Discount rate above which each preferred is cheaper than common (null if never)."""
    common = next((c for c in choices if c['ticker'] == 'MSTR'), None)
    out = {}
    for c in choices:
        if c['ticker'] == 'MSTR' or common is None or not c['annual_yield']:
            continue
        room = common['claim_per_gross_dollar']['nav_claim'] - c['claim_per_gross_dollar']['conversion_value']
        out[c['ticker']] = c['annual_yield'] / room if room > 0 else None
    return out


def recommend(scenario, capacities):
    fee = scenario['fee_fraction']
    btc = scenario['btc_usd']
    target = scenario['target_net_usd']
    budget = scenario['annual_dividend_budget_usd']
    choices, missing, disabled, blocked = price_instruments(scenario, capacities)
    allocations, ranking, warnings, remaining = [], [], [], target
    for choice in choices:
        ticker, annual = choice['ticker'], choice['annual_yield']
        # A residual within the fill tolerance is filled; it must not buy dust from the next instrument.
        open_target = remaining if remaining > FILL_TOLERANCE_USD else D(0)
        bounds = {'target': bounded_quotient(open_target, 1 - fee), 'user_limit': choice['limit_usd'],
                  'disclosed_capacity': choice['capacity_usd']}
        if annual:
            bounds['dividend_budget'] = bounded_quotient(budget, annual)
        gross = max(D(0), min(bounds.values()))
        binding = next(k for k in BINDING_ORDER if k in bounds and bounds[k] <= gross)
        if gross == 0 and binding == 'target':
            binding = 'target_already_filled'
        ranking.append({'ticker': ticker, 'cost_per_net_dollar': choice['cost_per_net_dollar'],
                        'claim_per_gross_dollar': choice['claim_per_gross_dollar'],
                        'gross_usd': gross, 'binding_constraint': binding})
        if gross <= 0:
            continue
        net = gross * (1 - fee)
        dividend = gross * annual
        claims = {f'{k}_usd': gross * v for k, v in choice['claim_per_gross_dollar'].items()}
        claim_value = sum(claims.values(), D(0))
        allocations.append({'ticker': ticker, 'gross_usd': gross, 'net_usd': net,
                            'annual_dividend_usd': dividend, **claims, 'claim_value_usd': claim_value,
                            'btc_acquired_scenario': net / btc,
                            'claim_value_btc': claim_value / btc,
                            'cost_per_net_dollar': choice['cost_per_net_dollar'],
                            'binding_constraint': binding,
                            'capacity_evidence': capacities[ticker]['sources']})
        if ticker == 'MSTR' and scenario['mnav'] < 1:
            warnings.append(f'Common issued at mNAV {scenario["mnav"]} (below 1): each $1 raised hands new holders '
                            f'${D(1) / scenario["mnav"]:.4f} of NAV claim. Set common_below_nav to block to exclude it.')
        remaining = max(D(0), remaining - net)
        budget -= dividend
    return {'objective': 'minimize present value of claims transferred per net dollar raised; deterministic ticker ties',
            'cost_basis': {
                'common': 'NAV claim = gross / mNAV',
                'preferred': 'perpetual dividends capitalized: gross x annual yield / perpetual_discount_rate',
                'strk_conversion': 'Black-Scholes call on 0.1 MSTR share at $1,000 per STRK; STRK price = $8 / yield',
                'perpetual_discount_rate': scenario.get('perpetual_discount_rate', DEFAULT_PERPETUAL_DISCOUNT_RATE),
                'perpetual_discount_rate_source': 'scenario' if 'perpetual_discount_rate' in scenario else 'default',
                'common_below_nav': scenario.get('common_below_nav', 'warn')},
            'ranking': ranking, 'allocations': allocations, 'unfilled_net_usd': remaining,
            'break_even_discount_rate_vs_common': break_even_rates(scenario, choices),
            'warnings': warnings, 'blocked': blocked,
            'missing_market_inputs': missing,
            'missing_capacity': sorted(set(scenario['limits_usd']) - set(capacities)), 'disabled_without_limit': disabled,
            'dividend_budget_remaining_usd': budget,
            'status': 'incomplete_inputs' if missing or set(scenario['limits_usd']) - set(capacities) else 'filled' if remaining <= FILL_TOLERANCE_USD else 'constrained'}
