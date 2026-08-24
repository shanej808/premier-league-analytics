"""Stub wrapper for the API-Football service.

Not wired up yet -- historical data currently comes from
football-data.co.uk via ingest_historical.py. This module will grow
into a thin client for live fixtures/stats once that integration is
scheduled.
"""

import os

import requests

API_BASE_URL = "https://v3.football.api-sports.io"


class APIFootballClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("API_FOOTBALL_KEY")
        self.session = requests.Session()

    def _headers(self) -> dict:
        return {"x-apisports-key": self.api_key or ""}

    def get_fixtures(self, **params):
        raise NotImplementedError("API-Football integration not implemented yet")
