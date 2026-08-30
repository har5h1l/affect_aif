# Camera-ready revision audit and provenance packet

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

## Final author decision

The historical manuscript packet is submitted provenance only. The
shared-action/squared-charge run is intermediate correction and robustness
provenance. The shared-action/linear-charge run has been promoted as the sole
canonical camera-ready model under `results/paper/`.

This directory is retained as a revision audit, not a promotion gate. Its
cross-generation comparisons explain why current values and claim boundaries
changed; current claim-bearing evidence lives in `results/paper/` and
`docs/manuscript/source_tables/`.

## Historical comparison artifacts

The comparison is primarily tabular because the section-level effects are more
useful than a large figure deck. Historical comparison figures and calculation
tables remain with the verified linear generation in the server archive; they
are revision provenance, not current paper source tables.
