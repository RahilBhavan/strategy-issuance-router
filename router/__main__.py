"""python -m router --scenario examples/synthetic.json [--ledger PATH]"""
import argparse
import json
from decimal import Decimal, DecimalException
from pathlib import Path
from . import io
from .core import recommend
from .financing import compare_financing


def evaluate(scenario, weeks, inst, compare=False):
    target = [w for w in weeks if w['period_end'] == scenario['period_end']]
    if len(target) != 1:
        raise ValueError('target period missing or ambiguous in ledger')
    target = target[0]
    if scenario['decision_date'] >= target['period_start']:
        raise ValueError('decision must be strictly before target period starts (date-only conservative cutoff)')
    available = io.capacities(inst, scenario['decision_date'])
    result = recommend(scenario, available)
    financing = compare_financing(scenario, available) if compare else None
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
    output = {'scenario': scenario, 'recommendation': result, 'comparison': comparison,
            'target_period_start': target['period_start'], 'target_actual_filed': target['filed'],
            'limits': ['Synthetic or user-supplied market inputs; no historical market feed.',
                       'Stale disclosed capacity is a scenario ceiling, not proof of tradability.',
                       'No execution, liquidity, conversion, principal liability, taxes or long-term optimality model.',
                       'Daily dividend proposal is pending as of 2026-10-21; cadence is not used.']}
    if compare:
        output['financing_comparison'] = financing
    return output


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--scenario', required=True)
    p.add_argument('--compare-financing', action='store_true',
                   help='compare router with common-only, preferred-only and single-preferred policies')
    p.add_argument('--ledger', default=str(Path(__file__).resolve().parents[1] / 'fixtures' / 'ledger-v1'))
    args = p.parse_args()
    try:
        data = io.scenario(args.scenario)
        weeks, inst = io.read_ledger(args.ledger)
        print(json.dumps(evaluate(data, weeks, inst, compare=args.compare_financing), default=str, indent=2, sort_keys=True))
    except (ValueError, KeyError, OSError, TypeError, DecimalException) as e:
        p.exit(2, f'error: {e}\n')


if __name__ == '__main__':
    main()
