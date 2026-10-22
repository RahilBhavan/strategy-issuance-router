"""Validate scenario JSON and dated ledger CSV boundaries."""
import csv
import datetime as dt
import json
from decimal import Decimal as D, InvalidOperation
from pathlib import Path

TICKERS = {'MSTR', 'STRK', 'STRF', 'STRD', 'STRC', 'STRE'}
REQUIRED = {'label', 'decision_date', 'market_as_of', 'period_end', 'target_net_usd',
            'btc_usd', 'fee_fraction', 'annual_dividend_budget_usd', 'limits_usd', 'yields'}


def date(value):
    if not isinstance(value, str) or dt.date.fromisoformat(value).isoformat() != value:
        raise ValueError('dates must be ISO YYYY-MM-DD')
    return value


def number(value, name, positive=False):
    if isinstance(value, bool):
        raise ValueError(f'{name}: boolean is not a number')
    try:
        value = D(str(value))
    except InvalidOperation as e:
        raise ValueError(f'{name}: invalid number') from e
    if not value.is_finite() or value < 0 or (positive and value == 0):
        raise ValueError(f'{name}: expected finite {"positive" if positive else "nonnegative"} number')
    return value


def scenario(path):
    data = json.loads(Path(path).read_text(), parse_float=D)
    if not isinstance(data, dict) or REQUIRED - data.keys() or data.keys() - REQUIRED - {'mnav'}:
        raise ValueError('scenario missing required fields or contains unknown fields')
    if not isinstance(data['label'], str) or not data['label'].strip():
        raise ValueError('label must describe observed or synthetic market inputs')
    for k in ('decision_date', 'market_as_of', 'period_end'):
        data[k] = date(data[k])
    if data['market_as_of'] > data['decision_date']:
        raise ValueError('market inputs are future-dated relative to decision')
    for k in ('target_net_usd', 'btc_usd', 'fee_fraction', 'annual_dividend_budget_usd', 'mnav'):
        if k in data:
            data[k] = number(data[k], k, k in ('btc_usd', 'mnav', 'target_net_usd'))
    if data['fee_fraction'] >= 1:
        raise ValueError('fee_fraction must be less than 1')
    for k in ('yields', 'limits_usd'):
        if not isinstance(data[k], dict) or data[k].keys() - TICKERS:
            raise ValueError(f'{k}: expected map of known tickers')
        data[k] = {t: number(v, f'{k}.{t}') for t, v in data[k].items()}
    if 'MSTR' in data['yields'] or any(v > 1 for v in data['yields'].values()):
        raise ValueError('preferred cash yields must be fractions from 0 to 1; MSTR uses mnav')
    return data


def read_ledger(root):
    def read(name):
        with (Path(root) / 'data' / name).open() as f:
            return list(csv.DictReader(f))
    weeks, inst = read('weekly.csv'), read('instrument_weekly.csv')
    week_ids = set()
    for r in weeks:
        for k in ('filed', 'period_start', 'period_end'):
            date(r[k])
        if r['period_start'] > r['period_end'] or r['period_end'] > r['filed']:
            raise ValueError('invalid ledger week chronology')
        if r['period_end'] in week_ids:
            raise ValueError('duplicate ledger week')
        week_ids.add(r['period_end'])
    week_map = {(r['accession'], r['period_end']): r for r in weeks}
    ids = set()
    for r in inst:
        identity = tuple(r[k] for k in ('accession', 'period_end', 'ticker', 'action', 'program'))
        if identity in ids:
            raise ValueError(f'duplicate ledger instrument: {identity}')
        ids.add(identity)
        if r['ticker'] not in TICKERS or r['action'] not in ('atm_sale', 'buyback') or r['currency'] not in ('USD', 'EUR'):
            raise ValueError('unknown ledger ticker, action or currency')
        for k in ('filed', 'period_start', 'period_end'):
            date(r[k])
        if r['period_start'] > r['period_end'] or r['period_end'] > r['filed']:
            raise ValueError('invalid ledger period/filing chronology')
        week = week_map.get((r['accession'], r['period_end']))
        if week is None or any(r[k] != week[k] for k in ('filed', 'period_start', 'doc_url')):
            raise ValueError('invalid ledger instrument/week join')
        for k in ('available_usd', 'amount_usd'):
            if r[k]:
                number(r[k], k)
    return weeks, inst


def capacities(inst, cutoff):
    eligible = [r for r in inst if r['filed'] <= cutoff and r['action'] == 'atm_sale'
                and r['available_usd'] and r['currency'] == 'USD']
    out = {}
    for ticker in sorted({r['ticker'] for r in eligible}):
        rows = [r for r in eligible if r['ticker'] == ticker]
        latest = max((r['period_end'], r['filed'], r['accession']) for r in rows)
        rows = [r for r in rows if (r['period_end'], r['filed'], r['accession']) == latest]
        out[ticker] = {'capacity_usd': sum((D(r['available_usd']) for r in rows), D(0)),
                       'sources': [{'url': r['doc_url'], 'filed': r['filed'], 'as_of': r['period_end'],
                                    'program': r['program'], 'capacity_usd': r['available_usd']}
                                   for r in rows]}
    return out
