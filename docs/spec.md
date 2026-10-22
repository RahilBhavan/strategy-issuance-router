# Issuance router v1 scope and acceptance

Agreed 2026-10-21. Deterministic CLI consuming the versioned weekly-ledger CSV contract; no trades.

Publication update: reviewed source is authorized for a public GitHub repository. The
bundled demo snapshot replaces the original mutable sibling dependency.

- Accept a dated scenario: decision cutoff, target proceeds, BTC spot, common mNAV, preferred yields, fee fraction, instrument limits and annual dividend budget.
- Use only ledger capacities filed strictly before the target period starts. Reject future-dated market inputs and invalid/nonfinite numbers; enumerate missing inputs instead of inferring them from subsequent issuance.
- Rank feasible instruments by an explicit cost per net dollar (originally a one-year proxy; replaced on 2026-10-22, see below). Fees reduce net cash. This is a rule-based scenario objective, not treasury optimization or a security valuation.
- Allocate up to target under known capacity, user limits and dividend budget. Compare recommended proceeds with the actual target-period per-instrument issuance, loaded only after the recommendation. Actual figures must never determine the recommendation.
- Demo uses visibly synthetic market assumptions over real historical ledger capacity and actual issuance. Prove no-lookahead, missing inputs, constraints, tie-breaking, negative inputs and deterministic replay.

## Reader-test model update (2026-10-22)

The one-year proxy is replaced by present value of claims per net dollar:
common `1/mNAV`, preferred `yield / perpetual_discount_rate`, plus a Black–Scholes
STRK conversion value. Common issuance below mNAV 1 warns or is blocked. A target
week absent from the ledger gives a forward-looking recommendation without an
actual comparison. See [method](method.md).

## Authorized comparison slice (2026-10-22)

Opt-in shared-assumption financing alternatives and optional common dilution are
specified in [the improvement plan](improvement-plan.md). Default output and the
pinned ledger contract remain compatible. See [comparison](financing-comparison.md)
for formulas and limits.
