# NOTE: This sandbox's network policy blocks www.football-data.co.uk, so
# ingestion here goes through a GitHub-hosted mirror (footballcsv/cache.footballdata)
# instead of the original site. Swap BASE_URL/fetch_season back to the direct
# football-data.co.uk CSV (see the commented-out block below) when running
# locally or in CI with unrestricted network access -- that source also
# includes Bet365 odds (B365H/B365D/B365A), which the mirror does not.
import pandas as pd
from db import get_connection

SEASONS = ["2223", "2324", "2425"]

# Original source (requires network access to football-data.co.uk):
# BASE_URL = "https://www.football-data.co.uk/mmz4281/{season}/E0.csv"
#
# def fetch_season(season: str) -> pd.DataFrame:
#     url = BASE_URL.format(season=season)
#     df = pd.read_csv(url)
#     df["season"] = season
#     return df

MIRROR_URL = "https://raw.githubusercontent.com/footballcsv/cache.footballdata/master/{season_dir}/eng.1.csv"
SEASON_DIRS = {"2223": "2022-23", "2324": "2023-24", "2425": "2024-25"}


def fetch_season(season: str) -> pd.DataFrame | None:
    season_dir = SEASON_DIRS[season]
    url = MIRROR_URL.format(season_dir=season_dir)
    try:
        raw = pd.read_csv(url)
    except Exception as exc:
        print(f"  Skipping {season}: {exc}")
        return None

    home_goals, away_goals = raw["FT"].str.split("-", expand=True).astype(int).values.T
    result = pd.Series(
        ["H" if h > a else "A" if a > h else "D" for h, a in zip(home_goals, away_goals)]
    )

    df = pd.DataFrame(
        {
            "Date": raw["Date"],
            "HomeTeam": raw["Team 1"],
            "AwayTeam": raw["Team 2"],
            "FTHG": home_goals,
            "FTAG": away_goals,
            "FTR": result,
            "B365H": None,
            "B365D": None,
            "B365A": None,
        }
    )
    df["season"] = season
    return df

def main():
    con = get_connection()
    for season in SEASONS:
        print(f"Fetching {season}...")
        df = fetch_season(season)
        if df is None:
            continue
        con.execute("INSERT INTO raw_matches SELECT season, Date, HomeTeam, AwayTeam, FTHG, FTAG, FTR, B365H, B365D, B365A FROM df")
    print("Done. Row count:", con.execute("SELECT COUNT(*) FROM raw_matches").fetchone())

if __name__ == "__main__":
    main()
