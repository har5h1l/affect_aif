"""Statistical helpers for configured analyses."""

from __future__ import annotations

import pandas as pd

from analysis.statistics import cumulative_payoff_anova, pairwise_payoff_tests


def payoff_anova(results: pd.DataFrame) -> dict:
    return cumulative_payoff_anova(results)


def pairwise_payoffs(results: pd.DataFrame) -> pd.DataFrame:
    return pairwise_payoff_tests(results)
