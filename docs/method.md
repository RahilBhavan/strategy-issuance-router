# Scenario objective and time boundary

Purpose: make the recommendation rule inspectable and expose what it omits.

The objective is to fund a fixed **net USD** target while handing new holders the least present value of claims per net dollar raised. For gross issuance `g`, common mNAV `m`, preferred annual cash yield `y`, perpetual discount rate `k`, fee fraction `f` and BTC spot `p`:

- Net cash = `g * (1-f)`; hypothetical BTC bought = net cash / `p`.
- Common claim = `g / m`: new shareholders receive this much NAV. At mNAV 1 a dollar raised costs a dollar of NAV.
- Preferred claim = `g * y / k`: the perpetual dividend stream capitalized at `k`. At `k = y` a preferred also costs a dollar per gross dollar.
- STRK adds its conversion right: a Black–Scholes call on 0.1 MSTR share struck at $1,000 (its conversion terms) over `horizon_years`, with the scenario's MSTR price, volatility and risk-free rate. The STRK price is implied by its cash yield ($8 dividend / `y`), so the option value per gross dollar is `0.1 * call * y / 8`.
- Score = claim / net cash. Rank ascending; break ties by ticker. Allocate fractional USD up to remaining target, disclosed capacity, explicit ticker limit and remaining annual dividend budget. Each allocation records which of these bound it.

### Why capitalize, and which rate

The earlier version compared one year of preferred dividends with a common NAV claim. Common hands over a permanent claim, so preferreds looked cheap until the dividend budget ran out. Both instruments are perpetual, so the router now values both as perpetual claims. A common horizon (for example ten years of dividends) would need a terminal value for the preferred anyway, and the answer would depend on that horizon. Capitalizing needs one stated number instead.

`perpetual_discount_rate` (`k`) is the issuer's required return on perpetual fixed claims. It is a scenario input; when omitted, the router uses 10% and records `perpetual_discount_rate_source: default`. The synthetic demo sets 10% explicitly: a round rate inside its synthetic 8–12% preferred yields. The output reports `break_even_discount_rate_vs_common` per preferred: `y / (1/m - conversion)`. A preferred is cheaper than common only when `k` is above that rate. In the demo, STRF and STRD break even at 12%, STRK at 10.7% and STRC at 14.4%, so the ranking is sensitive to `k`. Read the break-even rates before reading the allocation.

The conversion term is a simple stand-in. A finite European call understates a perpetual right, adding it to the full dividend value double-counts dividends after conversion, and STRK's price is inferred from the yield input. It is there so that STRK is not treated as a plain 8% preferred. Without `strk_conversion` inputs, STRK is reported as a missing input and is not ranked.

### Common below mNAV 1

At mNAV below 1, issuing common hands new holders more NAV than it raises. `common_below_nav` controls this: `warn` (default) ranks common normally and adds a warning to the output and to stderr whenever common is issued; `block` removes common and lists it under `blocked`.

This is a transparent rule, not a claim of globally optimal or feasible real treasury actions. Output uses 28-significant-digit Decimal arithmetic and labels the market assumptions. All inputs apply one common date. Missing preferred yields, common mNAV or capacity are exposed; unspecified ticker limits disable the ticker. No market input is inferred from subsequent purchases or issuance. Yields are fractions of gross financing proceeds for this model, not coupon rates automatically read from a security's designation. A price premium/discount, taxes and cash paid per legal notional would require more data.

## No lookahead

`decision_date` is an end-of-day cutoff, not an intraday timestamp, and must be strictly before the target period starts. Same-day filings are assumed known by that cutoff. Because the source has filing dates rather than acceptance timestamps, the date-only boundary is conservative and excludes the entire target period. Market data's `market_as_of` cannot exceed the decision date; these are user assertions, not independently authenticated market timestamps.

For each USD ticker, select the latest disclosed period/filing/accession known by the cutoff and sum separate programs at that observation. Earlier programs are not accumulated across dates. Available capacity is used as a gross USD ceiling by assumption; filings can describe authorized aggregate sale value rather than realized net proceeds. It can become stale or change between disclosures. STRE EUR capacity is excluded rather than silently FX-converted. No existing cash reserve is treated as a funding source.

If the ledger has no week ending on `period_end`, the run is forward-looking: the target week is assumed to be the seven days ending on `period_end`, the decision must precede that week, capacities come from filings known by the decision date, and `comparison` is null with a note on stderr. `--no-actuals` skips the comparison even when the week exists.

Only after `recommend` completes does `evaluate` read actual target-period ATM net proceeds. The target week's calendar dates identify the evaluation window; its dollar amounts never set the target or limits. A later issuance is an outcome for comparison, not an input. The result is one weekly scenario comparison, not a performance backtest or historical forecasting record.

## Demo interpretation

`examples/synthetic.json` supplies an invented $85,000 BTC spot, 1.2 common mNAV, 8–12% preferred yields, a 10% perpetual discount rate and STRK conversion inputs (MSTR $200, 60% volatility, 10 years, 4.5%) dated October 9, 2026. None is an observed historical market input. Capacities come from SEC filings available by that date. Actual comparison values come from the October 19 filing for October 12–18: MSTR $22M net and no preferred ATM issuance.

The router now issues $24.875M net of common (stopped by its $25M gross user limit) and $0.125M of STRK (the rest of the target). The earlier one-year proxy issued $3.11M of common and $21.89M of STRK, STRD and STRF. The new allocation agrees with the actual week's choice of common only, apart from the STRK remainder. This agreement comes from the stated inputs: at a discount rate above 12%, STRF and STRD would rank ahead of common again. One week with synthetic market inputs is a scenario replay, not evidence that the router predicts Strategy's choices.

As of October 21, the October 28 daily-dividend vote remains pending. This model uses only annual yield and makes no assumption about dividend cadence or approval.


## Numerical precision

JSON decimals are parsed directly as Decimal, without binary-float rounding.
Binding target/budget quotients round down so allocation cannot round above a
bound. A residual up to `1e-18` USD counts as filled; its actual residual is still
reported, rather than erased. Other arithmetic uses the default Decimal context
(28 significant digits). This is fractional scenario arithmetic, not settlement
rounding to cents or whole shares. Inputs with extreme magnitudes outside Decimal
arithmetic range are not supported.

Ascending scores are a rule, not a proven optimum. For plain preferreds, claim
value is proportional to dividend-budget use, so a lower score also uses less
budget. STRK's conversion term breaks that link: when the dividend budget binds,
a linear program could prefer a different mix. Instrument-specific fees, minimum
lots and legal constraints are also omitted. Residuals within the fill tolerance
do not buy dust from the next instrument.

Output is quantized for display only: USD to cents, BTC to eight places and
ratios to six places. Arithmetic keeps full Decimal precision, so displayed
parts can differ from displayed totals by a cent. Scenario inputs are echoed as
given.

## Financing alternatives

The optional [comparison](financing-comparison.md) restricts eligible instruments
while preserving all other assumptions and the original objective. It separates
fees, common NAV claim, capitalized preferred dividends, STRK conversion value and
annual cash expense, and optionally calculates direct common ownership dilution
from explicit price/share inputs. No metric establishes real economic superiority.
