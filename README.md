# Strategy issuance router: compare financing rules with weekly issuance

![Synthetic allocation: MSTR $3.11M, STRK $9.95M, STRD $9.95M and STRF $1.99M versus actual MSTR $22M and zero preferred issuance. Scenario replay, not a backtest.](figures/result.svg)

A deterministic Python CLI allocates a user-defined net funding target under disclosed ATM capacity, instrument limits and an annual dividend budget. It compares the recommendation with later weekly issuance. The market inputs are **synthetic**; capacity and actual issuance come from a pinned, bundled subset of the public SEC-derived ledger.

## What it does

- Ranks instruments using an explicit one-year cost proxy and reports unfilled funding, missing inputs and capacity evidence.
- Requires a decision before the target period; later issuance amounts do not influence allocation.
- Replays an October 9, 2026 synthetic $25M target against October 12–18 actual issuance: **$22M MSTR net proceeds**, zero preferred ATM proceeds ([result](examples/result.json)).
- Runs offline with no sibling checkout, package dependencies, credentials or paid feed.

## How it works

`router/io.py` validates scenario JSON and the ledger CSV contract, then selects capacity known by the cutoff. `router/core.py` greedily ranks proxy cost per net dollar: gross proceeds / mNAV for common, gross proceeds × annual cash yield for preferred. `router/__main__.py` adds actual comparisons after allocation. The proxies have different economic meanings; [method](docs/method.md) explains the simplification and precision policy.

## Run it

Python 3.11+; locally tested with 3.14.7; CI pins 3.14.0. No installation step or network access is needed after cloning.

```bash
git clone https://github.com/RahilBhavan/strategy-issuance-router.git
cd strategy-issuance-router
python -m unittest discover -s tests -v
python -m router --scenario examples/synthetic.json
python -m compileall -q router scripts tests
python scripts/render_result.py --check
```

Observed: **24 tests pass**. Two fresh CLI processes produce byte-identical output matching `examples/result.json`. The default fixture covers only the demo dates. For other dates, use `--ledger /path/to/restored-ledger`; see the [versioned dependency contract](docs/dependency.md).

## Repository layout

- `router/`: input boundary, capacity selection, pure rule and CLI.
- `fixtures/ledger-v1/`: selected public records and hash/provenance contract.
- `examples/`: labeled synthetic inputs and deterministic result.
- `figures/`, `scripts/`: generated result table and reproducibility checks.
- `tests/`: rule, boundary, precision and CLI regressions.
- `docs/`: methodology, source interpretation and verification.

## Documentation

- [Spec](docs/spec.md): scope and acceptance criteria.
- [Method](docs/method.md): objective, asymmetry, constraints and date boundary.
- [Sources](docs/sources.md): observed disclosures versus invented inputs.
- [Dependency](docs/dependency.md): pinned ledger contract and artifact verification.
- [Verification](docs/verification.md): exact checks and audit findings.
- [Publication](docs/publication.md): publication and clean-clone receipt.

## Sources

The bundled selection contains two weekly rows and twenty instrument rows (ten ATM and ten buyback), with original SEC URLs. Only ATM rows enter the rule. [Provenance](fixtures/ledger-v1/provenance.json) pins the ledger commit and artifact SHA-256 hashes; [source manifest](fixtures/ledger-v1/data/source-manifest.json) records original HTML hashes and fetch times. [October 5 capacity](https://www.sec.gov/Archives/edgar/data/1050446/000119312526413164/mstr-20261005.htm) and [October 19 actual issuance](https://www.sec.gov/Archives/edgar/data/1050446/000119312526424688/mstr-20261019.htm) were reviewed against primary filings. Source snapshot: October 21, 2026; UTC fetch dates are separate.

## Scope and limits

- Independent scenario tool, not affiliated with Strategy. No execution, account access or trades.
- Scenario replay, **not a historical backtest**. No independently sourced point-in-time mNAV/yield series is bundled; market dates are user assertions. No calibrated performance or optimal real treasury claim.
- Common NAV claim and one year of preferred cash expense are asymmetric proxies. Principal, perpetual duration, conversion, taxes, liquidity and legal issuance feasibility are omitted.
- Disclosed capacity may be stale. It is an assumed gross ceiling, not proof of tradability. EUR/STRE is excluded without FX modeling.
- The October 28 daily-dividend proposal was **pending at the October 21 snapshot**. Annual yields do not encode approval or dividend cadence.
- CSV validation and hashes do not certify financial data or security. The selected fixture is not a completeness claim.

## License

No license file yet. Third-party filings and data retain their own terms.

Part of [Rahil Bhavan's projects](https://github.com/RahilBhavan).
