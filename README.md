# Strategy issuance router: compare financing rules with weekly issuance

This local Python CLI allocates a user-defined funding target under disclosed ATM capacity, instrument limits and an annual dividend budget. It compares the result with actual weekly issuance after making the recommendation. The included market inputs are explicitly synthetic; the capacity and actual issuance come from SEC filings in the adjacent ledger.

## What it does

- Accepts BTC spot, common mNAV, preferred annual cash yields, fees, funding target and limits in dated JSON.
- Ranks instruments by an explicit one-year cost proxy, applies capacity/budget constraints and reports unfilled funding and missing inputs.
- Enforces a decision date before the target period and excludes filings after that decision. Actual issuance never sets the recommendation.
- Replays an October 9, 2026 synthetic scenario against actual October 12–18 issuance. `examples/result.json` includes $22M actual MSTR net proceeds and source URLs; it is not a historical performance claim.

## How it works

`router/io.py` validates JSON and ledger CSVs and selects capacity known by cutoff. The pure rule in `router/core.py` ranks cost per net dollar: common proxy cost is gross proceeds / mNAV; preferred proxy cost is gross proceeds × annual cash yield. `router/__main__.py` adds the later actual comparison only after allocation. [Method](docs/method.md) explains the asymmetry and omitted liabilities.

## Run it

Python 3.11+; tested with Python 3.14.7. No package dependencies, credentials or paid market feed. Keep `strategy-8k-ledger` adjacent, or pass `--ledger /path/to/strategy-8k-ledger`.

```bash
cd /home/rahil/projects/strategy-8k-ledger
python -m ledger restore
cd /home/rahil/projects/strategy-issuance-router
python -m unittest discover -s tests -v
python -m router --scenario examples/synthetic.json
```

Observed: **17 tests pass**, including real-source comparison, altered-future-data independence, budgets, missing inputs, duplicate rows, invalid/nonfinite numbers and deterministic CLI replay. The ledger tests verify the upstream extraction separately.

## Repository layout

- `router/`: validation, capacity selection, pure rule and CLI.
- `examples/`: labeled synthetic inputs and deterministic output over real ledger data.
- `tests/`: rule, boundary and CLI behavior checks.
- `docs/`: scope, objective, sources and verification.

## Documentation

- [Spec](docs/spec.md): agreed acceptance criteria.
- [Method](docs/method.md): objective, formulas, assumptions and time boundary.
- [Sources](docs/sources.md): observed filings versus invented market inputs.
- [Verification](docs/verification.md): commands and tested limits.

## Sources

The adjacent ledger freezes 97 weekly observations and 432 program/action rows from SEC EDGAR CIK 1050446, through October 19, 2026. Each selected capacity has a program, as-of date, filing date and URL. The ledger holds source-byte hashes; this router reads its normalized CSVs. See the [October 19 actual issuance filing](https://www.sec.gov/Archives/edgar/data/1050446/000119312526424688/mstr-20261019.htm) and [source coverage](docs/sources.md), reviewed October 21.

## Scope and limits

- Independent local scenario tool, not affiliated with Strategy. No execution, advice, account access or automation.
- No observed market series: mNAV, BTC, yields, fees and constraints in the demo are synthetic. Dates are user assertions.
- One-year cash cost and common NAV dilution are simplifying proxies with different economic meanings; no claim about optimal real treasury actions.
- Disclosed capacity may be stale. EUR/STRE is excluded without an FX model. Liquidity, legal issuance constraints, conversion and principal claims are omitted.
- No inference about the pending October 28 dividend vote; annual yields do not encode daily payment approval.

## License

No license file yet. No license has been selected; source filings retain their own terms.

Part of [Rahil Bhavan's projects](https://github.com/RahilBhavan).
