# Scenario objective and time boundary

Purpose: make the recommendation rule inspectable and expose what it omits.

The objective is to fund a fixed **net USD** target at the lowest one-year financing-cost proxy per net dollar. For gross issuance `g`, common mNAV `m`, preferred annual cash yield `y`, fee fraction `f` and BTC spot `p`:

- Net cash = `g * (1-f)`; hypothetical BTC bought = net cash / `p`.
- Common proxy cost = `g / m`, representing the modeled NAV claim issued. It is not a cash dividend or full dilution valuation.
- Preferred proxy cost = `g * y`, a one-year cash expense. Principal/liquidation claims, perpetual duration, calls, conversions and changing yields are omitted. Comparing this with a common NAV claim is a deliberate simplifying convention; changing the horizon can reverse rankings.
- Score = proxy cost / net cash. Rank ascending; break ties by ticker. Allocate fractional USD up to remaining target, disclosed capacity, explicit ticker limit and remaining annual dividend budget.

This is a transparent rule, not a claim of globally optimal or feasible real treasury actions. Output uses 28-significant-digit Decimal arithmetic and labels the market assumptions. All inputs apply one common date. Missing preferred yields, common mNAV or capacity are exposed; unspecified ticker limits disable the ticker. No market input is inferred from subsequent purchases or issuance. Yields are fractions of gross financing proceeds for this model, not coupon rates automatically read from a security's designation. A price premium/discount, taxes and cash paid per legal notional would require more data.

## No lookahead

`decision_date` is an end-of-day cutoff, not an intraday timestamp, and must be strictly before the target period starts. Same-day filings are assumed known by that cutoff. Because the source has filing dates rather than acceptance timestamps, the date-only boundary is conservative and excludes the entire target period. Market data's `market_as_of` cannot exceed the decision date; these are user assertions, not independently authenticated market timestamps.

For each USD ticker, select the latest disclosed period/filing/accession known by the cutoff and sum separate programs at that observation. Earlier programs are not accumulated across dates. Available capacity is used as a gross USD ceiling by assumption; filings can describe authorized aggregate sale value rather than realized net proceeds. It can become stale or change between disclosures. STRE EUR capacity is excluded rather than silently FX-converted. No existing cash reserve is treated as a funding source.

Only after `recommend` completes does `evaluate` read actual target-period ATM net proceeds. The target week's calendar dates identify the evaluation window; its dollar amounts never set the target or limits. A later issuance is an outcome for comparison, not an input. The result is one weekly scenario comparison, not a performance backtest or historical forecasting record.

## Demo interpretation

`examples/synthetic.json` supplies an invented $85,000 BTC spot, 1.2 common mNAV and 8–12% preferred yields dated October 9, 2026. None is an observed historical market input. Capacities come from SEC filings available by that date. Actual comparison values come from the October 19 filing for October 12–18: MSTR $22M net and no preferred ATM issuance. The different recommendation shows the proxy's behavior, not a conclusion that Strategy should have acted differently.

As of October 21, the October 28 daily-dividend vote remains pending. This model uses only annual yield and makes no assumption about dividend cadence or approval.


## Numerical precision

JSON decimals are parsed directly as Decimal, without binary-float rounding.
Binding target/budget quotients round down so allocation cannot round above a
bound. A residual up to `1e-18` USD counts as filled; its actual residual is still
reported, rather than erased. Other arithmetic uses the default Decimal context
(28 significant digits). This is fractional scenario arithmetic, not settlement
rounding to cents or whole shares. Inputs with extreme magnitudes outside Decimal
arithmetic range are not supported.

Preferred marginal proxy cost equals dividend-budget consumption. Lower yields
therefore improve both cost and budget use; the common instrument consumes no
dividend budget and has a fixed marginal cost. With the shared fee and fractional
allocations, ascending scores are sufficient for this model. This argument does
not extend to instrument-specific fees, minimum lots or omitted legal constraints.
