# Strategy issuance router: compare financing rules with weekly issuance

**Common is the cheapest capital in this repo's synthetic demo.** Selling Strategy's common stock (MSTR) gives new holders $0.84 of value per dollar raised, against $0.89 to $1.21 for its four preferred stocks. That holds at an assumed mNAV of 1.2 and a 10% discount rate, for the October 9, 2026 decision in [`examples/result.json`](examples/result.json).

[![Offline verification](https://github.com/RahilBhavan/strategy-issuance-router/actions/workflows/ci.yml/badge.svg)](https://github.com/RahilBhavan/strategy-issuance-router/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

![Synthetic $25M target, an illustrative amount and not a filed or planned raise. Router allocation: MSTR $24.88M at 0.84 per net dollar, STRK $0.13M at 0.89; STRD, STRF and STRC unused at 1.01 to 1.21. Actual week: MSTR $22M, no preferred issuance.](figures/result.svg)

A deterministic Python CLI splits a net funding target across Strategy's common stock (MSTR) and its USD preferreds. It respects disclosed ATM capacity, per-instrument limits and an annual dividend budget. It ranks each instrument by the present value of claims handed to new holders per net dollar raised, and names the constraint that stops each one. Market inputs are **synthetic**. Capacity and actual issuance come from a pinned subset of the public SEC-derived ledger.

## What it does

- Prices every instrument on one basis. Common costs `1/mNAV` of NAV claim per gross dollar. A preferred costs its annual yield capitalized at a perpetual discount rate (10% in the demo), and STRK adds the Black-Scholes value of its conversion right.
- Reports, for each instrument, cost per net dollar, the binding constraint and the discount rate at which a preferred would beat common. In the demo those break-even rates are 10.74% for STRK, 12% for STRD and STRF, and 14.4% for STRC ([`examples/result.json`](examples/result.json)). With the other inputs unchanged, common stops being the cheapest above 10.74%.
- Warns when common would be issued below mNAV 1, or excludes it with `"common_below_nav": "block"`.
- Requires a decision date before the target week, so later issuance never feeds the allocation. A week not yet in the ledger gets a forward-looking recommendation with no actual comparison.
- Replays the demo against October 12–18, 2026 actual issuance. The demo's **$25M target is synthetic**. It is an illustrative amount, not a filed or planned raise. The router issues **$24.875M net of MSTR** (stopped by its $25M gross limit) and $0.125M of STRK. Strategy issued **$22M of MSTR net proceeds** and no preferred ATM proceeds.
- Compares common-only, preferred-only and single-preferred policies under the same inputs with `--compare-financing`. In the demo the router funds $25M, common-only $24.875M and preferred-only $21.89M ([formulas](docs/financing-comparison.md)).
- Runs offline, with no sibling checkout, package dependencies, credentials or paid feed.

## How it works

`router/io.py` validates scenario JSON and the ledger CSV contract, then selects capacity known by the cutoff. `router/core.py` ranks instruments by claim value per net dollar, fills greedily, and records the bound that stops each one (target, dividend budget, user limit or disclosed capacity). `router/financing.py` builds the alternative policies. `router/__main__.py` adds the actual comparison after allocation when the ledger has the target week, and rounds output to cents. [Method](docs/method.md) covers the discount rate, the STRK conversion term and the precision policy.

## Run it

Python 3.11+. Tested locally with 3.14.7; CI pins 3.14.0. No installation step or network access is needed after cloning.

```bash
git clone https://github.com/RahilBhavan/strategy-issuance-router.git
cd strategy-issuance-router
python -m unittest discover -s tests -v
python -m router --scenario examples/synthetic.json
python -m router --scenario examples/forward.json
python -m router --scenario examples/synthetic.json --compare-financing
python -m compileall -q router scripts tests
python scripts/render_result.py --check
```

Observed: **45 tests pass**. Two fresh CLI runs produce byte-identical output that matches `examples/result.json`. `examples/forward.json` asks for the week ending November 1, 2026 from an October 22 decision. It uses capacities from the October 19 filing and prints a note that no actual comparison exists. `--no-actuals` skips the comparison for a past week. The bundled fixture covers only the demo dates. For other dates, pass `--ledger /path/to/restored-ledger` (see the [dependency contract](docs/dependency.md)).

## Repository layout

- `router/`: input boundary, capacity selection, allocation rule, financing comparison and CLI.
- `fixtures/ledger-v1/`: selected public records and the hash/provenance contract.
- `examples/`: labeled synthetic inputs and the deterministic result.
- `figures/`, `scripts/`: generated result table and reproducibility checks.
- `tests/`: rule, boundary, precision, financing and CLI regressions.
- `docs/`: method, sources and verification.
- `AGENTS.md`, `CLAUDE.md`, `DESIGN.md`, `design/`, `.githooks/`: instructions, design tokens and a pre-commit size check for the coding agents that work in this repository. The code does not use them.

## Documentation

- [Public design system](DESIGN.md): Rahil Design 3.3.0, shared tokens and visual review rules.
- [Spec](docs/spec.md): scope and acceptance criteria.
- [Method](docs/method.md): objective, constraints and date boundary.
- [Financing comparison](docs/financing-comparison.md): alternative policies, dilution and a five-minute example.
- [Sources](docs/sources.md): observed disclosures versus invented inputs.
- [Dependency](docs/dependency.md): pinned ledger contract and artifact verification.
- [Verification](docs/verification.md): exact checks and audit findings.
- [Publication](docs/publication.md): publication and clean-clone receipt.

## Sources

The bundled selection has two weekly rows and twenty instrument rows (ten ATM, ten buyback), each with its original SEC URL. Only ATM rows enter the rule. [Provenance](fixtures/ledger-v1/provenance.json) pins the ledger commit and artifact SHA-256 hashes, and the [source manifest](fixtures/ledger-v1/data/source-manifest.json) records original HTML hashes and fetch times. The [October 5 capacity filing](https://www.sec.gov/Archives/edgar/data/1050446/000119312526413164/mstr-20261005.htm) and the [October 19 actual-issuance filing](https://www.sec.gov/Archives/edgar/data/1050446/000119312526424688/mstr-20261019.htm) were checked against the primary documents. Source snapshot: October 21, 2026.

## Scope and limits

- Independent scenario tool, not affiliated with Strategy. It places no trades and uses no accounts.
- Scenario replay, **not a historical backtest**. No point-in-time mNAV or yield series is bundled, so market inputs are user assertions.
- The ranking depends on the discount rate and STRK conversion inputs. STRK's conversion value uses a finite-horizon European option as a stand-in for a perpetual right. Taxes, liquidity, calls and legal issuance feasibility are not modeled. The greedy fill is not proven optimal when the dividend budget binds.
- Disclosed capacity may be stale and is treated as a gross ceiling, not proof the shares can be sold. EUR-denominated STRE is excluded because FX is not modeled.
- The October 28 daily-dividend proposal was pending at the October 21 snapshot. Annual yields do not encode its outcome or dividend cadence.
- The fixture is a selection, not a complete ledger. Hashes check file integrity, not the accuracy of the financial data.

## License

[MIT](LICENSE). The license covers this project's code only. Third-party filings and data keep their own terms.

Part of [Rahil Bhavan's projects](https://github.com/RahilBhavan).
