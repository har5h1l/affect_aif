"""Structured progress reporting for experiment runs."""

from __future__ import annotations

from dataclasses import dataclass


def _fmt_float(value: object) -> str:
    if value is None:
        return "n/a"
    try:
        return f"{float(value):0.3f}"
    except (TypeError, ValueError):
        return str(value)


def _fmt_int(value: object) -> str:
    if value is None:
        return "n/a"
    try:
        return str(int(value))
    except (TypeError, ValueError):
        return str(value)


@dataclass
class ProgressReporter:
    """Base no-op reporter."""

    enabled: bool = False

    def emit(self, event: str, **payload):
        del event, payload


class StageStreamProgressReporter(ProgressReporter):
    """Compact deterministic line-oriented progress stream."""

    enabled: bool = True

    def emit(self, event: str, **payload):
        if not self.enabled:
            return
        line = self._format_event(event, payload)
        if line:
            print(line, flush=True)

    def _format_event(self, event: str, payload: dict) -> str:
        condition = payload.get("condition")
        replication = payload.get("replication")
        round_idx = payload.get("round_idx")
        round_count = payload.get("round_count")
        prefix = f"[cond={_fmt_int(condition)} rep={_fmt_int(replication)}]"
        if round_idx is not None:
            prefix += f" [round={int(round_idx) + 1}/{_fmt_int(round_count)}]"
        if event == "calibration_episode_start":
            return (
                f"[calibration] [episode={int(payload['episode_idx']) + 1}/{_fmt_int(payload.get('episode_count'))}]"
                f" seed={_fmt_int(payload.get('seed'))} start"
            )
        if event == "calibration_episode_end":
            return (
                f"[calibration] [episode={int(payload['episode_idx']) + 1}/{_fmt_int(payload.get('episode_count'))}]"
                " seed="
                f"{_fmt_int(payload.get('seed'))} end "
                "mean_abs_step_efe="
                f"{_fmt_float(payload.get('mean_abs_step_efe'))}"
            )
        if event == "condition_start":
            return f"{prefix} start name={payload.get('condition_name', 'unknown')}"
        if event == "condition_end":
            return f"{prefix} end rows={_fmt_int(payload.get('rows'))}"
        if event == "replication_start":
            return f"{prefix} start seed={_fmt_int(payload.get('seed'))}"
        if event == "replication_end":
            return (
                f"{prefix} end seed={_fmt_int(payload.get('seed'))}"
                f" cumulative_payoff={_fmt_float(payload.get('cumulative_payoff'))}"
            )
        if event == "round_start":
            return f"{prefix} stage=round_start active_partner={_fmt_int(payload.get('active_partner'))}"
        if event == "planning_start":
            return f"{prefix} stage=planning_start active_partner={_fmt_int(payload.get('active_partner'))}"
        if event == "planning_end":
            return (
                f"{prefix} stage=planning_end selected_partner={_fmt_int(payload.get('selected_partner'))}"
                f" action={_fmt_int(payload.get('selected_action'))}"
                f" raw_action={_fmt_int(payload.get('raw_action'))}"
                f" best_policy={_fmt_int(payload.get('best_policy_idx'))}"
            )
        if event == "environment_step_start":
            return f"{prefix} stage=env_step_start raw_action={_fmt_int(payload.get('raw_action'))}"
        if event == "environment_step_end":
            switch_flag = payload.get("switch_kind", "none")
            return (
                f"{prefix} stage=env_step_end partner={_fmt_int(payload.get('partner_idx'))}"
                f" agent_action={_fmt_int(payload.get('agent_action'))}"
                f" partner_action={_fmt_int(payload.get('partner_action'))}"
                f" payoff={_fmt_float(payload.get('payoff'))}"
                f" switch={switch_flag}"
            )
        if event == "belief_update_start":
            return f"{prefix} stage=belief_update_start partner={_fmt_int(payload.get('partner_idx'))}"
        if event == "belief_update_end":
            return (
                f"{prefix} stage=belief_update_end partner={_fmt_int(payload.get('partner_idx'))}"
                f" inferred={payload.get('inferred_type', 'n/a')}"
                f" correct={payload.get('inferred_type_correct', 'n/a')}"
            )
        if event == "metric_logging_end":
            return (
                f"{prefix} stage=logging_end payoff={_fmt_float(payload.get('payoff'))}"
                f" inferred={payload.get('inferred_type', 'n/a')}"
                f" q_pi_entropy={_fmt_float(payload.get('q_pi_entropy'))}"
            )
        if event == "gif_generation_start":
            return f"[gifs] start output_dir={payload.get('output_dir')}"
        if event == "gif_generation_end":
            return f"[gifs] end count={_fmt_int(payload.get('gif_count'))} output_dir={payload.get('output_dir')}"
        return ""


def create_progress_reporter(enabled: bool, mode: str) -> ProgressReporter:
    """Build a configured reporter."""

    if not enabled:
        return ProgressReporter(enabled=False)
    if mode != "stage_stream":
        raise ValueError(f"Unsupported verbosity mode '{mode}'.")
    return StageStreamProgressReporter(enabled=True)
