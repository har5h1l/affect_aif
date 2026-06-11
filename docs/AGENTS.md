# AGENTS.md - docs/

`docs/README.md` is the contract for this tree. Read it before reorganizing,
renaming, or updating documentation.

- Keep `docs/active/` as the always-read live state surface.
- Put stable model claims in `docs/overview/`, experiment procedure in
  `docs/experiments/`, interpreted evidence in `docs/results/`, manuscript
  assets in `docs/manuscript/`, and task transfer packets in `docs/handoffs/`.
- Do not duplicate durable state across several docs. Point to the owning doc
  and update the owner.
- Do not update interpreted result prose from new outputs without explicit user
  approval.
- If a docs edit changes how to run, verify, or interpret the project, update
  the matching root or subtree README in the same change.

