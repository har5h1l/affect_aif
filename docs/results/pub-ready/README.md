# Pub-ready results review packet

This packet lets a reviewer compare the current manuscript result packet with
the two completed reruns without hunting through raw CSVs.

## Read this first

1. [Run layout](run-layout.md) explains what changed between the three
   packets and where every raw table lives.
2. [Section comparison](section-comparison.md) maps the results to manuscript
   Sections 3.1--3.5, with the values and claim boundaries that matter for
   review.
3. [Claim and ablation ledger](claim-and-ablation-ledger.md) is the complete
   decision surface: each manuscript claim, its exact contrast, current
   status, and permitted wording.

## Review boundary

`results/paper/` remains the historical manuscript packet. The shared-action
correction is behavior-changing, so it is not a numerical reproduction of that
packet. The linear-charge run is a matched follow-up sensitivity analysis, not
an independently promoted manuscript result.

No manuscript prose, source tables, or canonical result cards have been
replaced by this review packet. It exists to support an informed decision about
what should be revised and what should remain a follow-up analysis.

## Compact figures

The comparison is primarily tabular because the section-level effects are more
useful than a large figure deck. Two locally generated figures are retained at
the linear-run analysis root for review:

- [Core effects across the three packets](../../../results/rebaseline_shared_action_policy_fix_6b7d889_local/linear_charge_20260812/analysis/three_way_comparison_20260813/fig_01_core_effects.png)
- [Partner-allocation shifts](../../../results/rebaseline_shared_action_policy_fix_6b7d889_local/linear_charge_20260812/analysis/three_way_comparison_20260813/fig_02_partner_allocation.png)

The underlying calculation tables and paired/independent bootstrap summaries
are in the same analysis directory. They are local review artifacts, not paper
figures.
