"""python -m router --scenario examples/synthetic.json [--ledger PATH] [--compare-financing]

If the ledger has the target week, actual issuance is compared after the recommendation.
Otherwise the recommendation is forward-looking: capacities known by the decision date only."""
import argparse
import datetime as dt
import json
import sys
from decimal import Decimal, DecimalException
from pathlib import Path
from . import io
from .core import recommend
from .financing import compare_financing

QUANTUM = {'usd': Decimal('0.01'), 'btc': Decimal('0.00000001'), 'ratio': Decimal('0.000001')}


def target_window(scenario, weeks):
    """Ledger week for the target, or an assumed seven-day week ending on period_end."""
    target = [w for w in weeks if w['period_end'] == scenario['period_end']]
    if target:
        return target[0]['period_start'], target[0]
    start = dt.date.fromisoformat(scenario['period_end']) - dt.timedelta(days=6)
    return start.isoformat(), None


def evaluate(scenario, weeks, inst, compare=False, compare_actual=True):
    period_start, week = target_window(scenario, weeks)
    if scenario['decision_date'] >= period_start:
        raise ValueError(f'decision_date {scenario["decision_date"]} must be strictly before the target period '
                         f'starts ({period_start}); date-only conservative cutoff')
    available = io.capacities(inst, scenario['decision_date'])
    result = recommend(scenario, available)
    financing = compare_financing(scenario, available) if compare else None
    output = {'scenario': scenario, 'recommendation': result,
              'target_period_start': period_start,
              'limits': ['Synthetic or user-supplied market inputs; no historical market feed.',
                         'Stale disclosed capacity is a scenario ceiling, not proof of tradability.',
                         'No execution, liquidity, principal liability, taxes or long-term optimality model; '
                         'STRK conversion uses a finite-horizon Black-Scholes stand-in.',
                         'Daily dividend proposal is pending as of 2026-10-21; cadence is not used.']}
    if week is None or not compare_actual:
        output['comparison'] = None
        output['target_actual_filed'] = None
        output['actual_comparison'] = ('skipped by --no-actuals' if week is not None else
                                       f'not available: the ledger has no week ending {scenario["period_end"]}. '
                                       'Forward-looking recommendation from capacities filed by the decision date; '
                                       f'assumed target week {period_start} to {scenario["period_end"]}.')
    else:
        output['target_actual_filed'] = week['filed']
        output['actual_comparison'] = 'compared after the recommendation was computed'
        output['comparison'] = actual_comparison(scenario, inst, available, result)
    if compare:
        output['financing_comparison'] = financing
    return output


def actual_comparison(scenario, inst, available, result):
    # Actual issuance is consulted only after recommendation is fully computed.
    actual = [r for r in inst if r['period_end'] == scenario['period_end'] and r['action'] == 'atm_sale'
              and r['currency'] == 'USD']
    comparison = []
    for ticker in sorted(set(available) | {r['ticker'] for r in actual}):
        rows = [r for r in actual if r['ticker'] == ticker]
        amount = sum((Decimal(r['amount_usd']) for r in rows), Decimal(0)) if rows and all(r['amount_usd'] for r in rows) else None
        recommended = sum((r['net_usd'] for r in result['allocations'] if r['ticker'] == ticker), Decimal(0))
        comparison.append({'ticker': ticker, 'scenario_net_usd': recommended, 'actual_net_usd': amount,
                           'difference_usd': recommended - amount if amount is not None else None,
                           'actual_sources': [r['doc_url'] for r in rows]})
    return comparison


def for_display(value, key=''):
    """Quantize computed Decimals for output; arithmetic keeps full precision.

    USD to cents, BTC to satoshis, ratios to six places. Scenario inputs are echoed as given."""
    if isinstance(value, dict):
        return {k: (v if k == 'scenario' else for_display(v, k)) for k, v in value.items()}
    if isinstance(value, list):
        return [for_display(v, key) for v in value]
    if isinstance(value, Decimal):
        unit = 'usd' if key.endswith('usd') else 'btc' if 'btc' in key else 'ratio'
        shown = value.quantize(QUANTUM[unit])
        return shown.copy_abs() if shown.is_zero() else shown
    return value


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--scenario', required=True)
    p.add_argument('--compare-financing', action='store_true',
                   help='compare router with common-only, preferred-only and single-preferred policies')
    p.add_argument('--no-actuals', action='store_true',
                   help='skip the actual-issuance comparison even when the ledger has the target week')
    p.add_argument('--ledger', default=str(Path(__file__).resolve().parents[1] / 'fixtures' / 'ledger-v1'))
    args = p.parse_args()
    try:
        data = io.scenario(args.scenario)
        weeks, inst = io.read_ledger(args.ledger)
        output = evaluate(data, weeks, inst, compare=args.compare_financing, compare_actual=not args.no_actuals)
        text = json.dumps(for_display(output), default=str, indent=2, sort_keys=True)
    except (ValueError, KeyError, OSError, TypeError, DecimalException) as e:
        p.exit(2, f'error: {e}\n')
    if output['comparison'] is None:
        print(f'note: actual comparison {output["actual_comparison"]}', file=sys.stderr)
    for warning in output['recommendation']['warnings']:
        print(f'warning: {warning}', file=sys.stderr)
    print(text)


if __name__ == '__main__':
    main()
