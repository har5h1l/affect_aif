"""Animated visualizations for experiment runs."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

LIST_LIKE_COLUMNS = (
    "true_types",
    "true_stances",
    "betas",
    "prediction_errors",
    "reward_avgs",
    "G",
    "q_pi",
    "best_policy_step_costs",
    "scheduled_switch_partner_ids",
    "partner_beliefs",
    "partner_posteriors",
    "partner_joint_beliefs",
    "partner_joint_posteriors",
    "partner_stance_beliefs",
)


def _parse_maybe_literal(value):
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return value
        normalized = text.replace("nan", "None")
        try:
            parsed = ast.literal_eval(normalized)
            return _restore_nans(parsed)
        except (ValueError, SyntaxError):
            return value
    return value


def _restore_nans(value):
    if isinstance(value, list):
        return [_restore_nans(item) for item in value]
    if value is None:
        return np.nan
    return value


def _normalize_results(results: pd.DataFrame) -> pd.DataFrame:
    normalized = results.copy()
    for column in LIST_LIKE_COLUMNS:
        if column in normalized.columns:
            normalized[column] = normalized[column].apply(_parse_maybe_literal)
    return normalized


def load_results(path: str) -> pd.DataFrame:
    source = Path(path)
    if source.suffix == ".parquet":
        return _normalize_results(pd.read_parquet(source))
    return _normalize_results(pd.read_csv(source))


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug or "run"


def _condition_slug(value) -> str:
    if isinstance(value, (int, np.integer)):
        return f"{int(value):02d}"
    text = _slugify(str(value))
    return text or "condition"


def _condition_sort_key(value) -> tuple[int, str]:
    if isinstance(value, (int, np.integer)):
        return (0, f"{int(value):04d}")
    return (1, str(value))


def _signal_label(run: pd.DataFrame) -> str:
    reward_values = run["reward_avgs"].dropna() if "reward_avgs" in run.columns else pd.Series(dtype=object)
    if any(np.any(np.isfinite(np.asarray(item, dtype=float))) for item in reward_values):
        return "Reward Avg"
    beta_values = run["betas"].dropna() if "betas" in run.columns else pd.Series(dtype=object)
    if any(np.any(np.isfinite(np.asarray(item, dtype=float))) for item in beta_values):
        return "Beta"
    return "Signal"


def _signal_values(row: pd.Series) -> np.ndarray | None:
    for column in ("reward_avgs", "betas"):
        values = row.get(column)
        if values is None:
            continue
        arr = np.asarray(values, dtype=float)
        if arr.size and np.any(np.isfinite(arr)):
            return arr
    return None


def _make_frame(run: pd.DataFrame, frame_idx: int) -> Image.Image:
    row = run.iloc[frame_idx]
    rounds = run["round"].to_numpy(dtype=int) + 1
    cumulative_payoff = run["payoff"].to_numpy(dtype=float).cumsum()
    signal_label = _signal_label(run)
    signal = _signal_values(row)
    true_types = list(row["true_types"])
    true_stances = list(row.get("true_stances", []))

    fig = plt.figure(figsize=(12, 7))
    grid = fig.add_gridspec(2, 2, width_ratios=(1.2, 1.0), height_ratios=(1.0, 1.0))
    ax_summary = fig.add_subplot(grid[0, 0])
    ax_payoff = fig.add_subplot(grid[1, 0])
    ax_signal = fig.add_subplot(grid[:, 1])

    fig.suptitle(
        f"{row['condition_name']} | seed {int(row['seed'])} | round {int(row['round']) + 1}/{len(run)}",
        fontsize=16,
        fontweight="bold",
    )

    current_partner = int(row["partner_idx"])
    active_partner = int(row["active_partner"])
    selected_partner = int(row["selected_partner"])
    summary_lines = [
        f"Active partner at start: P{active_partner}"
        if active_partner >= 0
        else "Active partner at start: agent choice",
        f"Selected partner/action: P{selected_partner} / {int(row['selected_action'])}",
        f"Observed current partner: P{current_partner}",
        f"True type/stance: {row['true_partner_type']} / {row.get('true_partner_stance', 'unknown')}",
        f"Inferred type/stance: {row['inferred_type']} / {row.get('inferred_stance', 'unknown')}",
        f"Actions (agent/partner): {int(row['agent_action'])} / {int(row['partner_action'])}",
        f"Payoff: {float(row['payoff']):0.2f}",
        f"Switch: {row['switch_kind']}",
        f"Policy entropy: {float(row['q_pi_entropy']):0.3f}",
    ]
    ax_summary.axis("off")
    ax_summary.text(0.0, 0.98, "\n".join(summary_lines), va="top", ha="left", fontsize=11, family="monospace")
    partner_roster = "\n".join(
        (
            f"P{idx}: {partner_type}"
            f"{'/' + true_stances[idx] if idx < len(true_stances) else ''}"
            f"{' <=' if idx == current_partner else ''}"
        )
        for idx, partner_type in enumerate(true_types)
    )
    ax_summary.text(0.62, 0.98, partner_roster, va="top", ha="left", fontsize=11, family="monospace")

    ax_payoff.plot(rounds[: frame_idx + 1], cumulative_payoff[: frame_idx + 1], color="#1f77b4", linewidth=2)
    ax_payoff.scatter([rounds[frame_idx]], [cumulative_payoff[frame_idx]], color="#d62728", zorder=3)
    switch_mask = (
        run.get("type_switched", pd.Series(False, index=run.index)).fillna(False).astype(bool)
        | run.get("stance_switched", pd.Series(False, index=run.index)).fillna(False).astype(bool)
    )
    switch_rounds = run.loc[switch_mask, "round"].to_numpy(dtype=int) + 1
    for switch_round in switch_rounds:
        ax_payoff.axvline(switch_round, color="#ff7f0e", linestyle="--", linewidth=1, alpha=0.6)
    ax_payoff.set_title("Cumulative Payoff")
    ax_payoff.set_xlabel("Round")
    ax_payoff.set_ylabel("Cumulative payoff")
    ax_payoff.set_xlim(1, max(1, len(run)))
    y_min = min(0.0, float(np.min(cumulative_payoff[: frame_idx + 1])) - 1.0)
    y_max = max(1.0, float(np.max(cumulative_payoff[: frame_idx + 1])) + 1.0)
    ax_payoff.set_ylim(y_min, y_max)

    ax_signal.set_title(f"{signal_label} by Partner")
    ax_signal.set_xlabel("Partner")
    ax_signal.set_ylabel(signal_label)
    positions = np.arange(len(true_types))
    if signal is None:
        ax_signal.axis("off")
        ax_signal.text(0.5, 0.5, "No partner signal for this condition", ha="center", va="center", fontsize=13)
    else:
        colors = ["#d62728" if idx == current_partner else "#4c78a8" for idx in positions]
        ax_signal.bar(positions, signal, color=colors, alpha=0.9)
        ax_signal.set_xticks(positions, [f"P{idx}" for idx in positions])
        finite_signal = signal[np.isfinite(signal)]
        upper = max(1.0, float(np.max(finite_signal)) + 0.1) if finite_signal.size else 1.0
        lower = min(0.0, float(np.min(finite_signal)) - 0.1) if finite_signal.size else 0.0
        ax_signal.set_ylim(lower, upper)
        for idx, value in enumerate(signal):
            ax_signal.text(idx, value + 0.03, f"{value:0.2f}", ha="center", va="bottom", fontsize=10)

    fig.tight_layout()
    fig.canvas.draw()
    rgba = np.asarray(fig.canvas.buffer_rgba())
    image = Image.fromarray(rgba[..., :3])
    plt.close(fig)
    return image


def build_run_gifs(
    results: pd.DataFrame,
    output_dir: str,
    frame_duration_ms: int = 350,
    reporter=None,
) -> list[Path]:
    """Create one GIF per primary condition/seed run."""

    normalized = _normalize_results(results)
    if "run_mode" in normalized.columns:
        primary = normalized[normalized["run_mode"] == "primary"].copy()
    else:
        primary = normalized.copy()
    if primary.empty:
        return []

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    if reporter is not None:
        reporter.emit("gif_generation_start", output_dir=str(output))

    written: list[Path] = []
    primary["_condition_sort"] = primary["condition"].apply(_condition_sort_key)
    grouped = (
        primary.sort_values(["_condition_sort", "seed", "round"])
        .drop(columns="_condition_sort")
        .groupby(["condition", "seed"], sort=True)
    )
    for (condition, seed), run in grouped:
        frames = [_make_frame(run.reset_index(drop=True), idx) for idx in range(len(run))]
        condition_name = str(run["condition_name"].iloc[0])
        target = output / f"{_condition_slug(condition)}_{_slugify(condition_name)}_seed_{int(seed)}.gif"
        first, *rest = frames
        first.save(
            target,
            save_all=True,
            append_images=rest,
            duration=int(frame_duration_ms),
            loop=0,
        )
        written.append(target)

    if reporter is not None:
        reporter.emit("gif_generation_end", gif_count=len(written), output_dir=str(output))
    return written
