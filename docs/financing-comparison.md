# Compare financing under identical assumptions

The opt-in comparison reuses the existing allocator with restricted eligible
instruments: all enabled instruments (`router`), MSTR alone (`common_only`), all
enabled preferred instruments (`preferred_only`), and each enabled preferred
instrument alone. Preferred-only still ranks by the existing yield proxy; it is
not equal weighting. No policy can invent capacity or override a user limit.
Unspecified instruments stay disabled. The default CLI output is unchanged.

## Five-minute offline reproduction

Python 3.11+, no packages or service needed, from the repository root:

```bash
python -m unittest discover -s tests -v
python -m router --scenario examples/synthetic.json --compare-financing
```

Read `financing_comparison.alternatives` in the JSON. Every policy carries the
original allocation result, including unfilled funding, missing inputs and
remaining dividend budget. `metrics.constraints` reports gross user limits,
disclosed capacity, remaining headroom and filing evidence for every eligible
ticker, including those not used. A null capacity means unknown, not zero.

For the supplied **synthetic** market scenario, router funding is $25,000,000;
common-only funding is $24,875,000, leaving $125,000 unfilled because the $25M
gross user limit also has to absorb the 0.5% fee. Preferred-only funding is
$21,890,000, leaving $3,110,000 unfilled with the $2M annual dividend budget
exhausted. These are model results, not observed financing performance.

`fees_usd` = gross issuance × fee fraction. Net funding already deducts that fee;
fees are shown separately and are not added again to the original proxy.
`common_nav_claim_proxy_usd` and `annual_preferred_cash_expense_usd` disaggregate
the asymmetric one-year proxy; their sum is `one_year_asymmetric_proxy_usd`.
`proxy_per_funded_net_dollar` divides by actual modeled funding, never the target;
it is null with zero funding. Comparing that ratio alone does not establish that
a partially filled policy can meet the target.

`proxy_excess_over_router_usd` is alternative proxy minus router proxy, emitted
only when both policies have complete inputs and fill the target within the
existing `1e-18` USD tolerance. Otherwise it is null. This is a proxy difference,
not economic savings. In the default demo every simple alternative is constrained,
so every alternative's full-target difference is null.

## Optional direct common dilution

Add both `common_share_price_usd` (gross execution price) and
`common_shares_outstanding` (pre-issue common share count) to a scenario. Both
must be finite and positive, on the same asserted `market_as_of` basis as the
other market inputs. No price or share count is inferred from mNAV or filings.

New common shares = common gross proceeds / price. New common ownership fraction
= new shares / (pre-issue shares + new shares). This equals the relative ownership
reduction for unchanged existing common holdings, assuming one share class and
no other issuance. It is not change in BTC per share, NAV dilution, EPS dilution
or a fully diluted capital model. With no pair supplied, both outputs are null,
even for a preferred-only policy; zero is reported only when inputs are present
and common issuance is zero. Preferred conversion and other claims are excluded.

Hand-check fixture used in tests: target $90, fee 10%, MSTR price $10, pre-issue
shares 90, mNAV 2, preferred yield 10%, annual budget $10 and each instrument's
capacity/limit $200. Common-only issues $100 gross / 10 new shares, pays $10 fees,
funds $90, reports $50 NAV claim and 10% new ownership. Preferred-only funds the
same $90 with $10 annual cash expense. The $40 proxy difference is deliberately
not labeled savings because these costs have different economic meanings.

## Measured coverage and limits

Verified 2026-10-22 on Python 3.14.7: 33 tests pass, including nine new comparison
tests. Two separate comparison CLI processes are byte-identical; the original
24-test baseline, default output bytes, fixture hash checks and SVG generation
check pass. No public visual artifact changed. No persistence or network write
path exists; independent processes exercise repeatability without mutable state.

Only the two-week pinned ledger fixture and synthetic scenarios were exercised.
Fractional Decimal allocations retain the existing precision/rounding rules.
Market data authentication, stale-capacity enforcement, liquidity, share lots,
legal issuance constraints, multi-year economics, debt, cash reserves and
principal/conversion valuation remain outside scope. A common price/share pair
is an asserted scenario input, not an independently validated market observation.
See [source review](sources.md#comparison-source-review-2026-10-22).
