# Follow-Up Experiment Plan

## Goal

Strengthen the first-draft manuscript by promoting the weakest supporting
open-regime and social-choice results from five-seed evidence to 30-seed
confirmation evidence, while keeping the current H1/H3 30-seed mechanism and
stress results unchanged.

## Run 1: Manuscript Open/Social Confirmation

Batch name:

```text
manuscript_open_social_confirm_20260525_single_worker
```

Configs:

- `configs/trust/hypotheses/h0_openness/graded_choice_confirm.toml`
- `configs/trust/hypotheses/h2_deployment/lesion_open_regime_confirm.toml`
- `configs/trust/hypotheses/h4_social_choice/partner_choice_confirm.toml`

Expected result roots:

- `results/manuscript_open_social_confirm_20260525_single_worker/h0/graded_choice_confirm/`
- `results/manuscript_open_social_confirm_20260525_single_worker/h2/lesion_open_regime_confirm/`
- `results/manuscript_open_social_confirm_20260525_single_worker/h4/partner_choice_confirm/`

Command:

```bash
.venv/bin/python scripts/experiment/run.py \
  --config configs/trust/hypotheses/h0_openness/graded_choice_confirm.toml \
  --config configs/trust/hypotheses/h2_deployment/lesion_open_regime_confirm.toml \
  --config configs/trust/hypotheses/h4_social_choice/partner_choice_confirm.toml \
  --output-dir results \
  --batch-name manuscript_open_social_confirm_20260525_single_worker \
  --workers 1
```

Post-run analysis:

```bash
.venv/bin/python scripts/analysis/analyze.py --results results/manuscript_open_social_confirm_20260525_single_worker/h0/graded_choice_confirm/results.csv --output-dir results/manuscript_open_social_confirm_20260525_single_worker/h0/graded_choice_confirm/analysis
.venv/bin/python scripts/analysis/analyze.py --results results/manuscript_open_social_confirm_20260525_single_worker/h2/lesion_open_regime_confirm/results.csv --output-dir results/manuscript_open_social_confirm_20260525_single_worker/h2/lesion_open_regime_confirm/analysis
.venv/bin/python scripts/analysis/analyze.py --results results/manuscript_open_social_confirm_20260525_single_worker/h4/partner_choice_confirm/results.csv --output-dir results/manuscript_open_social_confirm_20260525_single_worker/h4/partner_choice_confirm/analysis
```

## Aborted Run Note

`results/manuscript_open_social_confirm_20260525/` contains a partial aborted
parallel run started before the one-worker constraint was clarified. It is
marked with `ABORTED_DO_NOT_USE.md` and should not be interpreted.

## Why This Is The Next Best Run

- H1 and H3 already have 30-seed confirmations.
- H0/H2/H4 currently support the manuscript but still rest on five seeds.
- This run tests the most manuscript-relevant support claims without adding new
  runtime behavior or changing interpretation assumptions.
- It keeps output paths clean and resumable under one manuscript-specific batch.

## Include/Exclude Rules

Include in the manuscript only after review:

- H0 graded-choice payoff, entropy, and movement readouts.
- H2 affect-vs-lesion deployment dissociation.
- H4 partner-choice entropy and selection distribution.

Do not automatically rewrite interpretation docs from these outputs. First
compare them against `docs/paper/manuscript/results_digest.md` and decide
whether they strengthen, weaken, or leave unchanged the current manuscript
claims.

## Next Ablation After This Batch

Global-beta ablation remains the highest-value implementation follow-up because
it directly tests whether partner-specific affect is necessary. It should be a
separate code-and-test task, not mixed into this config-only confirmation run.
