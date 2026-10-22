"""Render the committed scenario result as an accessible SVG table; no dependencies."""
import argparse
import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def render():
    result = json.loads((ROOT / 'examples/result.json').read_text())
    rows = []
    for index, row in enumerate(result['comparison']):
        y = 220 + index * 40
        actual = row['actual_net_usd']
        actual = 'not stated' if actual is None else f'{Decimal(actual)/1000000:.2f}'
        modeled = f"{Decimal(row['scenario_net_usd'])/1000000:.2f}"
        rows.append(f'<text x="20" y="{y}">{row["ticker"]}</text>'
                    f'<text x="245" y="{y}" text-anchor="end">{modeled}</text>'
                    f'<text x="375" y="{y}" text-anchor="end">{actual}</text>')
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="655" viewBox="0 0 400 655" role="img" aria-labelledby="title desc">
<title id="title">Synthetic $25M allocation versus $22M actual issuance</title>
<desc id="desc">Net USD millions. Scenario: MSTR 3.11, STRC 0, STRD 9.95, STRF 1.99, STRK 9.95. Actual October 12–18: MSTR 22, all preferred zero. Scenario replay, not a backtest.</desc>
<style>text{font-family:'IBM Plex Sans',sans-serif;font-size:20px;fill:#111214}.note{font-size:18px;fill:#52545A}.head{font-weight:600}</style>
<rect width="400" height="655" fill="#F5F5EF"/>
<text x="20" y="40" class="head">Synthetic $25M allocation</text>
<text x="20" y="70" class="head">versus $22M actual issuance</text>
<text x="20" y="108" class="note">Decision: October 9, 2026</text>
<text x="20" y="138" class="note">Scenario replay · Net USD millions</text>
<text x="20" y="180" class="head">Ticker</text>
<text x="245" y="180" text-anchor="end" class="head">Scenario</text>
<text x="375" y="180" text-anchor="end" class="head">Actual</text>
<path d="M20 195H380" stroke="#C6C7BF"/>
''' + '\n'.join(rows) + '''
<text x="20" y="435" class="note">Actual: October 12–18, 2026</text>
<text x="20" y="465" class="note">SEC October 19 8-K</text>
<text x="20" y="505" class="note">Synthetic mNAV, yields, fees and limits.</text>
<text x="20" y="535" class="note">Source: examples/result.json</text>
<text x="20" y="565" class="note">Rahil Bhavan · Source as-of Oct 21</text>
<text x="20" y="605" class="note">Not a historical backtest or</text>
<text x="20" y="635" class="note">investment recommendation.</text>
</svg>
'''


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    path = ROOT / 'figures/result.svg'
    if args.check:
        if path.read_text() != render():
            raise SystemExit('result figure differs; run python scripts/render_result.py')
    else:
        path.parent.mkdir(exist_ok=True)
        path.write_text(render())
