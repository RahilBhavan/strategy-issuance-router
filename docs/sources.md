# Sources and coverage

Purpose: identify observed data separately from scenario inputs. As-of review: 2026-10-21.

The adjacent `../strategy-8k-ledger` contains 97 weekly observations from 93 weekly-update filings (147 candidate 8-K/8-K/A filings), plus 432 program/action rows, through the filing of October 19, 2026. This tool reads its `weekly.csv` and `instrument_weekly.csv`; source URL, as-of date, filing date and program accompany every capacity and actual comparison. The ledger's manifest and `hydrate` command verify original-byte SHA-256 hashes. This router does not independently fetch or prove corpus completeness.

Primary websites manually reopened on October 21:

- [SEC October 19 8-K](https://www.sec.gov/Archives/edgar/data/1050446/000119312526424688/mstr-20261019.htm): actual period issuance and holdings. This is deliberately unavailable to the demo's October 9 recommendation.
- [Strategy proposal timeline and FAQ](https://www.strategy.com/it/mstr/vote): October 28 vote and conditional new dividend cadence.
- [SEC October 16 filing](https://www.sec.gov/Archives/edgar/data/1050446/000119312526423400/mstr-20261015.htm): November daily STRC dividends are contingent, not evidence of enactment by October 21.

Follow the capacity source URLs printed in `examples/result.json` for the predecision filings. Those records are tested from real cached SEC HTML by the ledger; every historical source has not been separately manually read in a browser. Market prices, yields, fees, limits, budget and mNAV in the demo are **synthetic assumptions** with no market-data source. No forward rate, execution price or treasury objective is inferred from the filings.
