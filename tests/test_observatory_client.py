"""Tests for read-only Observatory client behavior."""

from pathlib import Path

from benchmark.observatory import ObservatoryClient


def _fixture(name: str):
    base = Path(__file__).parent / "fixtures" / "observatory"
    return (base / name).read_text()


def test_client_reads_season_detail_from_injected_fetcher():
    payloads = {
        "/tournament/seasons/beta-cvc": _fixture("season_beta_cvc.json"),
    }

    client = ObservatoryClient(
        base_url="https://example.test",
        fetch_text=lambda url, headers=None: payloads[url.replace("https://example.test", "")],
    )

    season = client.get_season("beta-cvc")
    assert season["name"] == "beta-cvc"
    assert season["compat_version"] == "0.19"


def test_client_reads_score_leaderboard_from_injected_fetcher():
    payloads = {
        "/tournament/seasons/beta-teams-tiny-fixed/score-policies-leaderboard": _fixture(
            "score_policies_beta_teams_tiny_fixed.json"
        ),
    }

    client = ObservatoryClient(
        base_url="https://example.test",
        fetch_text=lambda url, headers=None: payloads[url.replace("https://example.test", "")],
    )

    leaderboard = client.get_score_policies_leaderboard("beta-teams-tiny-fixed")
    assert leaderboard[0]["policy"]["name"] == "dinky"


def test_client_validates_expected_compat_version():
    payloads = {
        "/tournament/seasons/beta-cvc": _fixture("season_beta_cvc.json"),
    }

    client = ObservatoryClient(
        base_url="https://example.test",
        fetch_text=lambda url, headers=None: payloads[url.replace("https://example.test", "")],
    )

    assert client.validate_season_compat("beta-cvc", expected="0.19")["matches"] is True
