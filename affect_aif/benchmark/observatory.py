"""Read-only client for the Softmax Observatory API."""

from __future__ import annotations

import json
from typing import Callable
from urllib.error import HTTPError
from urllib.request import Request, urlopen


FetchText = Callable[[str, dict[str, str] | None], str]


def _default_fetch_text(url: str, headers: dict[str, str] | None = None) -> str:
    request = Request(url, headers=headers or {})
    try:
        with urlopen(request) as response:
            return response.read().decode("utf-8")
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Observatory request failed for {url}: {exc.code} {body}") from exc


class ObservatoryClient:
    """Small wrapper around public Observatory endpoints."""

    def __init__(
        self,
        base_url: str = "https://api.observatory.softmax-research.net",
        token: str | None = None,
        fetch_text: FetchText | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.fetch_text = fetch_text or _default_fetch_text

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _get_json(self, path: str):
        payload = self.fetch_text(f"{self.base_url}{path}", headers=self._headers())
        return json.loads(payload)

    def list_seasons(self):
        return self._get_json("/tournament/seasons")

    def get_season(self, season_name: str):
        return self._get_json(f"/tournament/seasons/{season_name}")

    def get_leaderboard(self, season_name: str, pool: str | None = None):
        suffix = "" if pool is None else f"?pool={pool}"
        return self._get_json(f"/tournament/seasons/{season_name}/leaderboard{suffix}")

    def get_score_policies_leaderboard(self, season_name: str):
        return self._get_json(f"/tournament/seasons/{season_name}/score-policies-leaderboard")

    def get_pool_config(self, season_name: str, pool_name: str):
        return self._get_json(f"/tournament/seasons/{season_name}/pools/{pool_name}/config")

    def discover_default_season(self, tournament_type: str | None = None):
        seasons = self.list_seasons()
        candidates = [
            season for season in seasons
            if tournament_type is None or season.get("tournament_type") == tournament_type
        ]
        for season in candidates:
            if season.get("is_default"):
                return season
        return candidates[0] if candidates else None

    def validate_season_compat(self, season_name: str, expected: str | None):
        season = self.get_season(season_name)
        actual = season.get("compat_version")
        return {
            "season": season_name,
            "expected": expected,
            "actual": actual,
            "matches": expected is None or actual == expected,
        }
