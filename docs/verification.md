# Verification receipt

Purpose: record exact local checks. Executed 2026-10-21 America/Detroit, Python 3.14.7.

```bash
cd /home/rahil/projects/strategy-8k-ledger
python -m ledger restore
cd /home/rahil/projects/strategy-issuance-router
python -m unittest discover -s tests -v
python -m router --scenario examples/synthetic.json
```

17 tests pass. Tests consume actual ledger records and verify the October 19 filing's $22M MSTR net issuance. Recommendation equality survives changing all later capacity and issuance values; the comparison changes independently. Decision-inside-period and future market dates refuse. Limits, zero budget, zero capacity, missing mNAV/yield/capacity, missing actuals (null, not zero), fee/price validation, nonfinite/negative/bool inputs and duplicate ledger records are exercised. Equal-cost preferred ties resolve deterministically by ticker. BTC spot changes modeled BTC units without changing USD allocation.

Two fresh CLI processes return byte-identical JSON matching `examples/result.json`. The demo labels its prices/yields/mNAV synthetic and includes actual source URLs. No historical market data service, strategy performance benchmark, live treasury decision, execution, multi-week scheduling or deployment was tested or claimed. Upstream ledger tests establish source extraction; this tool does not independently reparse raw filings.
