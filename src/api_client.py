"""Thin wrapper around the API-Football (api-sports.io) v3 REST API.

Used for live/current-season data (fixtures, standings, etc.) --
historical results and odds still come from football-data.co.uk via
ingest_historical.py. Nothing here is wired into the DuckDB pipeline
yet; this just proves out connectivity and basic response handling.
"""

import json
import os
from datetime import date

import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = "https://v3.football.api-sports.io"
PREMIER_LEAGUE_ID = 39


class APIFootballClient:
    def __init__(self, api_key: str | None = None, base_url: str = API_BASE_URL):
        self.api_key = api_key or os.environ.get("API_FOOTBALL_KEY")
        if not self.api_key:
            raise ValueError("API_FOOTBALL_KEY not set (check .env)")
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"x-apisports-key": self.api_key})

    def _get(self, path: str, **params) -> dict:
        resp = self.session.get(f"{self.base_url}{path}", params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_status(self) -> dict:
        """Cheap call to confirm the key is valid and check quota usage."""
        return self._get("/status")

    def get_fixtures(self, league: int = PREMIER_LEAGUE_ID, **params) -> dict:
        return self._get("/fixtures", league=league, **params)

    def get_season_fixtures(self, season: int | None = None, **params) -> dict:
        """All fixtures for a given Premier League season (defaults to the
        current one). Use this when you actually need a season's full
        schedule/results."""
        return self.get_fixtures(season=season or current_pl_season(), **params)

    def get_current_pl_fixtures(self, next_n: int = 10) -> dict:
        """Next N upcoming Premier League fixtures.

        Confirmed via a live call that the `next` parameter is a paid-only
        feature -- the free plan's /fixtures response for `next=5` came back
        with errors: {"plan": "Free plans do not have access to the Next
        parameter."}. So instead of `next`, this fetches the current
        season's not-yet-started fixtures (status=NS) and returns the
        earliest N by kickoff date, which works on the free plan.
        """
        data = self.get_season_fixtures(status="NS")
        upcoming = sorted(data.get("response", []), key=lambda f: f["fixture"]["date"])
        data["response"] = upcoming[:next_n]
        data["results"] = len(data["response"])
        return data


def current_pl_season() -> int:
    """API-Football labels a season by its start year (e.g. 2025 for 2025-26).
    The PL season starts in August, so treat Jan-Jul as still last year's season.
    """
    today = date.today()
    return today.year if today.month >= 8 else today.year - 1


if __name__ == "__main__":
    client = APIFootballClient()

    print("Checking API-Football connectivity...")
    status = client.get_status()
    print("GET /status -> full raw response:")
    print(json.dumps(status, indent=2))

    print("\nFetching current Premier League fixtures (status=NS, free-plan compatible)...")
    fixtures = client.get_current_pl_fixtures(next_n=5)

    print("\n--- summary ---")
    print("league requested:", PREMIER_LEAGUE_ID)
    print("errors:", fixtures.get("errors"))
    print("results:", fixtures.get("results"))

    for f in fixtures.get("response", []):
        teams = f["teams"]
        print(f"  {f['fixture']['date']}: {teams['home']['name']} vs {teams['away']['name']}")
