"""Render the committed scenario result as an accessible SVG table; no dependencies."""
import argparse
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOUND = {'user_limit': 'stops at its user limit', 'disclosed_capacity': 'stops at disclosed ATM capacity',
         'dividend_budget': 'stops at the dividend budget', 'target': 'fills the rest of the target'}


def millions(value):
    return str((Decimal(value) / 1000000).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def short(value):
    return millions(value).rstrip('0').rstrip('.')


def render():
    result = json.loads((ROOT / 'examples/result.json').read_text())
    recommendation = result['recommendation']
    cost = {r['ticker']: r['cost_per_net_dollar'] for r in recommendation['ranking']}
    target = short(result['scenario']['target_net_usd'])
    actual_total = sum(Decimal(r['actual_net_usd'] or 0) for r in result['comparison'])
    rate = Decimal(recommendation['cost_basis']['perpetual_discount_rate'])
    rows, desc = [], []
    for index, row in enumerate(result['comparison']):
        y = 230 + index * 40
        actual = 'n/a' if row['actual_net_usd'] is None else millions(row['actual_net_usd'])
        price = f'{Decimal(cost[row["ticker"]]):.2f}' if row['ticker'] in cost else 'n/a'
        rows.append(f'<text x="20" y="{y}">{row["ticker"]}</text>'
                    f'<text x="165" y="{y}" text-anchor="end">{price}</text>'
                    f'<text x="280" y="{y}" text-anchor="end">{millions(row["scenario_net_usd"])}</text>'
                    f'<text x="380" y="{y}" text-anchor="end">{actual}</text>')
        desc.append(f'{row["ticker"]} cost {price}, scenario {millions(row["scenario_net_usd"])}, actual {actual}')
    y = 230 + len(rows) * 40 + 20
    notes = []
    for allocation in recommendation['allocations']:
        notes.append(('', f'{allocation["ticker"]} {BOUND[allocation["binding_constraint"]]}.'))
    unused = [r['ticker'] for r in recommendation['ranking'] if Decimal(r['gross_usd']) == 0]
    if unused:
        notes.append(('', f'Unused: {", ".join(unused)} (costlier).'))
    notes += [('gap', ''), ('note', 'Cost/$: present value of claims'), ('note', 'given per net dollar raised.'),
              ('note', 'Common 1/mNAV; preferred yield'), ('note', f'÷ {rate:.0%} discount rate; STRK adds'),
              ('note', 'its conversion value.'), ('gap', ''),
              ('note', 'Actual: October 12–18, 2026'), ('note', 'SEC October 19 8-K'),
              ('note', 'Synthetic mNAV, yields, fees and limits.'),
              ('note', f'The ${target}M target is illustrative,'), ('note', 'not a filed or planned raise.'),
              ('note', 'Source: examples/result.json'),
              ('note', 'Rahil Bhavan · Source as-of Oct 21'), ('note', 'Not a historical backtest or'),
              ('note', 'investment recommendation.')]
    lines = []
    for kind, content in notes:
        if kind == 'gap':
            y += 10
            continue
        css = f' class="{kind}"' if kind else ''
        lines.append(f'<text x="20" y="{y}"{css}>{content}</text>')
        y += 30
    height = y + 5
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="{height}" viewBox="0 0 400 {height}" role="img" aria-labelledby="title desc">
<title id="title">Synthetic ${target}M allocation versus ${short(actual_total)}M actual issuance</title>
<desc id="desc">Net USD millions and cost per net dollar raised. {'; '.join(desc)}. The ${target}M target is illustrative, not a filed or planned raise. Actual October 12–18, 2026. Scenario replay, not a backtest.</desc>
<style>text{{font-family:'IBM Plex Sans',sans-serif;font-size:20px;fill:#111214}}.note{{font-size:18px;fill:#52545A}}.head{{font-weight:600}}</style>
<rect width="400" height="{height}" fill="#F5F5EF"/>
<text x="20" y="40" class="head">Synthetic ${target}M allocation</text>
<text x="20" y="70" class="head">versus ${short(actual_total)}M actual issuance</text>
<text x="20" y="108" class="note">Decision: October 9, 2026</text>
<text x="20" y="138" class="note">Scenario and actual: net USD millions</text>
<text x="20" y="190" class="head">Ticker</text>
<text x="165" y="190" text-anchor="end" class="head">Cost/$</text>
<text x="280" y="190" text-anchor="end" class="head">Scenario</text>
<text x="380" y="190" text-anchor="end" class="head">Actual</text>
<path d="M20 205H380" stroke="#C6C7BF"/>
''' + '\n'.join(rows) + '\n' + '\n'.join(lines) + '\n</svg>\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    path = ROOT / 'figures/result.svg'
    if args.check:
        if path.read_text() != render():
            raise SystemExit('result figure differs; run python scripts/render_result.py')
        print(f'ok: {path.relative_to(ROOT)} matches examples/result.json')
    else:
        path.parent.mkdir(exist_ok=True)
        path.write_text(render())
        print(f'wrote {path.relative_to(ROOT)} from examples/result.json')
