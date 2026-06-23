# Scheduled Public Market Price Updates

> **Purpose**: Maintain daily price snapshots for all public equity and fixed income holdings. Feeds the `defensive-compounding` barbell layer valuations and portfolio mark calculations.

---

## 1. Schedule

| Job | Trigger | Condition |
|---|---|---|
| Daily close fetch | Monday–Friday at 17:30 ET | US market open that day (skip holidays) |
| Weekly portfolio summary | Sunday at 08:00 ET | Always runs |
| Backfill check | Monday at 06:00 ET | Runs after any multi-day gap detected |

### US Market Holiday Calendar Skip Logic

Before running the daily close fetch, check whether the date is a US market holiday:

```python
# scripts/fetch_public_marks.py — holiday check
import pandas_market_calendars as mcal

def is_market_open(date_str: str) -> bool:
    nyse = mcal.get_calendar('NYSE')
    schedule = nyse.schedule(start_date=date_str, end_date=date_str)
    return not schedule.empty

# If False: log "Market closed {date} — skipping" and exit 0
```

Standard US market holidays (NYSE): New Year's Day, MLK Day, Presidents' Day, Good Friday, Memorial Day, Juneteenth, Independence Day, Labor Day, Thanksgiving, Christmas.

---

## 2. Output File Formats

### price_snapshot_{YYYY-MM-DD}.csv

Location: `public-marks/YYYY/MM/price_snapshot_{YYYY-MM-DD}.csv`

```csv
symbol,name,close,volume,source,fetched_at,currency,exchange
VTSAX,Vanguard Total Stock Market Index,118.45,42847291,yfinance,2026-06-23T17:35:12Z,USD,NASDAQ
VTI,Vanguard Total Stock Market ETF,247.32,8921034,yfinance,2026-06-23T17:35:12Z,USD,NYSE
BND,Vanguard Total Bond Market ETF,72.18,5614028,yfinance,2026-06-23T17:35:12Z,USD,NASDAQ
AAPL,Apple Inc.,192.30,51234567,yfinance,2026-06-23T17:35:12Z,USD,NASDAQ
MSFT,Microsoft Corporation,421.50,22341890,yfinance,2026-06-23T17:35:12Z,USD,NASDAQ
```

Rules:
- One row per symbol in the symbol mapping table (see Section 5).
- `close` = adjusted close price (splits/dividends adjusted).
- `volume` = shares traded (use 0 for mutual funds like VTSAX that don't report daily volume).
- `source` = `yfinance` or `alpha_vantage` (fallback).
- `fetched_at` = UTC ISO 8601 timestamp.

### portfolio_marks_{YYYY-MM-DD}.json

Location: `public-marks/YYYY/MM/portfolio_marks_{YYYY-MM-DD}.json`

```json
{
  "as_of_date": "2026-06-23",
  "generated_at": "2026-06-23T17:35:30Z",
  "script_version": "1.3.0",
  "holdings": [
    {
      "deal_slug": "vtsax-index-fund",
      "deal_id": "deal_e5f6a7b8-c9d0-1234-efab-567890123456",
      "symbol": "VTSAX",
      "shares": 1234.567,
      "close_price_usd": 118.45,
      "market_value_usd": 146274.87,
      "cost_basis_total_usd": 117283.87,
      "cost_basis_per_share_usd": 95.00,
      "unrealized_gain_loss_usd": 28991.00,
      "unrealized_gain_loss_pct": 24.72,
      "prior_close_usd": 117.80,
      "daily_change_usd": 0.65,
      "daily_change_pct": 0.55,
      "outlier_flag": false,
      "valuation_ref": "valuations/vtsax-index-fund/valuation_2026-06-23_f1a2b3c4.json"
    },
    {
      "deal_slug": "vti-etf-position",
      "deal_id": "deal_f6a7b8c9-d0e1-2345-fabc-678901234567",
      "symbol": "VTI",
      "shares": 500.0,
      "close_price_usd": 247.32,
      "market_value_usd": 123660.00,
      "cost_basis_total_usd": 110000.00,
      "cost_basis_per_share_usd": 220.00,
      "unrealized_gain_loss_usd": 13660.00,
      "unrealized_gain_loss_pct": 12.42,
      "prior_close_usd": 246.10,
      "daily_change_usd": 1.22,
      "daily_change_pct": 0.50,
      "outlier_flag": false,
      "valuation_ref": "valuations/vti-etf-position/valuation_2026-06-23_a2b3c4d5.json"
    }
  ],
  "portfolio_summary": {
    "total_market_value_usd": 269934.87,
    "total_cost_basis_usd": 227283.87,
    "total_unrealized_gain_loss_usd": 42651.00,
    "total_unrealized_gain_loss_pct": 18.77,
    "holdings_count": 2,
    "outlier_flags": 0,
    "stale_symbols": []
  }
}
```

---

## 3. Pipeline Steps

```
1. CHECK: is_market_open(today)? If no: log and exit.
2. LOAD: Read symbol_mapping.json → list of (symbol, deal_slug, deal_id, shares, cost_basis)
3. FETCH: For each symbol:
   a. Try yfinance: yf.Ticker(symbol).history(period="1d")
   b. If yfinance fails or returns empty: try Alpha Vantage API
   c. If both fail: add to stale_symbols list, log warning
4. VALIDATE: For each fetched price:
   a. Check price > 0
   b. Check daily_change_pct: if abs(daily_change_pct) > 20%: set outlier_flag = true, log alert
   c. Check symbol is in symbol_mapping (reject unknown symbols)
5. WRITE:
   a. Write price_snapshot_{YYYY-MM-DD}.csv
   b. Compute market values, gains/losses → write portfolio_marks_{YYYY-MM-DD}.json
   c. For each holding: write/update valuation record in valuations/{deal_slug}/
6. COMMIT:
   a. git add public-marks/YYYY/MM/
   b. git add valuations/{affected_slugs}/
   c. git commit -m "marks: daily close {YYYY-MM-DD}"
7. CHANGELOG: Append "MARKS: price_snapshot_{YYYY-MM-DD}.csv — {N} symbols, total portfolio ${X}"
8. ALERT (if any): Send Slack to #fo-markets for each outlier_flag or stale_symbol
```

---

## 4. Backfill Plan

### Gap Detection

On each Monday run (06:00 ET), `fetch_public_marks.py --mode backfill` checks for missing dates:

```python
def detect_gaps(year: int, month: int) -> list[str]:
    """Return list of trading dates in YYYY/MM/ that have no price_snapshot file."""
    expected_dates = get_trading_dates(year, month)  # NYSE calendar
    existing_files = glob(f"public-marks/{year}/{month:02d}/price_snapshot_*.csv")
    existing_dates = {parse_date_from_filename(f) for f in existing_files}
    return [d for d in expected_dates if d not in existing_dates]
```

### Backfill Execution

```bash
# Example: backfill missing dates for June 2026
python scripts/fetch_public_marks.py --mode backfill --year 2026 --month 6

# Output commits:
# "backfill: 2026-06-10 price_snapshot (3 symbols)"
# "backfill: 2026-06-11 price_snapshot (3 symbols)"
```

Backfill commits are tagged with `"backfill: "` prefix in CHANGELOG to distinguish from real-time fetches.

Maximum backfill window: 30 calendar days (yfinance reliable up to 5 years; keep it to 30 days for operational purposes).

---

## 5. Symbol Mapping Table

Stored at `public-marks/symbol_mapping.json`. Human-maintained; updated when a new public position is opened.

```json
[
  {
    "symbol": "VTSAX",
    "name": "Vanguard Total Stock Market Index Fund Admiral Shares",
    "deal_slug": "vtsax-index-fund",
    "deal_id": "deal_e5f6a7b8-c9d0-1234-efab-567890123456",
    "shares": 1234.567,
    "cost_basis_per_share_usd": 95.00,
    "lot_date": "2022-01-15",
    "barbell_layer": "defensive-compounding",
    "active": true
  },
  {
    "symbol": "VTI",
    "name": "Vanguard Total Stock Market ETF",
    "deal_slug": "vti-etf-position",
    "deal_id": "deal_f6a7b8c9-d0e1-2345-fabc-678901234567",
    "shares": 500.0,
    "cost_basis_per_share_usd": 220.00,
    "lot_date": "2023-03-20",
    "barbell_layer": "defensive-compounding",
    "active": true
  },
  {
    "symbol": "BND",
    "name": "Vanguard Total Bond Market ETF",
    "deal_slug": "bnd-bond-position",
    "deal_id": "deal_a7b8c9d0-e1f2-3456-abcd-789012345678",
    "shares": 300.0,
    "cost_basis_per_share_usd": 74.50,
    "lot_date": "2023-06-01",
    "barbell_layer": "defensive-compounding",
    "active": true
  }
]
```

---

## 6. Sanity Checks

| Check | Logic | Action on failure |
|---|---|---|
| Stale detection | If most recent snapshot is > 2 trading days old | Slack alert to #fo-markets; trigger backfill |
| Outlier filter | `abs(daily_change_pct) > 20%` | Set `outlier_flag = true`; Slack alert; human confirms before filing |
| Missing symbol | Symbol in mapping_table not in API response | Add to `stale_symbols`; log warning; use prior day's close for portfolio marks |
| Price = 0 or negative | Price from API is 0 or negative | Reject data point; use prior day's close; alert |
| Volume = 0 on ETF/stock | May indicate error on non-holiday | Log warning; flag for review |
| Schema mismatch | portfolio_marks JSON fails jsonschema | Do not commit; alert |

---

## 7. Script Outline: scripts/fetch_public_marks.py

```python
#!/usr/bin/env python3
"""
fetch_public_marks.py — Daily public market price fetcher.

Usage:
  python scripts/fetch_public_marks.py                          # Daily close
  python scripts/fetch_public_marks.py --mode weekly            # Weekly summary
  python scripts/fetch_public_marks.py --mode backfill          # Gap check + fill
  python scripts/fetch_public_marks.py --date 2026-06-10        # Specific date
  python scripts/fetch_public_marks.py --dry-run                # Fetch + validate, no write
"""

import argparse
import json
import csv
import os
import hashlib
from datetime import datetime, date
import yfinance as yf
import pandas_market_calendars as mcal
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SYMBOL_MAPPING_PATH = REPO_ROOT / "public-marks" / "symbol_mapping.json"
SCHEMAS_PATH = REPO_ROOT / "schemas"

def is_market_open(date_str: str) -> bool:
    """Return True if NYSE is open on the given date."""
    nyse = mcal.get_calendar('NYSE')
    schedule = nyse.schedule(start_date=date_str, end_date=date_str)
    return not schedule.empty

def load_symbol_mapping() -> list[dict]:
    """Load and return the symbol mapping table."""
    with open(SYMBOL_MAPPING_PATH) as f:
        return [s for s in json.load(f) if s.get("active", True)]

def fetch_price_yfinance(symbol: str, date_str: str) -> dict | None:
    """Fetch closing price for symbol on date_str. Returns None on failure."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(start=date_str, end=date_str, auto_adjust=True)
        if hist.empty:
            return None
        row = hist.iloc[-1]
        return {
            "close": round(float(row["Close"]), 4),
            "volume": int(row.get("Volume", 0)),
            "source": "yfinance"
        }
    except Exception as e:
        print(f"  yfinance error for {symbol}: {e}")
        return None

def fetch_price_alpha_vantage(symbol: str, api_key: str) -> dict | None:
    """Fallback to Alpha Vantage TIME_SERIES_DAILY endpoint."""
    import requests
    url = (
        f"https://www.alphavantage.co/query"
        f"?function=TIME_SERIES_DAILY_ADJUSTED"
        f"&symbol={symbol}&apikey={api_key}&outputsize=compact"
    )
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        ts = data.get("Time Series (Daily)", {})
        if not ts:
            return None
        latest_date = sorted(ts.keys())[-1]
        row = ts[latest_date]
        return {
            "close": round(float(row["5. adjusted close"]), 4),
            "volume": int(row["6. volume"]),
            "source": "alpha_vantage"
        }
    except Exception as e:
        print(f"  Alpha Vantage error for {symbol}: {e}")
        return None

def check_outlier(symbol: str, close: float, prior_close: float) -> bool:
    """Return True if single-day move exceeds 20%."""
    if prior_close and prior_close > 0:
        pct_change = abs((close - prior_close) / prior_close) * 100
        return pct_change > 20.0
    return False

def write_price_snapshot(date_str: str, rows: list[dict], dry_run: bool = False):
    """Write price_snapshot_{date}.csv to public-marks/YYYY/MM/."""
    year, month, _ = date_str.split("-")
    out_dir = REPO_ROOT / "public-marks" / year / month
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"price_snapshot_{date_str}.csv"
    if not dry_run:
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["symbol","name","close","volume","source","fetched_at","currency","exchange"])
            writer.writeheader()
            writer.writerows(rows)
    print(f"  {'[DRY RUN] Would write' if dry_run else 'Wrote'}: {path}")

def write_portfolio_marks(date_str: str, holdings: list[dict], dry_run: bool = False):
    """Write portfolio_marks_{date}.json to public-marks/YYYY/MM/."""
    year, month, _ = date_str.split("-")
    out_dir = REPO_ROOT / "public-marks" / year / month
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"portfolio_marks_{date_str}.json"
    total_value = sum(h["market_value_usd"] for h in holdings)
    total_cost = sum(h["cost_basis_total_usd"] for h in holdings)
    payload = {
        "as_of_date": date_str,
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "script_version": "1.3.0",
        "holdings": holdings,
        "portfolio_summary": {
            "total_market_value_usd": round(total_value, 2),
            "total_cost_basis_usd": round(total_cost, 2),
            "total_unrealized_gain_loss_usd": round(total_value - total_cost, 2),
            "total_unrealized_gain_loss_pct": round((total_value - total_cost) / total_cost * 100, 2) if total_cost else 0,
            "holdings_count": len(holdings),
            "outlier_flags": sum(1 for h in holdings if h.get("outlier_flag")),
            "stale_symbols": [h["symbol"] for h in holdings if h.get("stale")]
        }
    }
    if not dry_run:
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
    print(f"  {'[DRY RUN] Would write' if dry_run else 'Wrote'}: {path}")

def git_commit(date_str: str, dry_run: bool = False):
    """Stage and commit new mark files."""
    if dry_run:
        print("  [DRY RUN] Would git commit")
        return
    year, month, _ = date_str.split("-")
    os.system(f'git -C "{REPO_ROOT}" add public-marks/{year}/{month}/')
    os.system(f'git -C "{REPO_ROOT}" add valuations/')
    os.system(f'git -C "{REPO_ROOT}" commit -m "marks: daily close {date_str}"')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["daily", "weekly", "backfill"], default="daily")
    parser.add_argument("--date", help="Override date (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    target_date = args.date or date.today().strftime("%Y-%m-%d")

    if args.mode == "daily":
        if not is_market_open(target_date):
            print(f"Market closed {target_date} — skipping.")
            return

        print(f"Fetching prices for {target_date}...")
        symbols = load_symbol_mapping()
        api_key = os.environ.get("ALPHA_VANTAGE_API_KEY", "")

        price_rows = []
        holdings = []

        for s in symbols:
            symbol = s["symbol"]
            result = fetch_price_yfinance(symbol, target_date)
            if not result:
                result = fetch_price_alpha_vantage(symbol, api_key)
            if not result:
                print(f"  WARNING: Could not fetch {symbol} — using stale flag")
                holdings.append({**s, "stale": True, "outlier_flag": False})
                continue

            close = result["close"]
            shares = s["shares"]
            cost_basis_per_share = s["cost_basis_per_share_usd"]
            market_value = round(close * shares, 2)
            cost_basis_total = round(cost_basis_per_share * shares, 2)
            outlier = check_outlier(symbol, close, None)  # prior_close lookup omitted for brevity

            price_rows.append({
                "symbol": symbol,
                "name": s["name"],
                "close": close,
                "volume": result["volume"],
                "source": result["source"],
                "fetched_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "currency": "USD",
                "exchange": "NASDAQ"
            })

            holdings.append({
                "deal_slug": s["deal_slug"],
                "deal_id": s["deal_id"],
                "symbol": symbol,
                "shares": shares,
                "close_price_usd": close,
                "market_value_usd": market_value,
                "cost_basis_total_usd": cost_basis_total,
                "cost_basis_per_share_usd": cost_basis_per_share,
                "unrealized_gain_loss_usd": round(market_value - cost_basis_total, 2),
                "unrealized_gain_loss_pct": round((market_value - cost_basis_total) / cost_basis_total * 100, 2),
                "outlier_flag": outlier,
                "stale": False
            })

        write_price_snapshot(target_date, price_rows, dry_run=args.dry_run)
        write_portfolio_marks(target_date, holdings, dry_run=args.dry_run)
        git_commit(target_date, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
```

---

## 8. Cron / GitHub Actions Schedule

```yaml
# .github/workflows/daily-marks.yml
name: Daily Price Marks
on:
  schedule:
    - cron: '30 22 * * 1-5'   # 17:30 ET = 22:30 UTC (Mon-Fri)
    - cron: '0 13 * * 0'      # 08:00 ET Sunday = 13:00 UTC
  workflow_dispatch:            # Allow manual trigger

jobs:
  fetch-marks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.CI_BOT_PAT }}
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install yfinance pandas-market-calendars requests
      - run: python scripts/fetch_public_marks.py --mode daily
        env:
          ALPHA_VANTAGE_API_KEY: ${{ secrets.ALPHA_VANTAGE_API_KEY }}
      - name: Configure git
        run: |
          git config user.name "ci-bot"
          git config user.email "ci-bot@familyoffice.local"
      - run: python scripts/fetch_public_marks.py --mode daily
```
