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

```bash
cd src
python ingest_historical.py
```

This downloads season CSVs for `2223`, `2324`, and `2425`, and loads
them into `raw_matches` in a local DuckDB file (`premier_league.duckdb`
at the repo root). Run `python db.py` to inspect the schema/tables.

`src/api_client.py` is a stub for a future API-Football integration
and isn't wired into the pipeline yet.

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
│   └── api_client.py         # API-Football wrapper (stub for now, not used yet)
└── notebooks/
    └── sanity_check.ipynb    # top scorers, home win %, goals trend
```
