# premier-league-analytics

A predictive EPL goals model.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Data pipeline

Historical match results and odds come from
[football-data.co.uk](https://www.football-data.co.uk/englandm.php)
(English Premier League, `E0`).

`www.football-data.co.uk` is not reachable from this project's default
dev sandbox (blocked by network policy), so instead of fetching over
HTTP at runtime, the three current season files were downloaded
manually and committed as a one-off drop:

- `data/raw/E0_2022-23.csv`
- `data/raw/E0_2023-24.csv`
- `data/raw/E0_2024-25.csv`

`data/raw/` is gitignored by default (for any future ad hoc downloads),
with an explicit exception carved out for these `E0_*.csv` files so
they stay checked in. If you have unrestricted network access, you can
instead re-fetch a season directly with:

```python
import pandas as pd
pd.read_csv("https://www.football-data.co.uk/mmz4281/2425/E0.csv").to_csv("data/raw/E0_2024-25.csv", index=False)
```

```bash
cd src
python ingest_historical.py
```

This loads `raw_matches` from the local season CSVs (`2223`, `2324`,
`2425`) into a local DuckDB file (`premier_league.duckdb` at the repo
root), including Bet365 (`B365H/D/A`) odds. Run `python db.py` to
inspect the schema/tables. `schema.sql`'s `odds` table additionally
captures Pinnacle (`psh/psd/psa`) and market-average (`avgh/avgd/avga`)
odds, which are present in all three season files, for future use once
match/team normalization is wired up.

## Live data (API-Football)

`src/api_client.py` wraps the [API-Football](https://www.api-football.com/)
v3 REST API for live/current-season data (fixtures, standings, etc.).
It's not wired into the DuckDB pipeline yet -- historical results and
odds still come from the CSVs above.

**Live current-season fixtures require a paid API-Football plan.**
Confirmed against a real Free-plan key:
- The `next` parameter (used to fetch "next N upcoming fixtures") is
  paid-only -- the API returns `errors: {"plan": "Free plans do not
  have access to the Next parameter."}`.
- Even without `next`, the Free plan only covers the **2022-2024**
  seasons. The actual current season is out of range, so any query for
  it comes back empty regardless of which parameters are used.

`client.get_season_fixtures(season=2024)` (or 2022/2023) is the
Free-plan-compatible call and is what `api_client.py`'s `__main__`
block demonstrates -- run `python src/api_client.py` (with
`API_FOOTBALL_KEY` set in `.env`) to see it return real fixture data
end-to-end. `get_current_pl_fixtures` is implemented and correct but
will return nothing until the plan is upgraded.

## Notebooks

`notebooks/sanity_check.ipynb` runs a few quick sanity queries against
`raw_matches`: top scorers, home win %, and a goals-per-season trend.

## Project layout

```
premier-league-analytics/
├── README.md
├── requirements.txt
├── .env.example
├── data/
│   └── raw/                  # downloaded CSVs land here (gitignored)
├── src/
│   ├── db.py                 # DuckDB connection + schema setup
│   ├── schema.sql            # table definitions
│   ├── ingest_historical.py  # football-data.co.uk CSV loader
│   └── api_client.py         # API-Football wrapper (Free plan: 2022-2024 seasons only)
└── notebooks/
    └── sanity_check.ipynb    # top scorers, home win %, goals trend
```
