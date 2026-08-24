# NOTE: www.football-data.co.uk is blocked by this sandbox's network policy,
# so historical results and odds are loaded from local copies of the original
# football-data.co.uk season files instead of fetching them over HTTP. See
# the README for how these were obtained and how to switch back to a live
# fetch once network access allows it.
from pathlib import Path

import pandas as pd
from db import get_connection

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"

SEASON_FILES = {
    "2223": "E0_2022-23.csv",
    "2324": "E0_2023-24.csv",
    "2425": "E0_2024-25.csv",
}

RAW_MATCH_COLUMNS = [
    "Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR",
    "B365H", "B365D", "B365A",
]


def fetch_season(season: str) -> pd.DataFrame:
    path = RAW_DIR / SEASON_FILES[season]
    df = pd.read_csv(path, encoding="utf-8-sig")[RAW_MATCH_COLUMNS].copy()
    df["season"] = season
    return df


def main():
    con = get_connection()
    for season in SEASON_FILES:
        print(f"Loading {season}...")
        df = fetch_season(season)
        con.execute("INSERT INTO raw_matches SELECT season, Date, HomeTeam, AwayTeam, FTHG, FTAG, FTR, B365H, B365D, B365A FROM df")
    print("Done. Row count:", con.execute("SELECT COUNT(*) FROM raw_matches").fetchone())


if __name__ == "__main__":
    main()
