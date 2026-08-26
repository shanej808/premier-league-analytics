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

        NOTE: requires a paid API-Football plan. Confirmed via live calls
        on a Free-plan key that:
        1. The `next` parameter is paid-only (errors: {"plan": "Free plans
           do not have access to the Next parameter."}).
        2. Even without `next`, the Free plan only covers the 2022-2024
           seasons -- the actual current season (see current_pl_season())
           isn't in that range, so this will come back empty regardless.
        Left implemented for when the plan is upgraded; get_season_fixtures
        with an in-range season (e.g. 2024) is the free-plan-compatible
        call for now -- see api_client.py's __main__ block.
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

    # Confirmed live: the current (2026-27) season is outside the Free
    # plan's covered range (2022-2024), so a real, non-empty connectivity
    # proof on this plan means fetching an in-range season instead of the
    # live one. 2024 is the most recent season the Free plan covers.
    print("\nFetching 2024 Premier League fixtures (in-range for the Free plan)...")
    fixtures = client.get_season_fixtures(season=2024)

    print("\n--- summary ---")
    print("league requested:", PREMIER_LEAGUE_ID)
    print("errors:", fixtures.get("errors"))
    print("results:", fixtures.get("results"))

    for f in fixtures.get("response", [])[:5]:
        teams = f["teams"]
        print(f"  {f['fixture']['date']}: {teams['home']['name']} vs {teams['away']['name']}")
