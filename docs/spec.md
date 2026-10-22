# Issuance router v1 scope and acceptance

Agreed 2026-10-21. Local deterministic CLI consuming the adjacent weekly ledger; no trades or publication.

- Accept a dated scenario: decision cutoff, target proceeds, BTC spot, common mNAV, preferred yields, fee fraction, instrument limits and annual dividend budget.
- Use only ledger capacities filed strictly before the target period starts. Reject future-dated market inputs and invalid/nonfinite numbers; enumerate missing inputs instead of inferring them from subsequent issuance.
- Rank feasible instruments by an explicit one-year BTC-equivalent financing-cost proxy. Common cost = proceeds/mNAV; preferred cost = proceeds*annual cash yield; fees reduce net cash. This is a rule-based scenario objective, not treasury optimization or a security valuation.
- Allocate up to target under known capacity, user limits and dividend budget. Compare recommended proceeds with the actual target-period per-instrument issuance, loaded only after the recommendation. Actual figures must never determine the recommendation.
- Demo uses visibly synthetic market assumptions over real historical ledger capacity and actual issuance. Prove no-lookahead, missing inputs, constraints, tie-breaking, negative inputs and deterministic replay.
